from flask import current_app
from mailersend import EmailBuilder, MailerSendClient


def send_bulk_template_emails(
    template_id: str,
    subject: str,
    recipients: list[dict],
    template_data: dict | None = None,
    reply_to: dict | None = None,
) -> None:
    token = current_app.config.get("MAILERSEND_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Brak MAILERSEND_API_TOKEN")

    sender_email = current_app.config.get("MAIL_DEFAULT_SENDER_EMAIL", "").strip()
    if not sender_email:
        raise RuntimeError("Brak MAIL_DEFAULT_SENDER_EMAIL")

    sender_name = (current_app.config.get("MAIL_DEFAULT_SENDER_NAME") or "").strip()

    ms = MailerSendClient(api_key=token)
    email_requests = []

    for recipient in recipients:
        email = recipient.get("email")
        name = recipient.get("name")
        if not email:
            continue
        builder = EmailBuilder().from_email(sender_email, sender_name or None)
        builder = builder.to(email, name)
        if reply_to and reply_to.get("email"):
            builder = builder.reply_to(reply_to["email"], reply_to.get("name"))
        if template_data:
            builder = builder.personalize(email, **template_data)
        email_requests.append(builder.subject(subject).template(template_id).build())

    if not email_requests:
        return

    response = ms.emails.send_bulk(email_requests)

    if isinstance(response, dict) and response.get("message") not in {None, "Bulk email queued"}:
        raise RuntimeError(f"MailerSend odpowiedź: {response}")
