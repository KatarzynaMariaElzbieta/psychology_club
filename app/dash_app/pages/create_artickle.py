import base64
import os
import uuid
from datetime import datetime

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask import current_app, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.dash_app.src import normalize_google_form_embed, require_roles, url_for_uploads
from app.models import Article, Image, Tag, User

dash.register_page(__name__, path="/nowy_artykul", name="Nowy artykuł")


def get_upload_folder():
    return current_app.config["UPLOAD_FOLDER"]


# @require_roles("editor", redirect_to="/no-access")
@require_roles("autor")
def serve_layout():
    users = User.query.order_by(User.username.asc().nullslast(), User.email.asc()).all()
    author_options = [{"value": str(user.id), "label": user.username or user.email} for user in users]
    current_user_id = str(current_user.id) if current_user.is_authenticated else None
    return dmc.Container(
        [
            dmc.MultiSelect(
                label="Autorzy",
                placeholder="Wybierz autorów artykułu",
                id="article-authors-input",
                data=author_options,
                value=[current_user_id] if current_user_id else [],
                searchable=True,
                clearable=True,
                mb=20,
            ),
            dmc.TextInput(
                label="Tytuł artykułu",
                placeholder="Wpisz tytuł",
                id="article-title-input",
                required=True,
            ),
            dmc.TextInput(
                label="Skrócona wersja do podglądu",
                placeholder="Wpisz krótki opis artykułu (do 255 znaków)",
                id="article-short-input",
                required=True,
            ),
            dmc.RichTextEditor(
                id="article-editor",
                html="",
                mih=300,
                mb=20,
                toolbar={
                    "sticky": True,
                    "controlsGroups": [
                        [
                            {
                                "CustomControl": {
                                    "ariaLabel": "Wstaw tabelę",
                                    "title": "Wstaw tabelę",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-plus",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {
                                        "function": "rteInsertTable",
                                        "options": {
                                            "table": {
                                                "rows": 3,
                                                "cols": 3,
                                                "withHeaderRow": True,
                                            }
                                        },
                                    },
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Dodaj wiersz powyżej",
                                    "title": "Dodaj wiersz powyżej",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-row-plus-before",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteAddRowBefore"},
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Dodaj wiersz poniżej",
                                    "title": "Dodaj wiersz poniżej",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-row-plus-after",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteAddRowAfter"},
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Usuń wiersz",
                                    "title": "Usuń wiersz",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-row-remove",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteDeleteRow"},
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Dodaj kolumnę po lewej",
                                    "title": "Dodaj kolumnę po lewej",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-column-plus-before",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteAddColumnBefore"},
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Dodaj kolumnę po prawej",
                                    "title": "Dodaj kolumnę po prawej",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-column-plus-after",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteAddColumnAfter"},
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Usuń kolumnę",
                                    "title": "Usuń kolumnę",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-column-remove",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteDeleteColumn"},
                                }
                            },
                            {
                                "CustomControl": {
                                    "ariaLabel": "Usuń tabelę",
                                    "title": "Usuń tabelę",
                                    "children": [
                                        DashIconify(
                                            icon="mdi:table-remove",
                                            width=18,
                                            height=18,
                                        )
                                    ],
                                    "onClick": {"function": "rteDeleteTable"},
                                }
                            },
                        ],
                        ["Bold", "Italic", "Underline", "Code"],
                        ["H1", "H2", "H3", "H4", "H5", "H6"],
                        ["Strikethrough", "ClearFormatting", "Blockquote"],
                        ["BulletList", "OrderedList"],
                        ["Link", "Unlink"],
                        ["AlignLeft", "AlignCenter", "AlignJustify", "AlignRight"],
                        ["Undo", "Redo"],
                    ],
                },
            ),
            dmc.Textarea(
                label="Google Form (opcjonalnie)",
                placeholder="Wklej link osadzenia lub cały kod iframe z Google Forms",
                id="article-google-form-input",
                autosize=True,
                minRows=2,
                mb=20,
            ),
            dmc.Stack(
                [
                    dmc.Text("Data zamknięcia formularza (opcjonalnie)", size="sm", fw=500),
                    dcc.Input(
                        id="article-form-close-date-input",
                        type="date",
                        style={"width": "100%", "padding": "0.5rem"},
                    ),
                ],
                gap=6,
                mb=20,
            ),
            # 🔹 Upload sekcja
            dcc.Upload(
                id="upload-image",
                children=dmc.Button("📷 Dodaj obraz", variant="light", size="xs"),
                multiple=False,
                accept="image/*",
            ),
            html.Div(id="uploaded-images-preview", style={"marginTop": "1rem"}),  # <– miniatury
            dcc.Store(id="main-image-store"),  # <– zapamiętuje główny obraz
            dmc.TagsInput(
                label="Tagi",
                placeholder="Dodaj tagi",
                id="framework-tags-input",
                value=["psychologia", "relacje"],
                mb=20,
            ),
            dmc.Button("💾 Zapisz artykuł", id="save-article-btn", color="teal"),
        ],
        size="lg",
        p="xl",
    )


