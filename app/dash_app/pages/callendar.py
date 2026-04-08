import dash
import dash_mantine_components as dmc
from dash import html

dash.register_page(
    __name__,
    path="/kalendarium",
    name="Kalendarium",
    title="Kalendarium | Psychowam",
    description="Terminy wydarzeń, spotkań i aktywności Koła Psychologii WAM.",
)  # rejestracja strony


def site_in_build():
    return dmc.Center(
        [
            dmc.Paper(
                "Stona w budowie.",
                radius="sm",
                p="lg",
                shadow="sm",
                withBorder=False,
            )
        ],
    )


def calendar_layout():
    return dmc.Center(
        html.Iframe(
            src=(
                "https://calendar.google.com/calendar/embed?height=600&wkst=2&ctz=Europe%2FWarsaw&"
                "showPrint=0&showCalendars=0&title=Harmonogram%20ko%C5%82a%20naukowego&showTitle=0&"
                "src=MjhhZGYwYjJiY2ZmZmIwYzY3MTBiNjQxMjMzZjZkNDMyNjE2YzllYmFmMWMyNjA0NjE3MGQ3NGVmYThk"
                "MjU4YkBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&"
                "src=cGwucG9saXNoI2hvbGlkYXlAZ3JvdXAudi5jYWxlbmRhci5nb29nbGUuY29t&"
                "color=%237cb342&color=%230b8043"
            ),
            style={"border": "solid 1px #777", "width": "100%", "maxWidth": "900px", "height": "600px"},
        ),
    )


layout = dmc.Stack(
    [
        dmc.Container(
            [
                dmc.Title("Kalendarium"),
                dmc.Divider(variant="solid", w="100%"),
            ],
            style={"margin-top": "1rem"},
        ),
        dmc.Stack(
            [
                html.Div("Znajdziesz tu kalendarz wydarzeń organizowanych przez koło"),
                html.Div(" oraz dni powiązanych z psychologią"),
            ],
            align="center",
            gap="xs",
        ),
        dmc.Divider(variant="solid", w="100%"),
        calendar_layout(),
    ]
)
