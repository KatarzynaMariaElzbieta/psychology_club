from flask_security import current_user
from dash import dcc
from dash.exceptions import PreventUpdate
from functools import wraps


def require_roles(*roles, redirect_to=None):
    """
    Dekorator dla layoutów Dash.
    Blokuje dostęp do widoku jeśli użytkownik nie jest zalogowany lub nie ma wymaganej roli.

    redirect_to: jeśli podany, wykonuje redirect do wskazanej strony.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                if redirect_to:
                    return dcc.Location(href=redirect_to, id="redirect-login")
                else:
                    return dcc.Markdown("⛔ Zaloguj się, aby zobaczyć tę stronę")

            if not any(current_user.has_role(role) for role in roles):
                if redirect_to:
                    return dcc.Location(href=redirect_to, id="redirect-no-access")
                else:
                    return dcc.Markdown("⛔ Nie masz uprawnień do tej strony")

            return func(*args, **kwargs)

        return wrapper

    return decorator
