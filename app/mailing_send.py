from flask import current_app
from mailersend import EmailBuilder, MailerSendClient


def send_template_email(
    template_id: str,
    subject: str,
    visible_to: dict,
    bcc_list: list[dict],
    template_data: dict | None = None,
) -> None:
    token = current_app.config.get("MAILERSEND_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Brak MAILERSEND_API_TOKEN")

    sender_email = current_app.config.get("MAIL_DEFAULT_SENDER_EMAIL", "").strip()
    if not sender_email:
        raise RuntimeError("Brak MAIL_DEFAULT_SENDER_EMAIL")

    sender_name = (current_app.config.get("MAIL_DEFAULT_SENDER_NAME") or "").strip()

    ms = MailerSendClient(api_key=token)
    builder = EmailBuilder().from_email(sender_email, sender_name or None)

    if visible_to.get("name"):
        builder = builder.to_many([{"email": visible_to["email"], "name": visible_to["name"]}])
    else:
        builder = builder.to_many([{"email": visible_to["email"]}])

    if bcc_list:
        for recipient in bcc_list:
            email = recipient.get("email")
            name = recipient.get("name")
            if email:
                if name:
                    builder = builder.bcc(email, name)
                else:
                    builder = builder.bcc(email)

    # Brak personalizacji - wysyłka jednolita do wszystkich odbiorców.

    email = builder.subject(subject).template(template_id).build()
    response = ms.emails.send(email)

    if isinstance(response, dict):
        if response.get("message") not in {"Email sent", "Email queued", None}:
            raise RuntimeError(f"MailerSend odpowiedź: {response}")
