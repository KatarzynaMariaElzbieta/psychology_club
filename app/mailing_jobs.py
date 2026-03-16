import json
import os
import time as time_module
import uuid
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import func

from app import create_app
from app.extensions import db
from app.mailing_import import parse_recipient_file
from app.mailing_send import get_bulk_email_status, send_bulk_template_emails
from app.models import MailingBatch

RECIPIENTS_CACHE_TTL_SECONDS = 60 * 60 * 24 * 7
FAILED_RECIPIENTS_PREFIX = "mailing:failed"
SENT_RECIPIENTS_PREFIX = "mailing:sent"
PENDING_BULK_PREFIX = "mailing:bulk:pending"
BULK_REQUEST_PREFIX = "mailing:bulk"


def _get_redis_client():
    """Create a Redis client using app configuration."""
    from redis import Redis

    redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(redis_url)


def cache_recipients(emails: list[str], cache_key: str | None = None) -> str:
    """Store a recipient list in Redis and return its cache key."""
    redis_client = _get_redis_client()
    key = cache_key or f"mailing:recipients:{uuid.uuid4().hex}"
    redis_client.setex(key, RECIPIENTS_CACHE_TTL_SECONDS, json.dumps(emails))
    return key


def get_failed_recipients_cache_key(batch_id: int) -> str:
    """Build Redis key for failed recipients in a batch."""
    return f"{FAILED_RECIPIENTS_PREFIX}:{batch_id}"


def get_sent_recipients_cache_key(batch_id: int) -> str:
    """Build Redis key for sent recipients in a batch."""
    return f"{SENT_RECIPIENTS_PREFIX}:{batch_id}"


def get_pending_bulk_cache_key(batch_id: int) -> str:
    """Build Redis key for pending bulk ids in a batch."""
    return f"{PENDING_BULK_PREFIX}:{batch_id}"


def get_bulk_request_cache_key(bulk_email_id: str) -> str:
    """Build Redis key for a bulk request payload."""
    return f"{BULK_REQUEST_PREFIX}:{bulk_email_id}"


def _load_recipients_set(cache_key: str) -> set[str]:
    """Load a recipient set from Redis."""
    try:
        redis_client = _get_redis_client()
    except Exception:
        return set()
    try:
        raw = redis_client.smembers(cache_key)
    except Exception:
        return set()
    recipients = set()
    for item in raw or []:
        if isinstance(item, bytes):
            recipients.add(item.decode("utf-8", errors="ignore"))
        else:
            recipients.add(str(item))
    return recipients


def _add_recipients_set(cache_key: str, emails: list[str]) -> None:
    """Add recipients to a Redis set and refresh its TTL."""
    if not emails:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    try:
        redis_client.sadd(cache_key, *emails)
        redis_client.expire(cache_key, RECIPIENTS_CACHE_TTL_SECONDS)
    except Exception:
        pass


def load_failed_recipients(batch_id: int) -> list[str]:
    """Load failed recipients for a batch, with legacy fallback."""
    failed = _load_recipients_set(get_failed_recipients_cache_key(batch_id))
    if failed:
        return sorted(failed)
    legacy = load_cached_recipients(get_failed_recipients_cache_key(batch_id))
    return legacy or []


def add_failed_recipients(batch_id: int, emails: list[str]) -> None:
    """Add recipients to the failed set for a batch."""
    _add_recipients_set(get_failed_recipients_cache_key(batch_id), emails)


def load_sent_recipients(batch_id: int) -> set[str]:
    """Load sent recipients for a batch."""
    return _load_recipients_set(get_sent_recipients_cache_key(batch_id))


def add_sent_recipients(batch_id: int, emails: list[str]) -> None:
    """Add recipients to the sent set for a batch."""
    _add_recipients_set(get_sent_recipients_cache_key(batch_id), emails)


def remove_failed_recipients(batch_id: int, emails: list[str]) -> None:
    """Remove recipients from the failed set for a batch."""
    if not emails:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    key = get_failed_recipients_cache_key(batch_id)
    try:
        redis_client.srem(key, *emails)
    except Exception:
        pass


