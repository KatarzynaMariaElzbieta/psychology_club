import dash
from dash import html
import dash_mantine_components as dmc


dash.register_page(__name__, path="/", name="Aktualności")


def generate_card(number):
    return dmc.CarouselSlide(dmc.Card(
        [
            dmc.CardSection(dmc.Text(number, size="xl", m=20, mb=10, className="card_number")),
            dmc.CardSection(dmc.Image(
                src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-4.png"
            )
            ),
            dmc.CardSection(
                [dmc.Title("jakiś Tytuł", order=4),
                             dmc.Text("Opis tego co się dzieje bla bla bla")],
            p=10)
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    ))


layout = (
    html.Div([
        dmc.Title("Aktualności", order=1, style={"margin-left": "7rem"}),
        dmc.Center([
            dmc.Carousel(
                [
                    generate_card(f"{i:02}") for i in range(1, 5)
                ],
                id="carousel-simple",
                orientation="horizontal",
                withControls=True,
                withIndicators=True,
                slideSize="33.3333%",
                slideGap="md",
                emblaOptions={"loop": True, "align": "start", "slidesToScroll": 1},
                controlSize=50,
                style={"margin": "1rem"},
                w=1200,
            )
        ],
        p=100,
        pt=0),
    ],
    className="padding_top_main")

)
