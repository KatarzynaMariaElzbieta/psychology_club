import os

from dotenv import load_dotenv
from flask import Flask, redirect, send_from_directory
from flask_security import SQLAlchemyUserDatastore

from app.dash_app.pages.avatars import register_avatar_routes
from app.extensions import db, migrate, security


def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_CONFIRMABLE"] = False
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")
    app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
    app.config["SECURITY_URL_PREFIX"] = "/auth"
    app.config["SECURITY_REMEMBER_ME"] = True

    db.init_app(app)
    migrate.init_app(app, db)

    # Import modeli
    from app import models  # noqa

    # 🔹 Konfiguracja Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security.init_app(app, user_datastore)

    UPLOAD_FOLDER = os.path.join(os.getcwd(), "app/uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Inicjalizacja Dash
    from app.dash_app import init_dash

    init_dash(app)

    from app.views.roles import roles_bp

    app.register_blueprint(roles_bp)

    @app.route("/")
    def index():
        return redirect("/aktualnosci/")

    @app.route("/media/<path:filename>")
    def media(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    register_avatar_routes(app)
    return app
