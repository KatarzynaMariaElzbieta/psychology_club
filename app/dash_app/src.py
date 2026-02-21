import bleach
from bleach.css_sanitizer import CSSSanitizer
import dash_mantine_components as dmc

from flask import has_request_context
from flask_security import current_user
from dash import dcc
from dash.exceptions import PreventUpdate
from functools import wraps

from app.models import Article


def require_roles(*roles, redirect_to=None):
    """
    Dekorator dla layoutów Dash.
    Blokuje dostęp do widoku jeśli użytkownik nie jest zalogowany lub nie ma wymaganej roli.

    redirect_to: jeśli podany, wykonuje redirect do wskazanej strony.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_request_context() or not getattr(current_user, "is_authenticated", False):
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


def require_admin_or_author(article_id_getter=None, redirect_to=None, raise_on_fail=False):
    """
    Dekorator dla layoutów i callbacków Dash.
    Zezwala adminowi lub autorowi artykułu.

    article_id_getter: opcjonalna funkcja do pobrania ID artykułu z args/kwargs.
    raise_on_fail: jeśli True, podnosi PreventUpdate zamiast zwracać komponent.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_request_context() or not getattr(current_user, "is_authenticated", False):
                if redirect_to:
                    return dcc.Location(href=redirect_to, id="redirect-login")
                if raise_on_fail:
                    raise PreventUpdate
                return dcc.Markdown("⛔ Zaloguj się, aby zobaczyć tę stronę")

            if current_user.has_role("admin"):
                return func(*args, **kwargs)

            if article_id_getter:
                article_id = article_id_getter(*args, **kwargs)
            else:
                article_id = kwargs.get("article_id")
                if article_id is None:
                    article_id = kwargs.get("id")
                if article_id is None and args:
                    article_id = args[0]

            try:
                article_id = int(article_id)
            except (TypeError, ValueError):
                article_id = None

            if not article_id:
                if redirect_to:
                    return dcc.Location(href=redirect_to, id="redirect-no-article")
                if raise_on_fail:
                    raise PreventUpdate
                return dcc.Markdown("⛔ Nie można ustalić artykułu")

            article = Article.query.get(article_id)
            if not article or current_user not in article.authors:
                if redirect_to:
                    return dcc.Location(href=redirect_to, id="redirect-no-access")
                if raise_on_fail:
                    raise PreventUpdate
                return dcc.Markdown("⛔ Nie masz uprawnień do tego artykułu")

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


def url_for_uploads(filename):
    return f"/media/{filename}"
