import base64
import os
import uuid

from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

import dash
from dash import html, Input, Output, State, callback, dcc
import dash_mantine_components as dmc
from flask import current_app, url_for
from dash.exceptions import PreventUpdate

from app import db
from app.models import Image, Tag, Article


dash.register_page(__name__, path="/nowy_artykul", name="Nowy artykuł")


def get_upload_folder():
    folder = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(folder, exist_ok=True)
    return folder


# @require_roles("editor", redirect_to="/no-access")
@login_required
def serve_layout():
    return dmc.Container(
    [
        dmc.TextInput(
            label="Tytuł artykułu",
            placeholder="Wpisz tytuł",
            id="article-title-input",
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
                    ["Bold", "Italic", "Underline", "Code"],
                    ["H1", "H2", "H3"],
                    ["BulletList", "OrderedList"],
                    ["Link", "Unlink"],
                    ["Undo", "Redo"],
                ],
            },
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
    State("article-editor", "html"),
    State("framework-tags-input", "value"),
    State("main-image-store", "data"),
    State("uploaded-images-preview", "children"),
    prevent_initial_call=True,
)
def save_article(n_clicks, title, content, tags, main_image, previews):
    if not title or not content:
        return "⚠️ Uzupełnij wszystkie pola!"

    # --- Utwórz nowy artykuł ---
    article = Article(title=title.strip(), content=content)
    article.authors.append(current_user)

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
        rel_path = img_src.replace(current_app.static_url_path + "/", "")
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

    img_url = url_for("static", filename=f"uploads/{safe_name}")
    new_content = (editor_content or "") + f'<p><img src="{img_url}" style="max-width:700px;"></p>'


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
