import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, no_update
from flask_security import hash_password
from flask_security.utils import verify_password
from flask_login import current_user

from app import db
from app.models import User


dash.register_page(__name__, path="/moje-konto", name="Moje konto")


def serve_layout():
    if not current_user or not current_user.is_authenticated:
        return dcc.Location(href="/auth/login", id="redirect-my-account-login")

    return dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Title("Moje konto", order=1),
                    dmc.Text("Możesz zaktualizować swoje dane i deklaracje.", c="dimmed"),
                ],
                gap="xs",
                mb="lg",
            ),
            dmc.Paper(
                [
                    dmc.Stack(
                        [
                            dmc.TextInput(
                                id="my-account-email",
                                label="E-mail",
                                value=current_user.email,
                                required=True,
                            ),
                            dmc.TextInput(
                                id="my-account-username",
                                label="Nazwa użytkownika",
                                value=current_user.username or "",
                                required=True,
                            ),
                            dmc.TextInput(
                                id="my-account-phone",
                                label="Numer telefonu (opcjonalnie)",
                                value=current_user.phone or "",
                            ),
                            dmc.Checkbox(
                                id="my-account-wants-active-membership",
                                label="Wyrażam chęć dołączenia do koła jako jego aktywny członek",
                                checked=bool(current_user.wants_active_membership),
                            ),
                            dmc.Checkbox(
                                id="my-account-wants-email-notifications",
                                label="Chcę być informowany mailowo o planowanych wydarzeniach",
                                checked=bool(current_user.wants_email_notifications),
                            ),
                            dmc.Checkbox(
                                id="my-account-image-consent",
                                label="Wyrażam zgodę na użycie mojego wizerunku na stronie koła i w jego social mediach",
                                checked=bool(current_user.image_consent),
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Zapisz zmiany",
                                        id="my-account-save-btn",
                                        color="teal",
                                    )
                                ],
                                justify="flex-end",
                                mt="sm",
                            ),
                            dmc.Box(id="my-account-save-status"),
                            dmc.Divider(my="sm"),
                            dmc.Title("Zmiana hasła", order=4),
                            dmc.PasswordInput(
                                id="my-account-current-password",
                                label="Aktualne hasło",
                                required=True,
                            ),
                            dmc.PasswordInput(
                                id="my-account-new-password",
                                label="Nowe hasło",
                                required=True,
                                description="Minimum 8 znaków.",
                            ),
                            dmc.PasswordInput(
                                id="my-account-new-password-confirm",
                                label="Powtórz nowe hasło",
                                required=True,
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Zmień hasło",
                                        id="my-account-change-password-btn",
                                        color="blue",
                                        variant="light",
                                    )
                                ],
                                justify="flex-end",
                            ),
                            dmc.Box(id="my-account-password-status"),
                            dmc.Divider(my="sm"),
                            dmc.Title("Usunięcie konta", order=4, c="red"),
                            dmc.Text(
                                "Usunięcie konta oznacza jego dezaktywację. Po wykonaniu tej operacji zostaniesz wylogowany/a.",
                                size="sm",
                                c="dimmed",
                            ),
                            dmc.Checkbox(
                                id="my-account-delete-confirm",
                                label="Potwierdzam dezaktywację mojego konta",
                                color="red",
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Usuń konto",
                                        id="my-account-delete-btn",
                                        color="red",
                                        variant="filled",
                                    )
                                ],
                                justify="flex-end",
                            ),
                            dmc.Box(id="my-account-delete-status"),
                            dmc.Box(id="my-account-redirect"),
                        ],
                        gap="sm",
                    )
                ],
                withBorder=True,
                radius="md",
                shadow="xs",
                p="lg",
            ),
        ],
        size="md",
        py="xl",
        style={"min-height": "calc(100vh - 130px)"},
    )


layout = serve_layout