def add_pending_bulk(batch_id: int, bulk_email_id: str) -> None:
    """Record a pending bulk id for a batch."""
    if not bulk_email_id:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    key = get_pending_bulk_cache_key(batch_id)
    try:
        redis_client.sadd(key, bulk_email_id)
        redis_client.expire(key, RECIPIENTS_CACHE_TTL_SECONDS)
    except Exception:
        pass


def remove_pending_bulk(batch_id: int, bulk_email_id: str) -> None:
    """Remove a pending bulk id from a batch."""
    if not bulk_email_id:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    key = get_pending_bulk_cache_key(batch_id)
    try:
        redis_client.srem(key, bulk_email_id)
    except Exception:
        pass


def has_pending_bulk(batch_id: int) -> bool:
    """Return True if a batch has pending bulk status checks."""
    try:
        redis_client = _get_redis_client()
    except Exception:
        return False
    key = get_pending_bulk_cache_key(batch_id)
    try:
        return bool(redis_client.scard(key))
    except Exception:
        return False


def cache_bulk_request(bulk_email_id: str, batch_id: int, emails: list[str], attempts: int = 0) -> None:
    """Cache bulk request metadata used to poll its status."""
    if not bulk_email_id:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    payload = {
        "batch_id": batch_id,
        "emails": emails,
        "attempts": attempts,
        "created_at": datetime.utcnow().isoformat(),
    }
    try:
        redis_client.setex(
            get_bulk_request_cache_key(bulk_email_id),
            RECIPIENTS_CACHE_TTL_SECONDS,
            json.dumps(payload),
        )
    except Exception:
        pass


def load_bulk_request(bulk_email_id: str) -> dict | None:
    """Load cached bulk request metadata."""
    if not bulk_email_id:
        return None
    try:
        redis_client = _get_redis_client()
    except Exception:
        return None
    try:
        raw = redis_client.get(get_bulk_request_cache_key(bulk_email_id))
    except Exception:
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def delete_bulk_request(bulk_email_id: str) -> None:
    """Delete cached bulk request metadata."""
    if not bulk_email_id:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    try:
        redis_client.delete(get_bulk_request_cache_key(bulk_email_id))
    except Exception:
        pass


def get_recipients_set_size(cache_key: str) -> int | None:
    """Return size of a recipient set or None on Redis errors."""
    try:
        redis_client = _get_redis_client()
    except Exception:
        return None
    try:
        return int(redis_client.scard(cache_key))
    except Exception:
        return None


def refresh_batch_counts(batch: MailingBatch) -> None:
    """Update batch sent/failed counts from Redis sets."""
    failed_size = get_recipients_set_size(get_failed_recipients_cache_key(batch.id))
    sent_size = get_recipients_set_size(get_sent_recipients_cache_key(batch.id))
    if failed_size is not None:
        batch.failed_count = failed_size
    if sent_size is not None:
        batch.sent_count = sent_size


def delete_mailing_cache(
    recipient_cache_key: str | None,
    failed_cache_key: str | None = None,
    sent_cache_key: str | None = None,
    pending_cache_key: str | None = None,
) -> None:
    """Delete recipient-related cache entries for a batch."""
    if not recipient_cache_key and not failed_cache_key and not sent_cache_key and not pending_cache_key:
        return
    try:
        redis_client = _get_redis_client()
    except Exception:
        return
    if recipient_cache_key:
        try:
            redis_client.delete(recipient_cache_key)
        except Exception:
            pass
    if failed_cache_key:
        try:
            redis_client.delete(failed_cache_key)
        except Exception:
            pass
    if sent_cache_key:
        try:
            redis_client.delete(sent_cache_key)
        except Exception:
            pass
    if pending_cache_key:
        try:
            redis_client.delete(pending_cache_key)
        except Exception:
            pass


def load_cached_recipients(cache_key: str | None) -> list[str] | None:
    """Load cached recipients list by key."""
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
    """Entry point for background worker to send a mailing batch."""
    app = create_app()
    with app.app_context():
        _send_mailing_batch(batch_id, recipient_cache_key)


