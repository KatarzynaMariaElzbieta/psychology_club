# Psychology Club App

## Reset hasła przez e-mail (MailerSend API)

Ustaw w środowisku:

```env
SECURITY_RECOVERABLE=true
SECURITY_PASSWORD_SALT=<losowy_salt>

MAILERSEND_API_TOKEN=<token_api_mailersend>
MAILERSEND_API_URL=https://api.mailersend.com/v1/email
MAIL_DEFAULT_SENDER=no-reply@twojadomena.pl
SECURITY_EMAIL_SENDER=no-reply@twojadomena.pl
MAIL_TIMEOUT=30
MAILERSEND_BATCH_SIZE=10
MAILERSEND_DAILY_LIMIT=100
MAILERSEND_BATCH_DELAY_SECONDS=1
MAILERSEND_RETRY_MAX=3
MAILERSEND_RETRY_BASE_DELAY_SECONDS=1
REDIS_URL=redis://localhost:6379/0

USE_SERVER_NAME=true
SERVER_NAME=www.twojadomena.pl
PREFERRED_URL_SCHEME=https
```

Uwagi:
- Na środowisku lokalnym możesz ustawić `USE_SERVER_NAME=false`, wtedy link resetu użyje hosta bieżącego żądania.
- Jeśli `MAILERSEND_API_TOKEN` nie jest ustawiony, aplikacja spróbuje użyć standardowego backendu SMTP.

Szybki test API (na serwerze):

```bash
curl -i https://api.mailersend.com/v1/email \
  -H "Authorization: Bearer $MAILERSEND_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {"email": "no-reply@mail.psychowam.pl"},
    "to": [{"email": "twoj-testowy-email@example.com"}],
    "subject": "Test MailerSend",
    "text": "Test"
  }'

## Mailing wydarzeń (CSV/XLSX + harmonogram)

Mailing działa przez kolejkę RQ i Redis. W produkcji uruchom osobny proces workera.

### Lokalnie (docker-compose)

Po zmianach w `docker-compose.yml` uruchamiasz:

```bash
docker compose up --build
```

Uruchomi się:
- web (Flask)
- worker (RQ + scheduler)
- redis
- postgres

### Railway

Dodaj usługę Redis (plugin) i ustaw `REDIS_URL` w env.

Ustaw dwa procesy (w repo jest `railway.json`):
- Web: `poetry run gunicorn -w 2 -b 0.0.0.0:8080 wsgi:app`
- Worker: `poetry run rq worker mailing --with-scheduler`

Jeśli Railway nie odczyta automatycznie `railway.json`, dodaj drugi serwis ręcznie
i ustaw powyższe start commands.
```
