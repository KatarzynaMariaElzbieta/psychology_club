import os
from flask import Flask, redirect
from dotenv import load_dotenv
from flask_security import SQLAlchemyUserDatastore

from app.extensions import db, migrate, security


def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    app.config['SECURITY_CONFIRMABLE'] = False
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
    app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    app.config["SECURITY_URL_PREFIX"] = "/auth"
    app.config["SECURITY_REMEMBER_ME"] = True

    db.init_app(app)
    migrate.init_app(app, db)


    #Import modeli
    from app import models # noqa


    # 🔹 Konfiguracja Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security.init_app(app, user_datastore)


    #Inicjalizacja Dash
    from app.dash_app import init_dash
    init_dash(app)

    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

    @app.route('/')
    def index():
        return redirect('/aktualnosci/')

    return app