from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_security import SQLAlchemyUserDatastore, roles_accepted

from app import models
from app.extensions import db

roles_bp = Blueprint("roles", __name__, url_prefix="/roles")

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
