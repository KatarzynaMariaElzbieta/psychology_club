import bleach
from bleach.css_sanitizer import CSSSanitizer
import dash_mantine_components as dmc

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


def prepare_html(content):
    allowed_tags = [
        "p", "br", "img", "h1", "h2", "h3", "h4", "b", "i", "strong", "em",
        "ul", "ol", "li", "a", "blockquote", "figure", "figcaption"
    ]
    allowed_attrs = {
        "img": ["src", "alt", "style"],
        "a": ["href", "title", "target", "rel"],
        "p": ["style"],
    }
    allowed_styles = [
        "color", "font-weight", "font-style", "text-decoration",
        "text-align", "background-color", "margin", "padding",
    ]
    css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        css_sanitizer=css_sanitizer,
        strip=True
    )