def _send_mailing_batch(batch_id: int, recipient_cache_key: str | None = None) -> None:
    """Send a batch and schedule bulk status checks per chunk."""
    batch = MailingBatch.query.get(batch_id)
    if not batch:
        return
    if batch.status in {"sent", "cancelled"}:
        return

    batch.status = "sending"
    batch.last_error = None
    db.session.commit()

    failed_key = get_failed_recipients_cache_key(batch.id)
    sent_key = get_sent_recipients_cache_key(batch.id)
    use_failed_list = recipient_cache_key == failed_key
    if use_failed_list:
        emails = load_failed_recipients(batch.id)
    else:
        emails = load_cached_recipients(recipient_cache_key)
        if not emails:
            emails = load_cached_recipients(batch.recipient_cache_key)
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
        batch.last_error = (
            "Brak nieudanych adresów do ponownej wysyłki"
            if use_failed_list
            else "Brak poprawnych adresów e-mail"
        )
        db.session.commit()
        return

    emails = list(dict.fromkeys(emails))

    sent_recipients = load_sent_recipients(batch.id)
    if sent_recipients:
        emails = [email for email in emails if email not in sent_recipients]
    if not emails:
        batch.status = "failed"
        batch.last_error = "Brak nowych adresów do wysyłki"
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
    reply_to = None
    if batch.visible_to_email:
        reply_to = {"email": batch.visible_to_email}
        if batch.visible_to_name:
            reply_to["name"] = batch.visible_to_name

    failed_emails: list[str] = []

    delay_seconds = float(current_app.config.get("MAILERSEND_BATCH_DELAY_SECONDS", 1) or 1)
    retry_max = int(current_app.config.get("MAILERSEND_RETRY_MAX", 3) or 3)
    retry_base_delay = float(current_app.config.get("MAILERSEND_RETRY_BASE_DELAY_SECONDS", 1) or 1)
    status_delay_seconds = float(
        current_app.config.get("MAILERSEND_BULK_STATUS_DELAY_SECONDS", 10) or 10
    )

    for i in range(0, len(emails), batch_size):
        chunk = emails[i : i + batch_size]
        attempt = 0
        while True:
            try:
                bulk_email_id = send_bulk_template_emails(
                    batch.template_id,
                    batch.subject,
                    [{"email": email} for email in chunk],
                    template_data=template_data,
                    reply_to=reply_to,
                )
                if bulk_email_id:
                    cache_bulk_request(bulk_email_id, batch.id, chunk)
                    add_pending_bulk(batch.id, bulk_email_id)
                    enqueue_bulk_status_check(bulk_email_id, delay_seconds=status_delay_seconds)
                else:
                    failed_emails.extend(chunk)
                break
            except Exception as exc:
                error_text = str(exc)
                is_rate_limit = "429" in error_text or "Too Many Requests" in error_text
                attempt += 1
                if is_rate_limit and attempt <= retry_max:
                    time_module.sleep(retry_base_delay * (2 ** (attempt - 1)))
                    continue
                failed_emails.extend(chunk)
                batch.last_error = error_text
                break

        if delay_seconds and i + batch_size < len(emails):
            time_module.sleep(delay_seconds)

    if failed_emails:
        add_failed_recipients(batch.id, failed_emails)
        refresh_batch_counts(batch)

    if has_pending_bulk(batch.id):
        batch.status = "sending"
    else:
        refresh_batch_counts(batch)
        if batch.failed_count:
            batch.status = "failed" if batch.sent_count == 0 else "partial"
        else:
            batch.status = "sent"

    db.session.commit()

    if batch.status == "sent" and batch.auto_delete:
        delete_mailing_cache(
            batch.recipient_cache_key,
            get_failed_recipients_cache_key(batch.id),
            get_sent_recipients_cache_key(batch.id),
            get_pending_bulk_cache_key(batch.id),
        )
        try:
            stored_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "mailing", batch.stored_name)
            os.remove(stored_path)
        except OSError:
            pass


def enqueue_mailing_batch(batch_id: int, recipient_cache_key: str | None = None) -> None:
    """Enqueue batch sending now or at its scheduled time."""
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


def enqueue_bulk_status_check(bulk_email_id: str, delay_seconds: float | None = None) -> None:
    """Enqueue a bulk status check job, optionally delayed."""
    from redis import Redis
    from rq import Queue

    redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
    queue = Queue("mailing", connection=Redis.from_url(redis_url))

    if delay_seconds and delay_seconds > 0:
        queue.enqueue_in(timedelta(seconds=delay_seconds), check_bulk_email_status, bulk_email_id)
    else:
        queue.enqueue(check_bulk_email_status, bulk_email_id)


