import json
import os
import uuid
from datetime import datetime, time
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import func

from app import create_app
from app.extensions import db
from app.mailing_import import parse_recipient_file
from app.mailing_send import send_template_email
from app.models import MailingBatch


def _get_redis_client():
    from redis import Redis

    redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(redis_url)


def cache_recipients(emails: list[str]) -> str:
    redis_client = _get_redis_client()
    key = f"mailing:recipients:{uuid.uuid4().hex}"
    redis_client.setex(key, 60 * 60 * 24 * 7, json.dumps(emails))
    return key


def load_cached_recipients(cache_key: str | None) -> list[str] | None:
    if not cache_key:
        return None
    redis_client = _get_redis_client()
    raw = redis_client.get(cache_key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def send_mailing_batch(batch_id: int, recipient_cache_key: str | None = None) -> None:
    app = create_app()
    with app.app_context():
        _send_mailing_batch(batch_id, recipient_cache_key)


def _send_mailing_batch(batch_id: int, recipient_cache_key: str | None = None) -> None:
    batch = MailingBatch.query.get(batch_id)
    if not batch:
        return
    if batch.status in {"sent", "cancelled"}:
        return

    batch.status = "sending"
    batch.last_error = None
    db.session.commit()

    emails = load_cached_recipients(recipient_cache_key or batch.recipient_cache_key)
    if not emails:
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
        batch.last_error = "Brak poprawnych adresów e-mail"
        db.session.commit()
        return

    warsaw_tz = ZoneInfo("Europe/Warsaw")
    utc_tz = ZoneInfo("UTC")
    local_send_at = batch.send_at.replace(tzinfo=utc_tz).astimezone(warsaw_tz)
    day_start_local = datetime.combine(local_send_at.date(), time.min, tzinfo=warsaw_tz)
    day_end_local = datetime.combine(local_send_at.date(), time.max, tzinfo=warsaw_tz)
    day_start_utc = day_start_local.astimezone(utc_tz).replace(tzinfo=None)
    day_end_utc = day_end_local.astimezone(utc_tz).replace(tzinfo=None)
    daily_limit = int(current_app.config.get("MAILERSEND_DAILY_LIMIT", 100) or 100)
    already_sent = (
        db.session.query(func.coalesce(func.sum(MailingBatch.sent_count), 0))
        .filter(MailingBatch.send_at >= day_start_utc, MailingBatch.send_at <= day_end_utc)
        .scalar()
    )
    if already_sent + len(emails) > daily_limit:
        batch.status = "failed"
        batch.last_error = (
            f"Limit dzienny {daily_limit} przekroczony "
            f"(wysłano {already_sent}, planowane {len(emails)})"
        )
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
            send_template_email(
                batch.template_id,
                batch.subject,
                visible_to,
                bcc_list,
                template_data=template_data,
            )
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
        if batch.recipient_cache_key:
            try:
                _get_redis_client().delete(batch.recipient_cache_key)
            except Exception:
                pass
        try:
            stored_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "mailing", batch.stored_name)
            os.remove(stored_path)
        except OSError:
            pass


def enqueue_mailing_batch(batch_id: int, recipient_cache_key: str | None = None) -> None:
    from redis import Redis
    from rq import Queue

    redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
    queue = Queue("mailing", connection=Redis.from_url(redis_url))

    batch = MailingBatch.query.get(batch_id)
    if not batch:
        return

    send_at = batch.send_at
    now = datetime.utcnow()
    if send_at <= now:
        queue.enqueue(send_mailing_batch, batch_id, recipient_cache_key)
        batch.status = "queued"
    else:
        queue.enqueue_at(send_at, send_mailing_batch, batch_id, recipient_cache_key)
        batch.status = "scheduled"

    db.session.commit()
