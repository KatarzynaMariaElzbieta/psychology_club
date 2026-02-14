import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, callback, html

from app.dash_app.src import url_for_uploads
from app.models import Article

dash.register_page(__name__, path="/artykuly", name="Artykuły")


def article_to_dict(article: Article) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "author": article.authors[0].email,
        "summary": article.short_content,
        "content": article.content,
        "tags": [tag.name for tag in article.tags] if article.tags else [],
        "image": article.main_image.file_path if article.main_image else None,
        "created_at": article.created_at.isoformat() if article.created_at else None,
    }


def get_articles():
    articles = Article.query.filter_by(published=True).order_by(Article.created_at.desc()).all()
    return [article_to_dict(a) for a in articles]


layout = dmc.Stack(
    [
        dmc.Container(
            [
                dmc.Title("Artykuły"),
                dmc.Divider(variant="solid", w="100%"),
            ],
            style={"margin-top": "1rem"},
        ),
        dmc.Stack(
            [
                html.Div("Znajdziesz tu artykuły na temat psychologii, badania i metaanalizy"),
                html.Div(" rezencje książek oraz felietony, a wszystko przygotowane przez naszych studentów,"),
                html.Div("Chcesz byśmy opublikowali Twoją pracę?"),
                html.Div(
                    [
                        "Chcesz byśmy opublikowali Twoją pracę? Zapraszamy do ",
                        dmc.Anchor("zakładki kontakt.", href="/kontakt", style={"color": "blue"}),
                    ]
                ),
            ],
            align="center",
            gap="xs",
        ),
        dmc.TextInput(
            id="search-input",
            placeholder="Wyszukaj po tytule, treści, autorze, tagach.",
            debounce=True,
            style={"width": "100%"},
        ),
        dmc.Box(id="artickles_containter"),
        dag.AgGrid(
            id="articles-grid",
            rowData=[],
            columnDefs=[
                {"field": "title"},
                {"field": "summary"},
                {"field": "content"},
                {"field": "tags"},
                {"field": "image"},
            ],
            dashGridOptions={
                "quickFilterText": "",
                "rowSelection": "single",
            },
            style={"display": "none"},
        ),
        dmc.Box(id="articles-list", style={"width": "100%"}),
        dmc.Pagination(
            id="articles-pagination",
            total=1,
            value=1,
            siblings=1,
            withEdges=True,
        ),
    ],
    align="center",
    justify="center",
    gap="md",
    m={
        "base": "5% 25%",
        "md": "3% 25%",
    },
    style={"min-height": "calc(100vh - 130px)"},
)


def article_card(article):
    if article["image"]:
        img_src = url_for_uploads(article["image"])
    else:
        img_src = "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-4.png"

    return dmc.Paper(
        dmc.Grid(
            children=[
                dmc.GridCol(
                    dmc.Image(
                        src=img_src,
                        fallbackSrc="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-4.png",
                        h=200,
                        fit="contain",
                    ),
                    span=4,
                ),
                dmc.GridCol(
                    dmc.Stack(
                        [
                            dmc.Title(article["title"], order=4),
                            dmc.Text(article["author"]),
                            dmc.Text(
                                [
                                    article["summary"],
                                    dmc.Anchor(
                                        " Czytaj dalej>",
                                        href=f"artykul/{article['id']}",
                                        style={"color": "Blue", "align": "right", "font-weight": "normal"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                    span=8,
                ),
            ],
            gutter="xl",
        ),
        radius="lg",
        p="lg",
        shadow="md",
        withBorder=True,
        w="100%",
        m="1rem",
    )


@callback(
    Output("articles-grid", "rowData"),
    Input("articles-grid", "id"),  # dummy trigger
)
def load_articles(_):
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return [article_to_dict(a) for a in articles]


@callback(Output("articles-grid", "dashGridOptions"), Input("search-input", "value"), prevent_initial_call=True)
def update_quick_filter(text):
    return {"quickFilterText": text or ""}


@callback(
    Output("articles-list", "children"),
    Output("articles-pagination", "total"),
    Output("articles-pagination", "style"),
    Input("articles-grid", "virtualRowData"),
    Input("articles-pagination", "value"),
)
def render_articles(filtered_rows, page):

    if not filtered_rows:
        return "Brak wyników", 1, {"display": "none"}

    per_page = 15
    total_items = len(filtered_rows)
    total_pages = (total_items + per_page - 1) // per_page

    # zabezpieczenie gdy zmniejszy się liczba stron po filtrze
    if page > total_pages:
        page = 1

    start = (page - 1) * per_page
    end = start + per_page

    visible_articles = filtered_rows[start:end]

    return (
        [article_card(article) for article in visible_articles],
        total_pages,
        {"display": "none" if total_pages == 1 else "block"},
    )


@callback(Output("articles-pagination", "value"), Input("search-input", "value"), prevent_initial_call=True)
def reset_page(_):
    return 1
