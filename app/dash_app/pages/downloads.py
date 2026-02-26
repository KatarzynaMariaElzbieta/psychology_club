import dash
import dash_mantine_components as dmc

from app.models import DownloadFile

dash.register_page(__name__, path="/do-pobrania", name="Do pobrania")


def serve_layout():
    files = DownloadFile.query.order_by(DownloadFile.id).all()

    if not files:
        file_list = dmc.Text("Brak plików do pobrania.", c="dimmed")
    else:
        file_list = dmc.Center(
            dmc.List(
                [
                    dmc.ListItem(
                        dmc.Anchor(
                            file.title,
                            href=f"/pobierz/{file.id}",
                            target="_blank",
                            style={
                                "color": "black",
                                "font-size": "18px",
                            },
                            fw=500,
                        ),
                    )
                    for file in files
                ],
                type="ordered",
            ),
        )

    return dmc.Stack(
        [
            dmc.Container(
                [
                    dmc.Title("Do pobrania"),
                    dmc.Divider(variant="solid", w="100%"),
                ],
                style={"margin-top": "1rem"},
            ),
            dmc.Stack(
                [
                    dmc.Text("W tym miejscu znajdziesz pliki udostępnione przez koło.", c="dimmed", mb="lg"),
                ],
                align="center",
                gap="xs",
            ),
            file_list,
        ],
        align="center",
        justify="center",
        gap="md",
        m={
            "base": "5% 15%",
            "md": "3% 25%",
        },
    )


layout = serve_layout