@callback(
    Output("my-account-save-status", "children"),
    Input("my-account-save-btn", "n_clicks"),
    State("my-account-email", "value"),
    State("my-account-username", "value"),
    State("my-account-phone", "value"),
    State("my-account-wants-active-membership", "checked"),
    State("my-account-wants-email-notifications", "checked"),
    State("my-account-image-consent", "checked"),
    prevent_initial_call=True,
)
def save_my_account(
    _n_clicks,
    email,
    username,
    phone,
    wants_active_membership,
    wants_email_notifications,
    image_consent,
):
    if not current_user or not current_user.is_authenticated:
        return dmc.Alert("Sesja wygasła. Zaloguj się ponownie.", color="red", variant="light")

    email_normalized = (email or "").strip().lower()
    username_normalized = (username or "").strip()
    phone_normalized = (phone or "").strip() or None

    if not email_normalized:
        return dmc.Alert("Adres e-mail jest wymagany.", color="red", variant="light")
    if "@" not in email_normalized:
        return dmc.Alert("Podaj poprawny adres e-mail.", color="red", variant="light")
    if not username_normalized:
        return dmc.Alert("Nazwa użytkownika jest wymagana.", color="red", variant="light")

    email_taken = User.query.filter(User.email == email_normalized, User.id != current_user.id).first()
    if email_taken:
        return dmc.Alert("Ten adres e-mail jest już zajęty.", color="red", variant="light")

    user = User.query.get(current_user.id)
    if not user:
        return dmc.Alert("Nie znaleziono użytkownika.", color="red", variant="light")

    user.email = email_normalized
    user.username = username_normalized
    user.phone = phone_normalized
    user.wants_active_membership = bool(wants_active_membership)
    user.wants_email_notifications = bool(wants_email_notifications)
    user.image_consent = bool(image_consent)
    db.session.commit()

    return dmc.Alert("Dane zostały zapisane.", color="green", variant="light")


@callback(
    Output("my-account-password-status", "children"),
    Output("my-account-current-password", "value"),
    Output("my-account-new-password", "value"),
    Output("my-account-new-password-confirm", "value"),
    Input("my-account-change-password-btn", "n_clicks"),
    State("my-account-current-password", "value"),
    State("my-account-new-password", "value"),
    State("my-account-new-password-confirm", "value"),
    prevent_initial_call=True,
)
def change_my_password(_n_clicks, current_password, new_password, new_password_confirm):
    if not current_user or not current_user.is_authenticated:
        return (
            dmc.Alert("Sesja wygasła. Zaloguj się ponownie.", color="red", variant="light"),
            no_update,
            no_update,
            no_update,
        )

    current_password = current_password or ""
    new_password = new_password or ""
    new_password_confirm = new_password_confirm or ""

    if not current_password or not new_password or not new_password_confirm:
        return (
            dmc.Alert("Wypełnij wszystkie pola hasła.", color="red", variant="light"),
            no_update,
            no_update,
            no_update,
        )

    user = User.query.get(current_user.id)
    if not user:
        return (
            dmc.Alert("Nie znaleziono użytkownika.", color="red", variant="light"),
            no_update,
            no_update,
            no_update,
        )

    if not verify_password(current_password, user.password):
        return (
            dmc.Alert("Aktualne hasło jest niepoprawne.", color="red", variant="light"),
            "",
            "",
            "",
        )

    if len(new_password) < 8:
        return (
            dmc.Alert("Nowe hasło musi mieć co najmniej 8 znaków.", color="red", variant="light"),
            "",
            "",
            "",
        )

    if new_password != new_password_confirm:
        return (
            dmc.Alert("Nowe hasła nie są identyczne.", color="red", variant="light"),
            "",
            "",
            "",
        )

    user.password = hash_password(new_password)
    db.session.commit()

    return (
        dmc.Alert("Hasło zostało zmienione.", color="green", variant="light"),
        "",
        "",
        "",
    )


@callback(
    Output("my-account-delete-status", "children"),
    Output("my-account-redirect", "children"),
    Input("my-account-delete-btn", "n_clicks"),
    State("my-account-delete-confirm", "checked"),
    prevent_initial_call=True,
)
def deactivate_my_account(_n_clicks, is_confirmed):
    if not current_user or not current_user.is_authenticated:
        return dmc.Alert("Sesja wygasła. Zaloguj się ponownie.", color="red", variant="light"), no_update

    if not is_confirmed:
        return dmc.Alert("Zaznacz potwierdzenie, aby dezaktywować konto.", color="red", variant="light"), no_update

    user = User.query.get(current_user.id)
    if not user:
        return dmc.Alert("Nie znaleziono użytkownika.", color="red", variant="light"), no_update

    user.active = False
    db.session.commit()

    return (
        dmc.Alert("Konto zostało dezaktywowane. Trwa wylogowanie.", color="green", variant="light"),
        dcc.Location(href="/auth/logout", id="my-account-logout-redirect"),
    )
