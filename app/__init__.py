import os

from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, send_from_directory
from flask_security import SQLAlchemyUserDatastore, roles_accepted

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
from app.extensions import db, mail, migrate, security
from app.security_forms import ClubRegisterForm


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
    app.config["SECURITY_REGISTER_FORM"] = ClubRegisterForm
    app.config["SECURITY_RECOVERABLE"] = _env_bool("SECURITY_RECOVERABLE", True)
    app.config["SECURITY_EMAIL_SENDER"] = os.getenv("SECURITY_EMAIL_SENDER") or os.getenv("MAIL_DEFAULT_SENDER")
    app.config["SECURITY_FORGOT_PASSWORD_WITHIN"] = os.getenv("SECURITY_FORGOT_PASSWORD_WITHIN", "2 days")
    app.config["SECURITY_EMAIL_SUBJECT_PASSWORD_RESET"] = os.getenv(
        "SECURITY_EMAIL_SUBJECT_PASSWORD_RESET",
        "Instrukcja resetu hasła",
    )
    app.config["SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE"] = os.getenv(
        "SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE",
        "Hasło zostało zresetowane",
    )
    app.config["SECURITY_MSG_PASSWORD_RESET_REQUEST"] = (
        "Jeśli konto istnieje, wysłaliśmy e-mail z linkiem do resetu hasła. "
        "Sprawdź również folder SPAM.",
        "info",
    )
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")
    app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
    app.config["SECURITY_URL_PREFIX"] = "/auth"
    app.config["SECURITY_REMEMBER_ME"] = True

    # SMTP / e-mail
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "")
    app.config["MAIL_PORT"] = _env_int("MAIL_PORT", 587)
    app.config["MAIL_USE_TLS"] = _env_bool("MAIL_USE_TLS", True)
    app.config["MAIL_USE_SSL"] = _env_bool("MAIL_USE_SSL", False)
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "")
    app.config["MAIL_TIMEOUT"] = _env_int("MAIL_TIMEOUT", 10)

    # Publiczny host do linków absolutnych (np. reset hasła) ustawiaj świadomie.
    # Lokalnie lepiej bazować na aktualnym hoście żądania, bez wymuszania SERVER_NAME.
    if _env_bool("USE_SERVER_NAME", False):
        server_name = os.getenv("SERVER_NAME", "").strip()
        if server_name:
            app.config["SERVER_NAME"] = server_name
    app.config["PREFERRED_URL_SCHEME"] = os.getenv("PREFERRED_URL_SCHEME", "https")

    app.config["GA4_MEASUREMENT_ID"] = os.getenv("GA4_MEASUREMENT_ID", "").strip()

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Import modeli
    from app import models  # noqa

    # 🔹 Konfiguracja Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security.init_app(app, user_datastore)

    UPLOAD_FOLDER = os.path.join(os.getcwd(), "app/uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, "downloads"), exist_ok=True)
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

    @app.route("/pobierz/<int:file_id>")
    def download_file(file_id):
        file_obj = models.DownloadFile.query.get(file_id)
        if not file_obj:
            abort(404)

        return send_from_directory(
            os.path.join(app.config["UPLOAD_FOLDER"], "downloads"),
            file_obj.stored_name,
            as_attachment=True,
            download_name=file_obj.original_name,
        )

    @app.route("/admin")
    @roles_accepted("admin")
    def admin_panel():
        return render_template("admin/panel.html")

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
