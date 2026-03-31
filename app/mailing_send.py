import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import current_app
from urllib.parse import urlparse

from mailersend import EmailBuilder, MailerSendClient

from app.newsletter import build_unsubscribe_url


def send_bulk_template_emails(
    template_id: str,
    subject: str,
    recipients: list[dict],
    template_data: dict | None = None,
    reply_to: dict | None = None,
) -> str | None:
    """Send a bulk template email and return the bulk identifier if available."""
    subject = (subject or "").strip()
    if not subject:
        raise RuntimeError("Brak tematu wiadomości.")
    token = current_app.config.get("MAILERSEND_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Brak MAILERSEND_API_TOKEN")

    sender_email = current_app.config.get("MAIL_DEFAULT_SENDER_EMAIL", "").strip()
    if not sender_email:
        raise RuntimeError("Brak MAIL_DEFAULT_SENDER_EMAIL")

    sender_name = (current_app.config.get("MAIL_DEFAULT_SENDER_NAME") or "").strip()
    base_url = (current_app.config.get("NEWSLETTER_PUBLIC_BASE_URL") or "").strip() or None

    ms = MailerSendClient(api_key=token)
    email_requests = []

    total_recipients = 0
    for recipient in recipients:
        email = recipient.get("email")
        name = recipient.get("name")
        if not email:
            continue
        total_recipients += 1
        builder = EmailBuilder().from_email(sender_email, sender_name or None)
        to_entry = {"email": email}
        if name:
            to_entry["name"] = name
        builder = builder.to_many([to_entry])
        if reply_to and reply_to.get("email"):
            builder = builder.reply_to(reply_to["email"], reply_to.get("name"))
        data = dict(template_data or {})
        unsubscribe_url = build_unsubscribe_url(email, base_url=base_url)
        data["unsubscribe_url"] = unsubscribe_url
        print(f"{data=}")
        for k, i in data.items():
            print(f"{k=}: {i=}")
        if current_app.config.get("NEWSLETTER_LOG_UNSUBSCRIBE_URLS", False):
            current_app.logger.info(
                "Newsletter unsubscribe_url for %s: %s",
                email,
                unsubscribe_url,
            )
        else:
            parsed = urlparse(unsubscribe_url)
            token_suffix = parsed.path.rsplit("/", 1)[-1][-8:]
            current_app.logger.info(
                "Newsletter unsubscribe_url built for %s (host=%s, token_suffix=%s)",
                email,
                parsed.netloc,
                token_suffix,
            )
        builder = builder.template(template_id).personalize_many([{"email": email, "data": data}])
        payload = builder.subject(subject).build()
        payload["personalization"] = [{"email": email, "data": data}]
        if current_app.config.get("NEWSLETTER_LOG_EMAIL_PAYLOADS", False):
            personalization = payload.get("personalization") or payload.get("personalisation")
            keys = None
            if personalization and personalization[0].get("data"):
                keys = list(personalization[0]["data"].keys())
            current_app.logger.info(
                "MailerSend payload: template_id=%s to=%s personalization_keys=%s",
                payload.get("template_id"),
                payload.get("to"),
                keys,
            )
        email_requests.append(payload)

    if not email_requests:
        return None
    current_app.logger.info("MailerSend bulk template: prepared %s recipients", total_recipients)

    response = ms.emails.send_bulk(email_requests)

    if isinstance(response, dict):
        if response.get("message") not in {None, "Bulk email queued"}:
            raise RuntimeError(f"MailerSend odpowiedź: {response}")
        return response.get("bulk_email_id")

    bulk_email_id = getattr(response, "bulk_email_id", None)
    if bulk_email_id:
        return bulk_email_id
    return None


def get_bulk_email_status(bulk_email_id: str) -> dict:
    """Fetch bulk email status details from MailerSend."""
    token = current_app.config.get("MAILERSEND_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Brak MAILERSEND_API_TOKEN")

    url = f"https://api.mailersend.com/v1/bulk-email/{bulk_email_id}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "psychology-club-mailer/1.0",
        },
        method="GET",
    )

    try:
        with urlopen(req, timeout=10) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except HTTPError as exc:
        payload = exc.read().decode("utf-8") if exc.fp else ""
        raise RuntimeError(f"MailerSend HTTP {exc.code}: {payload}") from exc
    except URLError as exc:
        raise RuntimeError(f"MailerSend URL error: {exc}") from exc
