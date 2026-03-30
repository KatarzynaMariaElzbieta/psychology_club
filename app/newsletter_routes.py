from flask import Blueprint, current_app, render_template

from app import models
from app.extensions import db
from app.newsletter import verify_unsubscribe_token


newsletter_bp = Blueprint("newsletter", __name__)


@newsletter_bp.route("/newsletter/unsubscribe/<token>", methods=["GET"])
def unsubscribe(token: str):
    max_age_seconds = current_app.config.get("NEWSLETTER_UNSUBSCRIBE_MAX_AGE_SECONDS")
    email = verify_unsubscribe_token(token, max_age_seconds=max_age_seconds)
    if not email:
        return render_template("newsletter/unsubscribe.html", status="invalid", email=None)

    subscriber = models.NewsletterSubscriber.query.filter_by(email=email).first()
    if not subscriber:
        return render_template("newsletter/unsubscribe.html", status="not_found", email=email)

    if not subscriber.is_active:
        return render_template("newsletter/unsubscribe.html", status="already", email=email)

    subscriber.is_active = False
    db.session.commit()
    return render_template("newsletter/unsubscribe.html", status="success", email=email)