layout = serve_layout
# ========================
# ZAPIS ARTYKUŁU
# ========================
@callback(
    Output("save-article-btn", "children"),
    Input("save-article-btn", "n_clicks"),
    State("article-title-input", "value"),
    State("article-short-input", "value"),
    State("article-editor", "html"),
    State("article-google-form-input", "value"),
    State("article-form-close-date-input", "value"),
    State("framework-tags-input", "value"),
    State("article-authors-input", "value"),
    State("main-image-store", "data"),
    State("uploaded-images-preview", "children"),
    prevent_initial_call=True,
)
def save_article(
    n_clicks, title, short_content, content, google_form_raw, form_close_date_raw, tags, authors, main_image, previews
):
    if not title or not content:
        return "⚠️ Uzupełnij wszystkie pola!"
    if not authors:
        return "⚠️ Wybierz co najmniej jednego autora!"

    google_form_url = normalize_google_form_embed(google_form_raw)
    if google_form_raw and not google_form_url:
        return "⚠️ Dozwolone są tylko osadzenia Google Forms z docs.google.com/forms"
    form_close_date = None
    if form_close_date_raw:
        try:
            form_close_date = datetime.strptime(form_close_date_raw, "%Y-%m-%d").date()
        except ValueError:
            return "⚠️ Niepoprawny format daty zamknięcia formularza"

    # --- Utwórz nowy artykuł ---
    article = Article(
        title=title.strip(),
        content=content,
        short_content=short_content,
        google_form_url=google_form_url,
        form_closes_at=form_close_date,
    )
    author_ids = []
    for author_id in authors:
        try:
            author_ids.append(int(author_id))
        except (TypeError, ValueError):
            continue
    if not author_ids:
        return "⚠️ Wybierz poprawnych autorów!"
    article.authors = User.query.filter(User.id.in_(author_ids)).all()

    # --- Tagi ---
    tag_objects = []
    for tag_name in tags or []:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tag_objects.append(tag)
    article.tags = tag_objects

    # --- Obrazy ---
    uploaded_urls = []
    for thumb in previews or []:
        img_src = thumb["props"]["children"][0]["props"]["src"]
        rel_path = img_src.replace("/media" + "/", "")
        img = Image(file_path=rel_path, is_main=(main_image in img_src))
        article.images.append(img)
        uploaded_urls.append(img_src)

    # --- Zapis do bazy ---
    db.session.add(article)
    db.session.commit()

    return "✅ Artykuł zapisano!"


# ========================
# UPLOAD OBRAZÓW
# ========================
@callback(
    Output("uploaded-images-preview", "children", allow_duplicate=True),
    Output("article-editor", "html", allow_duplicate=True),
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    State("uploaded-images-preview", "children"),
    State("article-editor", "html"),
    prevent_initial_call=True,
)
def upload_image(contents, filename, current_preview, editor_content):
    """Zapisuje obraz i dodaje miniaturę do listy."""
    if not contents:
        raise PreventUpdate
    if not contents:
        return editor_content or ""

    data = contents.split(",", 1)[1]
    img_bytes = base64.b64decode(data)

    upload_folder = get_upload_folder()
    name, ext = os.path.splitext(filename)
    safe_name = secure_filename(f"{uuid.uuid4().hex}{ext}")
    save_path = os.path.join(upload_folder, safe_name)

    with open(save_path, "wb") as f:
        f.write(img_bytes)

    img_url = url_for_uploads(safe_name)
    new_content = (editor_content or "") + f'<p ><img src="{img_url}" style="max-width:700px;"></p>'

    # Miniatura + przycisk „ustaw jako główny”
    thumb = dmc.Paper(
        [
            html.Img(src=img_url, style={"width": "150px", "borderRadius": "8px"}),
            dmc.Button(
                "⭐ Ustaw jako główny",
                id={"type": "set-main-btn", "index": safe_name},
                color="yellow",
                fullWidth=True,
                mt=5,
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        p="sm",
        style={"display": "inline-block", "marginRight": "10px"},
    )

    return (current_preview or []) + [thumb], new_content


# ========================
# WYBÓR GŁÓWNEGO OBRAZU
# ========================
@callback(
    Output("main-image-store", "data"),
    Output("uploaded-images-preview", "children"),
    Input({"type": "set-main-btn", "index": dash.ALL}, "n_clicks"),
    State({"type": "set-main-btn", "index": dash.ALL}, "id"),
    State("uploaded-images-preview", "children"),
    prevent_initial_call=True,
)
def set_main_image(n_clicks, btn_ids, previews):
    if not n_clicks or all(v is None for v in n_clicks):
        raise PreventUpdate

    # 🔹 znajdź kliknięty przycisk
    clicked_idx = [i for i, v in enumerate(n_clicks) if v][0]
    selected = btn_ids[clicked_idx]["index"]

    # 🔹 przebuduj podgląd (zachowując strukturę, ale od nowa)
    updated_previews = []
    for thumb in previews:
        img_src = thumb["props"]["children"][0]["props"]["src"]
        fname = os.path.basename(img_src)
        is_main = fname == selected

        border_color = "gold" if is_main else "transparent"
        btn_label = "🌟 Główny obraz" if is_main else "⭐ Ustaw jako główny"
        btn_color = "yellow" if is_main else "gray"

        # 🔸 Tworzymy nowy Paper — nie modyfikujemy istniejącego
        new_thumb = dmc.Paper(
            [
                html.Img(
                    src=img_src,
                    style={
                        "width": "150px",
                        "borderRadius": "8px",
                        "border": f"3px solid {border_color}",
                    },
                ),
                dmc.Button(
                    btn_label,
                    id={"type": "set-main-btn", "index": fname},
                    color=btn_color,
                    fullWidth=True,
                    mt=5,
                    variant="light",
                    size="xs",
                ),
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            p="sm",
            style={"display": "inline-block", "marginRight": "10px"},
        )

        updated_previews.append(new_thumb)

    return selected, updated_previews
