import bleach
import dash
from dash import Output, Input, callback, html, dcc
import dash_mantine_components as dmc
from markupsafe import Markup
from dash_extensions import Purify

from ..src import prepare_html
from ... import db
from ...models import Article

dash.register_page(__name__, path_template='/artykul/<id>')  # rejestracja strony

layout = html.Div(id="article-content")


@callback(
    Output("article-content", "children"),
    Input("url", "pathname"),
)
def show_article(pathname):
    try:
        article_id = int(pathname.split("/")[-1])
    except (ValueError, IndexError):
        return dmc.Text("Nieprawidłowy adres artykułu", )

    # pobranie z bazy
    article = db.session.get(Article, article_id)
    if not article:
        return dmc.Text("Nie znaleziono artykułu", )

    safe_html = prepare_html(article.content)
    return dmc.Container(
        dmc.Paper(
            [
                dmc.Text(
                    dmc.Title(article.title, order=1, style={"marginBottom": "1rem", "padding-top": "1rem"})
                    , ta="center"),
                dmc.Text(
                    f"{'Autor' if len(article.authors) < 2 else 'Autorzy'}: {', '.join([author.email for author in article.authors])}",
                    size="sm", ta="center"),
                html.Hr(),
                dmc.Group([dmc.Badge(tag.name, variant="light") for tag in article.tags], justify="center", ),
                html.Hr(),
                html.Div([
                    Purify(html=safe_html)
                ])
            ],
            radius="lg",
            p="lg",
            shadow="md",
            withBorder=True,
        ),
        size="md",
        mt=20
    )
