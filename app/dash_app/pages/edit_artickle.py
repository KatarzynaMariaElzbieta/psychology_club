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
from app.dash_app.src import normalize_google_form_embed, require_admin_or_author, url_for_uploads
from app.models import Article, Image, Tag, User

dash.register_page(__name__, path_template="/edytuj_artykul/<id>")


layout = html.Div(
    [
        dmc.Container(
            [
                dmc.MultiSelect(
                    label="Autorzy",
                    placeholder="Wybierz autorów artykułu",
                    id="article-authors-input",
                    data=[],
                    value=[],
                    searchable=True,
                    clearable=True,
                    mb=20,
                ),
                dmc.TextInput(
                    label="Tytuł artykułu",
                    placeholder="Wpisz tytuł",
                    id="article-title-input",
                    value="",
                    required=True,
                ),
                dmc.TextInput(
                    label="Skrócona wersja do podglądu",
                    placeholder="Wpisz krótki opis artykułu (do 255 znaków)",
                    id="article-short-input",
                    value="",
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
                dcc.Upload(
                    id="upload-image_edit",
                    children=dmc.Button("📷 Dodaj obraz", variant="light", size="xs"),
                    multiple=False,
                    accept="image/*",
                ),
                html.Div(id="uploaded-images_", children=[], style={"marginTop": "1rem"}),
                dcc.Store(id="main-image-store_edit", data=""),
                dmc.TagsInput(
                    label="Tagi",
                    placeholder="Dodaj tagi",
                    id="framework-tags-input",
                    value=[],
                    mb=20,
                ),
                dmc.Button("💾 Zapisz zmiany", id="save-article-btn_edit", color="teal"),
                dcc.Store(id="article-id-store", data=""),
            ],
            size="lg",
            p="xl",
        )
    ],
    id="edit-article-content",
    style={"display": "none"},
)


@require_admin_or_author(raise_on_fail=True)
def serve_edit_layout(article_id):
    article = Article.query.get_or_404(article_id)
    users = User.query.order_by(User.username.asc().nullslast(), User.email.asc()).all()
    author_options = [{"value": str(user.id), "label": user.username or user.email} for user in users]
    selected_authors = [str(author.id) for author in article.authors]

    # Miniatury obrazów
    previews = []
    main_image = None
    for img in article.images:

        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], img.file_path)
        if not os.path.exists(file_path):
            img_url = url_for_uploads("8a57a97cab424295a53e1f133c823e2d.jpg")
        else:
            img_url = url_for_uploads(img.file_path)
        border_color = "gold" if img.is_main else "transparent"
        btn_label = "🌟 Główny obraz" if img.is_main else "⭐ Ustaw jako główny"
        btn_color = "yellow" if img.is_main else "gray"
        if img.is_main:
            main_image = os.path.basename(img.file_path)

        thumb = dmc.Paper(
            [
                html.Img(
                    src=img_url,
                    style={
                        "width": "150px",
                        "borderRadius": "8px",
                        "border": f"3px solid {border_color}",
                    },
                ),
                dmc.Button(
                    btn_label,
                    id={"type": "set-main-btn", "index": os.path.basename(img.file_path)},
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
        previews.append(thumb)

    return (
        author_options,
        selected_authors,
        article.title,
        article.short_content,
        article.content,
        article.google_form_url,
        article.form_closes_at.isoformat() if article.form_closes_at else None,
        [tag.name for tag in article.tags],
        previews,
        article.id,
        main_image,
        {"display": "block"},
    )


@callback(
    Output("article-authors-input", "data"),
    Output("article-authors-input", "value"),
    Output("article-title-input", "value"),
    Output("article-short-input", "value"),
    Output("article-editor", "html", allow_duplicate=True),
    Output("article-google-form-input", "value"),
    Output("article-form-close-date-input", "value"),
    Output("framework-tags-input", "value"),
    Output("uploaded-images_", "children", allow_duplicate=True),
    Output("article-id-store", "data"),
    Output("main-image-store_edit", "data", allow_duplicate=True),
    Output("edit-article-content", "style", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call="initial_duplicate",
)
def load_article_for_edit(pathname):
    try:
        article_id = int(pathname.split("/")[-1])
    except (ValueError, IndexError):
        return (
            [],
            [],
            "Nieprawidłowy adres artykułu",
            None,
            "",
            None,
            None,
            [],
            [],
            None,
            None,
            {"display": "block"},
        )
    result = serve_edit_layout(article_id)
    return result


# ========================
# ZAPIS EDYCJI ARTYKUŁU
# ========================
@callback(
    Output("save-article-btn_edit", "children"),
    Input("save-article-btn_edit", "n_clicks"),
    State("article-authors-input", "value"),
    State("article-title-input", "value"),
    State("article-short-input", "value"),
    State("article-editor", "html"),
    State("article-google-form-input", "value"),
    State("article-form-close-date-input", "value"),
    State("framework-tags-input", "value"),
    State("main-image-store_edit", "data"),
    State("uploaded-images_", "children"),
    State("article-id-store", "data"),
    # prevent_initial_call=True,
)
@require_admin_or_author(
    article_id_getter=lambda n_clicks, authors, title, short_content, content, google_form_raw, form_close_date_raw, tags, main_image, previews, article_id: article_id,
    raise_on_fail=True,
)
def save_article_edit(
    n_clicks,
    authors,
    title,
    short_content,
    content,
    google_form_raw,
    form_close_date_raw,
    tags,
    main_image,
    previews,
    article_id,
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

    author_ids = []
    for author_id in authors:
        try:
            author_ids.append(int(author_id))
        except (TypeError, ValueError):
            continue
    if not author_ids:
        return "⚠️ Wybierz poprawnych autorów!"

    article = Article.query.get_or_404(article_id)
    article.title = title.strip()
    article.short_content = short_content
    article.content = content
    article.google_form_url = google_form_url
    article.form_closes_at = form_close_date
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
    article.images = []  # opcjonalnie wyczyść stare obrazy
    uploaded_urls = []
    for thumb in previews or []:
        img_src = thumb["props"]["children"][0]["props"]["src"]
        rel_path = img_src.replace("/media" + "/", "")
        img = Image(file_path=rel_path, is_main=(main_image in img_src))
        article.images.append(img)
        uploaded_urls.append(img_src)

    db.session.commit()
    return "✅ Artykuł zaktualizowany!"


# ========================
# UPLOAD OBRAZÓW
# ========================
@callback(
    Output("uploaded-images_", "children", allow_duplicate=True),
    Output("article-editor", "html", allow_duplicate=True),
    Input("upload-image_edit", "contents"),
    State("upload-image_edit", "filename"),
    State("uploaded-images_", "children"),
    State("article-editor", "html"),
    prevent_initial_call="initial_duplicate",
)
def upload_image(contents, filename, current_preview, editor_content):
    if not contents:
        raise PreventUpdate
    if not contents:
        return editor_content or ""

    data = contents.split(",", 1)[1]
    img_bytes = base64.b64decode(data)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    name, ext = os.path.splitext(filename)
    safe_name = secure_filename(f"{uuid.uuid4().hex}{ext}")
    save_path = os.path.join(upload_folder, safe_name)

    with open(save_path, "wb") as f:
        f.write(img_bytes)

    img_url = url_for_uploads(safe_name)
    new_content = (editor_content or "") + f'<p><img src="{img_url}" style="max-width:700px;"></p>'

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
    Output("main-image-store_edit", "data", allow_duplicate=True),
    Output("uploaded-images_", "children", allow_duplicate=True),
    Input({"type": "set-main-btn", "index": dash.ALL}, "n_clicks"),
    State({"type": "set-main-btn", "index": dash.ALL}, "id"),
    State("uploaded-images_", "children"),
    prevent_initial_call="initial_duplicate",
)
def set_main_image(n_clicks, btn_ids, previews):
    if not n_clicks or all(v is None for v in n_clicks):
        raise PreventUpdate

    clicked_idx = [i for i, v in enumerate(n_clicks) if v][0]
    selected = btn_ids[clicked_idx]["index"]

    updated_previews = []
    for thumb in previews:
        img_src = thumb["props"]["children"][0]["props"]["src"]
        fname = os.path.basename(img_src)
        is_main = fname == selected

        border_color = "gold" if is_main else "transparent"
        btn_label = "🌟 Główny obraz" if is_main else "⭐ Ustaw jako główny"
        btn_color = "yellow" if is_main else "gray"

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
