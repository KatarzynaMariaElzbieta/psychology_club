import dash
from flask import url_for

import dash_mantine_components as dmc

from ... import db
from ...models import Article

dash.register_page(__name__, path="/", name="Psychologii WAM")

def get_last_articles():
    articles = db.session.query(Article).order_by(Article.created_at.desc()).limit(4)
    return articles

def generate_card(number, article):
    if article.main_image:
        img_src = url_for("static", filename=article.main_image.file_path)
    else:
        img_src = "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-4.png"

    return dmc.CarouselSlide(dmc.Card(
        [
            dmc.CardSection(dmc.Text(number, size="xl", m=20, mb=10, className="card_number")),
            dmc.CardSection(dmc.Image(
                src=img_src,
                fallbackSrc="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-4.png",
                h=200
            )
            ),
            dmc.CardSection(
                [dmc.Title(article.title, order=4),
                 dmc.Text([
                     article.short_content,
                     dmc.Anchor(" Czytaj dalej>", href=f"artykul/{article.id}",
                                style={"color": "Blue", "align": "right", "font-weight": "normal"})

                 ]),
                 ],
            p=10)
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    ))

def main_layout():
    return (
    dash.html.Div([
        dmc.Title("Aktualności", order=1, style={"margin-left": "9rem", "color": "#3b3b3c"}),
        dmc.Center([
            dmc.Carousel(
                [
                    generate_card(f"{i:02}", a) for i, a in enumerate(get_last_articles(), 1)
                ],
                id="carousel-simple",
                orientation="horizontal",
                withControls=True,
                withIndicators=False,
                slideSize={"base": "100%", "sm": "40%", "md": "33.333333%"},
                slideGap="xl",
                emblaOptions={"loop": True, "align": "start", "slidesToScroll": 1},
                controlSize=50,
                style={"margin": "1rem"},
                w=1200,
            )
        ],
        p=100,
        pt=0,
        pb=0),
    ],
    className="padding_top_main")

)

layout = main_layout
