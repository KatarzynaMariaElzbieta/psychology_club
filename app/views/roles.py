import json
import os
import uuid
from zoneinfo import ZoneInfo

from datetime import datetime
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_security import SQLAlchemyUserDatastore, hash_password, roles_accepted
from werkzeug.utils import secure_filename

from app import models
from app.extensions import db
from app.mailing_import import parse_recipient_file
from email_validator import EmailNotValidError, validate_email
from app.mailing_jobs import enqueue_mailing_batch

roles_bp = Blueprint("roles", __name__, url_prefix="/admin")

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)


# --- Lista ról ---
@roles_bp.route("/menu")
@roles_accepted("admin")
def list_roles():
    roles = models.Role.query.all()
    return render_template("roles/menu.html", roles=roles)


# --- Dodawanie nowej roli ---
@roles_bp.route("/create", methods=["GET", "POST"])
@roles_accepted("admin")
def create_role():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")

        if not name:
            flash("Nazwa roli jest wymagana", "danger")
            return redirect(url_for("roles.create_role"))

        if user_datastore.find_role(name):
            flash("Taka rola już istnieje", "warning")
            return redirect(url_for("roles.create_role"))

        user_datastore.create_role(name=name, description=description)
        db.session.commit()

        flash("Rola została utworzona", "success")
        return redirect(url_for("roles.list_roles"))

    return render_template("roles/create.html")


# --- Przypisywanie użytkowników do roli ---
@roles_bp.route("/<role_name>/assign", methods=["GET", "POST"])
@roles_accepted("admin")
def assign_role(role_name):
    role = user_datastore.find_role(role_name)
    if not role:
        flash("Rola nie istnieje", "danger")
        return redirect(url_for("roles.list_roles"))

    users = models.User.query.all()

    if request.method == "POST":
        selected = request.form.getlist("users")

        # Czyścimy role
        for user in users:
            if role in user.roles:
                user.roles.remove(role)

        # Dodajemy nowe przypisania
        for uid in selected:
            user = user_datastore.find_user(id=int(uid))
            if user:
                user_datastore.add_role_to_user(user, role)

        db.session.commit()

        flash("Zaktualizowano przypisania użytkowników", "success")
        return redirect(url_for("roles.list_roles"))

    return render_template("roles/assign.html", role=role, users=users)


# --- Lista użytkowników ---
@roles_bp.route("/users")
@roles_accepted("admin")
def list_users():
    users = models.User.query.order_by(models.User.email.asc()).all()
    return render_template("roles/users.html", users=users)


# --- Dodawanie użytkownika ---
@roles_bp.route("/users/create", methods=["GET", "POST"])
@roles_accepted("admin")
def create_user():
    all_roles = models.Role.query.order_by(models.Role.name.asc()).all()

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        username = (request.form.get("username") or "").strip() or None
        phone = (request.form.get("phone") or "").strip() or None
        is_active = request.form.get("active") == "on"
        selected_role_ids = {int(role_id) for role_id in request.form.getlist("roles")}

        if not email:
            flash("Adres e-mail jest wymagany", "danger")
            return render_template("roles/create_user.html", all_roles=all_roles)

        if len(password) < 8:
            flash("Hasło musi mieć co najmniej 8 znaków", "danger")
            return render_template("roles/create_user.html", all_roles=all_roles)

        if user_datastore.find_user(email=email):
            flash("Użytkownik z takim adresem e-mail już istnieje", "warning")
            return render_template("roles/create_user.html", all_roles=all_roles)

        user = user_datastore.create_user(
            email=email,
            password=hash_password(password),
            username=username,
            phone=phone,
            active=is_active,
        )

        for role in all_roles:
            if role.id in selected_role_ids:
                user_datastore.add_role_to_user(user, role)

        db.session.commit()
        flash("Użytkownik został dodany", "success")
        return redirect(url_for("roles.list_users"))

    return render_template("roles/create_user.html", all_roles=all_roles)


# --- Edycja użytkownika (role + aktywność) ---
@roles_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_accepted("admin")
def edit_user(user_id):
    user = user_datastore.find_user(id=user_id)
    if not user:
        flash("Użytkownik nie istnieje", "danger")
        return redirect(url_for("roles.list_users"))

    all_roles = models.Role.query.order_by(models.Role.name.asc()).all()

    if request.method == "POST":
        selected_role_ids = {int(role_id) for role_id in request.form.getlist("roles")}
        user.active = request.form.get("active") == "on"

        # Usuwamy role, których nie zaznaczono.
        for role in list(user.roles):
            if role.id not in selected_role_ids:
                user.roles.remove(role)

        # Dodajemy nowo zaznaczone role.
        current_role_ids = {role.id for role in user.roles}
        for role in all_roles:
            if role.id in selected_role_ids and role.id not in current_role_ids:
                user_datastore.add_role_to_user(user, role)

        db.session.commit()
        flash("Dane użytkownika zostały zaktualizowane", "success")
        return redirect(url_for("roles.edit_user", user_id=user.id))

    return render_template("roles/edit_user.html", user=user, all_roles=all_roles)


