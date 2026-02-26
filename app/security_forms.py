from flask_security.forms import RegisterForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired, Length, Optional


class ClubRegisterForm(RegisterForm):
    username = StringField(
        "Nazwa użytkownika",
        validators=[
            DataRequired(message="Nazwa użytkownika jest wymagana."),
            Length(max=100),
        ],
    )
    phone = StringField(
        "Numer telefonu (opcjonalnie)",
        validators=[Optional(), Length(max=20)],
    )
    statute_accepted = BooleanField(
        "Zapoznałem/am się i akceptuję statut koła",
        validators=[
            DataRequired(
                message="Akceptacja statutu koła jest wymagana, aby się zarejestrować."
            )
        ],
    )
    wants_active_membership = BooleanField(
        "Wyrażam chęć dołączenia do koła jako jego aktywny członek"
    )
    wants_email_notifications = BooleanField(
        "Chcę być informowany mailowo o planowanych wydarzeniach"
    )
    image_consent = BooleanField(
        "Wyrażam zgodę na użycie mojego wizerunku na stronie koła i w jego social mediach"
    )
