from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import current_app, url_for


def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is required for newsletter unsubscribe tokens.")
    salt = current_app.config.get("NEWSLETTER_UNSUBSCRIBE_SALT", "newsletter-unsubscribe")
    return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)


def generate_unsubscribe_token(email: str) -> str:
    serializer = _get_serializer()
    normalized = (email or "").strip().lower()
    return serializer.dumps({"email": normalized})


def verify_unsubscribe_token(token: str, max_age_seconds: int | None = None) -> str | None:
    if not token:
        return None
    serializer = _get_serializer()
    try:
        data = serializer.loads(token, max_age=max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None
    email = (data.get("email") or "").strip().lower()
    return email or None


def build_unsubscribe_url(email: str, base_url: str | None = None, _external: bool = True) -> str:
    token = generate_unsubscribe_token(email)
    if base_url:
        return f"{base_url.rstrip('/')}/newsletter/unsubscribe/{token}"
    return url_for("newsletter.unsubscribe", token=token, _external=_external)
