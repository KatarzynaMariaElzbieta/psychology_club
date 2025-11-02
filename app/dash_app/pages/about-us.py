import bleach
import dash
import dash_mantine_components as dmc
from dash import html
from dash_extensions import Purify

from app import db
from app.models import Article

dash.register_page(__name__, path="/o-nas/")


def get_about_us():
    article = db.session.query(Article).filter(Article.title == "O nas").first()
    return article.content


def create_layout():
    return dmc.Container(
        dmc.Paper(
            [
                dmc.Text(
                    dmc.Title("O nas", order=1, style={"marginBottom": "1rem", "padding-top": "1rem"})
                    , ta="center"),
                html.Hr(),
                html.Div([
                    Purify(html=get_about_us())
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


layout = create_layout