@roles_bp.route("/downloads", methods=["GET", "POST"])
@roles_accepted("admin")
def downloads():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        uploaded_file = request.files.get("file")

        if not title:
            flash("Tytuł pliku jest wymagany.", "danger")
            return redirect(url_for("roles.downloads"))

        if not uploaded_file or not uploaded_file.filename:
            flash("Wybierz plik do dodania.", "danger")
            return redirect(url_for("roles.downloads"))

        original_name = secure_filename(uploaded_file.filename)
        if not original_name:
            flash("Nieprawidłowa nazwa pliku.", "danger")
            return redirect(url_for("roles.downloads"))

        _, ext = os.path.splitext(original_name)
        stored_name = f"{uuid.uuid4().hex}{ext.lower()}"

        upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "downloads")
        os.makedirs(upload_dir, exist_ok=True)
        uploaded_file.save(os.path.join(upload_dir, stored_name))

        db.session.add(
            models.DownloadFile(
                title=title,
                description=description,
                stored_name=stored_name,
                original_name=original_name,
            )
        )
        db.session.commit()
        flash("Plik został dodany do sekcji 'Do pobrania'.", "success")
        return redirect(url_for("roles.downloads"))

    files = models.DownloadFile.query.order_by(models.DownloadFile.created_at.desc()).all()
    return render_template("roles/downloads.html", files=files)


@roles_bp.route("/mailing", methods=["GET", "POST"])
@roles_accepted("admin")
def mailing():
    warsaw_tz = ZoneInfo("Europe/Warsaw")
    if request.method == "POST" and request.form.get("action") == "retry":
        batch_id = request.form.get("batch_id")
        if batch_id:
            batch = models.MailingBatch.query.get(int(batch_id))
            if batch:
                enqueue_mailing_batch(batch.id)
                flash("Wysyłka została ponownie zaplanowana.", "success")
        return redirect(url_for("roles.mailing"))

    if request.method == "POST":
        template_type_id = request.form.get("template_type_id")
        template_type = None
        template_id = ""
        if template_type_id:
            template_type = models.MailingTemplateType.query.get(int(template_type_id))
            if template_type:
                template_id = template_type.template_id

        template_id = (template_id or request.form.get("template_id") or "").strip()
        visible_to_email = (request.form.get("visible_to_email") or "").strip()
        visible_to_name = (request.form.get("visible_to_name") or "").strip() or None
        template_data = {}
        for key, value in request.form.items():
            if key.startswith("tpl_"):
                cleaned = (value or "").strip()
                if cleaned:
                    template_data[key[4:]] = cleaned
        send_at_raw = (request.form.get("send_at") or "").strip()
        auto_delete = request.form.get("auto_delete") == "on"
        upload_file = request.files.get("file")

        if not template_id:
            flash("ID szablonu jest wymagane.", "danger")
            return redirect(url_for("roles.mailing"))

        if not upload_file or not upload_file.filename:
            flash("Wybierz plik CSV lub XLSX z adresami e-mail.", "danger")
            return redirect(url_for("roles.mailing"))

        if not visible_to_email:
            flash("Podaj adres widoczny w polu Do (To).", "danger")
            return redirect(url_for("roles.mailing"))

        try:
            visible_to_email = validate_email(visible_to_email, check_deliverability=False).email
        except EmailNotValidError:
            flash("Adres widoczny w polu Do (To) jest nieprawidłowy.", "danger")
            return redirect(url_for("roles.mailing"))

        try:
            if send_at_raw:
                local_dt = datetime.fromisoformat(send_at_raw).replace(tzinfo=warsaw_tz)
                send_at = local_dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            else:
                send_at = datetime.utcnow()
        except ValueError:
            flash("Nieprawidłowa data wysyłki.", "danger")
            return redirect(url_for("roles.mailing"))

        original_name = secure_filename(upload_file.filename)
        if not original_name:
            flash("Nieprawidłowa nazwa pliku.", "danger")
            return redirect(url_for("roles.mailing"))

        _, ext = os.path.splitext(original_name)
        ext = ext.lower()
        if ext not in {".csv", ".xlsx", ".xlsm", ".xltx", ".xltm"}:
            flash("Obsługiwane są tylko pliki CSV lub XLSX.", "danger")
            return redirect(url_for("roles.mailing"))

        stored_name = f"{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "mailing")
        os.makedirs(upload_dir, exist_ok=True)
        stored_path = os.path.join(upload_dir, stored_name)
        upload_file.save(stored_path)

        try:
            emails = parse_recipient_file(stored_path)
        except Exception as exc:
            if os.path.exists(stored_path):
                os.remove(stored_path)
            flash(str(exc), "danger")
            return redirect(url_for("roles.mailing"))

        if not emails:
            if os.path.exists(stored_path):
                os.remove(stored_path)
            flash("Plik nie zawiera poprawnych adresów e-mail.", "danger")
            return redirect(url_for("roles.mailing"))

        batch = models.MailingBatch(
            template_type_id=template_type.id if template_type else None,
            template_id=template_id,
            template_data=json.dumps(template_data, ensure_ascii=False) if template_data else None,
            visible_to_email=visible_to_email,
            visible_to_name=visible_to_name,
            send_at=send_at,
            total_recipients=len(emails),
            original_name=original_name,
            stored_name=stored_name,
            auto_delete=auto_delete,
            status="queued",
        )
        db.session.add(batch)
        db.session.commit()

        enqueue_mailing_batch(batch.id)
        flash("Wysyłka została zaplanowana.", "success")
        return redirect(url_for("roles.mailing"))

    if request.method == "POST" and request.form.get("action") == "retry":
        batch_id = request.form.get("batch_id")
        if batch_id:
            batch = models.MailingBatch.query.get(int(batch_id))
            if batch:
                enqueue_mailing_batch(batch.id)
                flash("Wysyłka została ponownie zaplanowana.", "success")
        return redirect(url_for("roles.mailing"))

    batches = models.MailingBatch.query.order_by(models.MailingBatch.created_at.desc()).all()
    default_visible = current_app.config.get("MAIL_DEFAULT_SENDER_EMAIL", "")
    default_name = current_app.config.get("MAIL_DEFAULT_SENDER_NAME", "")
    for batch in batches:
        if batch.created_at:
            batch.created_at = batch.created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(warsaw_tz)
        if batch.send_at:
            batch.send_at = batch.send_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(warsaw_tz)
    template_types = models.MailingTemplateType.query.order_by(models.MailingTemplateType.name.asc()).all()
    selected_type = None
    selected_fields = []
    selected_type_id = request.args.get("type_id")
    if selected_type_id:
        selected_type = models.MailingTemplateType.query.get(int(selected_type_id))
        if selected_type and selected_type.fields:
            for line in selected_type.fields.splitlines():
                line = line.strip()
                if not line:
                    continue
                if "|" in line:
                    key, label = [part.strip() for part in line.split("|", 1)]
                else:
                    key, label = line, line
                if key:
                    selected_fields.append({"key": key, "label": label or key})
    return render_template(
        "roles/mailing.html",
        batches=batches,
        default_visible=default_visible,
        default_name=default_name,
        template_types=template_types,
        selected_type=selected_type,
        selected_fields=selected_fields,
    )


