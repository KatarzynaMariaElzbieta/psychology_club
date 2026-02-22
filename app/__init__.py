import os

from dotenv import load_dotenv
from flask import Flask, redirect, send_from_directory
from flask_security import SQLAlchemyUserDatastore

from app.cookie_texts import (
    COOKIE_ACCEPT_LABEL,
    COOKIE_BANNER_MESSAGE,
    COOKIE_REJECT_LABEL,
    COOKIE_SETTINGS_LABEL,
    PRIVACY_POLICY_CONTENT,
    PRIVACY_POLICY_LABEL,
    PRIVACY_POLICY_TITLE,
)
from app.dash_app.pages.avatars import register_avatar_routes
from app.extensions import db, migrate, security


def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECURITY_REGISTERABLE"] = False
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

    @app.context_processor
    def inject_ga4_measurement_id():
        return {
            "ga4_measurement_id": app.config.get("GA4_MEASUREMENT_ID", ""),
            "cookie_banner_message": COOKIE_BANNER_MESSAGE,
            "cookie_accept_label": COOKIE_ACCEPT_LABEL,
            "cookie_reject_label": COOKIE_REJECT_LABEL,
            "cookie_settings_label": COOKIE_SETTINGS_LABEL,
            "privacy_policy_label": PRIVACY_POLICY_LABEL,
            "privacy_policy_title": PRIVACY_POLICY_TITLE,
            "privacy_policy_content": PRIVACY_POLICY_CONTENT,
        }

    return app
