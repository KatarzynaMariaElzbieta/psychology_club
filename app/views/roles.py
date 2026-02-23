from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_security import SQLAlchemyUserDatastore, hash_password, roles_accepted

from app import models
from app.extensions import db

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