def check_bulk_email_status(bulk_email_id: str) -> None:
    """Job entry point to check a bulk email status."""
    app = create_app()
    with app.app_context():
        _check_bulk_email_status(bulk_email_id)


def _extract_failed_from_status(emails: list[str], status: dict) -> set[str]:
    """Extract failed recipients from a bulk status response."""
    data = status.get("data") if isinstance(status, dict) else {}
    if isinstance(data, list):
        data = {}
    if not data and isinstance(status, dict):
        data = status

    failed: set[str] = set()

    for item in data.get("validation_errors", []) or []:
        if not isinstance(item, dict):
            continue
        for key in item.keys():
            if not isinstance(key, str) or not key.startswith("message."):
                continue
            try:
                index = int(key.split(".", 1)[1])
            except ValueError:
                continue
            if 0 <= index < len(emails):
                failed.add(emails[index])

    for item in data.get("suppressed_recipients", []) or []:
        if isinstance(item, dict):
            email = item.get("email") or item.get("recipient")
            if email:
                failed.add(email)
        elif isinstance(item, str):
            failed.add(item)

    for key in ("failed_recipients", "failed_emails"):
        for item in data.get(key, []) or []:
            if isinstance(item, dict):
                email = item.get("email") or item.get("recipient")
                if email:
                    failed.add(email)
            elif isinstance(item, str):
                failed.add(item)

    return failed


def _check_bulk_email_status(bulk_email_id: str) -> None:
    """Process bulk status and update sent/failed sets and batch status."""
    payload = load_bulk_request(bulk_email_id)
    if not payload:
        return

    batch_id = payload.get("batch_id")
    emails = payload.get("emails") or []
    attempts = int(payload.get("attempts") or 0)

    batch = MailingBatch.query.get(batch_id) if batch_id else None
    if not batch:
        delete_bulk_request(bulk_email_id)
        return

    max_attempts = int(current_app.config.get("MAILERSEND_BULK_STATUS_MAX_ATTEMPTS", 12) or 12)
    retry_delay = float(current_app.config.get("MAILERSEND_BULK_STATUS_RETRY_DELAY_SECONDS", 15) or 15)

    try:
        status = get_bulk_email_status(bulk_email_id)
    except Exception as exc:
        attempts += 1
        if attempts <= max_attempts:
            cache_bulk_request(bulk_email_id, batch_id, emails, attempts=attempts)
            enqueue_bulk_status_check(bulk_email_id, delay_seconds=retry_delay)
            return
        batch.last_error = str(exc)
        add_failed_recipients(batch.id, emails)
        remove_pending_bulk(batch.id, bulk_email_id)
        delete_bulk_request(bulk_email_id)
        refresh_batch_counts(batch)
        db.session.commit()
        return

    data = status.get("data") if isinstance(status, dict) else {}
    state = None
    if isinstance(data, dict):
        state = data.get("state")
    if state is None and isinstance(status, dict):
        state = status.get("state")

    if state and state not in {"completed", "failed"}:
        attempts += 1
        if attempts <= max_attempts:
            cache_bulk_request(bulk_email_id, batch_id, emails, attempts=attempts)
            enqueue_bulk_status_check(bulk_email_id, delay_seconds=retry_delay)
            return

    failed = _extract_failed_from_status(emails, status)
    failed_list = [email for email in emails if email in failed]
    sent_list = [email for email in emails if email not in failed]

    if failed_list:
        add_failed_recipients(batch.id, failed_list)
    if sent_list:
        add_sent_recipients(batch.id, sent_list)
        remove_failed_recipients(batch.id, sent_list)

    remove_pending_bulk(batch.id, bulk_email_id)
    delete_bulk_request(bulk_email_id)
    refresh_batch_counts(batch)

    if not has_pending_bulk(batch.id):
        if batch.failed_count:
            batch.status = "failed" if batch.sent_count == 0 else "partial"
        else:
            batch.status = "sent"

    db.session.commit()
