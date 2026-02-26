import json
import logging
from email.utils import parseaddr
from urllib import error, request

from flask import current_app
from flask_security.mail_util import MailUtil


class MailerSendMailUtil(MailUtil):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    def send_mail(
        self,
        template,
        subject,
        recipient,
        sender,
        body,
        html,
        **kwargs,
    ):
        token = current_app.config.get("MAILERSEND_API_TOKEN", "").strip()
        if not token:
            # Fallback dla lokalnego środowiska bez API tokenu.
            return super().send_mail(template, subject, recipient, sender, body, html, **kwargs)

        sender_name, sender_email = self._normalize_sender(sender)
        payload = {
            "from": {"email": sender_email},
            "to": [{"email": recipient}],
            "subject": subject,
            "text": body,
            "html": html or f"<pre>{body}</pre>",
        }
        if sender_name:
            payload["from"]["name"] = sender_name

        api_url = current_app.config.get("MAILERSEND_API_URL", "https://api.mailersend.com/v1/email")
        timeout = int(current_app.config.get("MAIL_TIMEOUT", 10) or 10)

        req = request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "psychology-club-mailer/1.0",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=timeout) as response:
                status = getattr(response, "status", None) or response.getcode()
                if not (200 <= status < 300):
                    raise RuntimeError(f"MailerSend API zwrocilo status {status}")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            self.logger.exception("MailerSend HTTPError: %s", details)
            raise RuntimeError(f"MailerSend API blad HTTP {exc.code}: {details}") from exc
        except Exception as exc:
            self.logger.exception("MailerSend transport error")
            raise RuntimeError(f"Nie udalo sie wyslac e-maila przez MailerSend API: {exc}") from exc

    @staticmethod
    def _normalize_sender(sender):
        if isinstance(sender, tuple) and len(sender) == 2:
            return str(sender[0]).strip(), str(sender[1]).strip()

        sender_str = str(sender or "").strip()
        name, email = parseaddr(sender_str)
        if email:
            return name.strip(), email.strip()
        return "", sender_str
