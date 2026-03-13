import json
import os
from datetime import datetime

from flask import current_app

from app import create_app
from app.extensions import db
from app.mailing_import import parse_recipient_file
from app.mailing_send import send_template_email
from app.models import MailingBatch


def send_mailing_batch(batch_id: int) -> None:
    app = create_app()
    with app.app_context():
        _send_mailing_batch(batch_id)


def _send_mailing_batch(batch_id: int) -> None:
    batch = MailingBatch.query.get(batch_id)
    if not batch:
        return
    if batch.status in {"sent", "cancelled"}:
        return

    batch.status = "sending"
    batch.last_error = None
    db.session.commit()

    stored_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "mailing", batch.stored_name)
    try:
        emails = parse_recipient_file(stored_path)
    except Exception as exc:
        batch.status = "failed"
        batch.last_error = str(exc)
        db.session.commit()
        return

    template_data = None
    if batch.template_data:
        try:
            template_data = json.loads(batch.template_data)
        except json.JSONDecodeError:
            batch.status = "failed"
            batch.last_error = "Nieprawidłowe dane szablonu"
            db.session.commit()
            return

    if not emails:
        batch.status = "failed"
        batch.last_error = "Brak poprawnych adresów e-mail w pliku"
        db.session.commit()
        return

    batch_size = int(current_app.config.get("MAILERSEND_BATCH_SIZE", 10) or 10)
    visible_to = {"email": batch.visible_to_email}
    if batch.visible_to_name:
        visible_to["name"] = batch.visible_to_name

    sent = 0
    failed = 0

    for i in range(0, len(emails), batch_size):
        chunk = emails[i : i + batch_size]
        bcc_list = [{"email": email} for email in chunk]
        try:
            send_template_email(batch.template_id, visible_to, bcc_list, template_data=template_data)
            sent += len(chunk)
        except Exception as exc:
            failed += len(chunk)
            batch.last_error = str(exc)
            break

    batch.sent_count = sent
    batch.failed_count = failed
    if failed:
        batch.status = "failed" if sent == 0 else "partial"
    else:
        batch.status = "sent"

    db.session.commit()

    if batch.status == "sent" and batch.auto_delete:
        try:
            os.remove(stored_path)
        except OSError:
            pass


def enqueue_mailing_batch(batch_id: int) -> None:
    from redis import Redis
    from rq import Queue

    redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
    queue = Queue("mailing", connection=Redis.from_url(redis_url))

    batch = MailingBatch.query.get(batch_id)
    if not batch:
        return

    send_at = batch.send_at
    now = datetime.now(send_at.tzinfo)
    if send_at <= now:
        queue.enqueue(send_mailing_batch, batch_id)
        batch.status = "queued"
    else:
        queue.enqueue_at(send_at, send_mailing_batch, batch_id)
        batch.status = "scheduled"

    db.session.commit()