@roles_bp.route("/mailing-types", methods=["GET", "POST"])
@roles_accepted("admin")
def mailing_types():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        template_id = (request.form.get("template_id") or "").strip()
        fields = (request.form.get("fields") or "").strip() or None

        if not name or not template_id:
            flash("Nazwa i ID szablonu są wymagane.", "danger")
            return redirect(url_for("roles.mailing_types"))

        existing = models.MailingTemplateType.query.filter_by(name=name).first()
        if existing:
            flash("Taki typ maila już istnieje.", "danger")
            return redirect(url_for("roles.mailing_types"))

        db.session.add(
            models.MailingTemplateType(
                name=name,
                template_id=template_id,
                fields=fields,
            )
        )
        db.session.commit()
        flash("Typ maila został zapisany.", "success")
        return redirect(url_for("roles.mailing_types"))

    template_types = models.MailingTemplateType.query.order_by(models.MailingTemplateType.created_at.desc()).all()
    return render_template("roles/mailing_types.html", template_types=template_types)


@roles_bp.route("/mailing-types/<int:type_id>/delete", methods=["POST"])
@roles_accepted("admin")
def delete_mailing_type(type_id: int):
    template_type = models.MailingTemplateType.query.get(type_id)
    if not template_type:
        flash("Typ maila nie istnieje.", "danger")
        return redirect(url_for("roles.mailing_types"))

    db.session.delete(template_type)
    db.session.commit()
    flash("Typ maila został usunięty.", "success")
    return redirect(url_for("roles.mailing_types"))


@roles_bp.route("/downloads/<int:file_id>/delete", methods=["POST"])
@roles_accepted("admin")
def delete_download(file_id):
    file_obj = models.DownloadFile.query.get(file_id)
    if not file_obj:
        flash("Plik nie istnieje.", "danger")
        return redirect(url_for("roles.downloads"))

    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "downloads", file_obj.stored_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(file_obj)
    db.session.commit()
    flash("Plik został usunięty.", "success")
    return redirect(url_for("roles.downloads"))
