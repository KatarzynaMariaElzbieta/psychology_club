from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security

try:
    from flask_mailman import Mail
except ModuleNotFoundError:  # pragma: no cover - fallback before dependency install
    class Mail:  # type: ignore[override]
        def init_app(self, _app):
            return None

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
security = Security()
