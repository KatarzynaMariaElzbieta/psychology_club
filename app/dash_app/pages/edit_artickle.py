import base64
import os
import uuid

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
from flask import current_app, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.dash_app.src import url_for_uploads
from app.models import Article, Image, Tag


dash.register_page(__name__, path_template='/edytuj_artykul/<id>')
layout = html.Div(
    [
dmc.Container(
        [
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
            ),
            dcc.Upload(
                id="upload-image",
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
            dmc.Button("💾 Zapisz zmiany", id="save-article-btn", color="teal"),
            dcc.Store(id="article-id-store", data=""),
        ],
        size="lg",
        p="xl",
    )
    ],
    id="edit-article-content")


# @login_required
def serve_edit_layout(article_id):
    print(f"{article_id=}")
    article = Article.query.get_or_404(article_id)

    # Miniatury obrazów
    previews = []
    main_image = None
    for img in article.images:

        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], img.file_path)
        print(file_path)
        if not os.path.exists(file_path):
            print(f"Brak pliku fizycznego: {file_path}, używam placeholdera")
            img_url = url_for_uploads("8a57a97cab424295a53e1f133c823e2d.jpg")
        else:
            img_url = url_for_uploads(img.file_path)
        print(f"{img_url=}")
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
    print(previews)

    return (
        article.title,
        article.short_content,
        article.content,
        [tag.name for tag in article.tags],
        previews,
        article.id,
        main_image
    )

@callback(
    Output("article-title-input", "value"),
    Output("article-short-input", "value"),
    Output("article-editor", "html"),
    Output("framework-tags-input", "value"),
    Output("uploaded-images_", "children"),
    Output("article-id-store", "data"),
    Output("main-image-store_edit", "data"),
    Input("url", "pathname"),

)
def load_article_for_edit(pathname):
    try:
        article_id = int(pathname.split("/")[-1])
    except (ValueError, IndexError):
        return dmc.Text("Nieprawidłowy adres artykułu")
    result = serve_edit_layout(article_id)
    print(result)
    return result


# # ========================
# # ZAPIS EDYCJI ARTYKUŁU
# # ========================
# @callback(
#     Output("save-article-btn", "children"),
#     Input("save-article-btn", "n_clicks"),
#     State("article-title-input", "value"),
#     State("article-short-input", "value"),
#     State("article-editor", "html"),
#     State("framework-tags-input", "value"),
#     State("main-image-store", "data"),
#     State("uploaded-images_", "children"),
#     State("article-id-store", "data"),
#     prevent_initial_call=True,
# )
# def save_article_edit(n_clicks, title, short_content, content, tags, main_image, previews, article_id):
#     if not title or not content:
#         return "⚠️ Uzupełnij wszystkie pola!"
#
#     article = Article.query.get_or_404(article_id)
#     article.title = title.strip()
#     article.short_content = short_content
#     article.content = content
#
#     # --- Tagi ---
#     tag_objects = []
#     for tag_name in tags or []:
#         tag = Tag.query.filter_by(name=tag_name).first()
#         if not tag:
#             tag = Tag(name=tag_name)
#             db.session.add(tag)
#         tag_objects.append(tag)
#     article.tags = tag_objects
#
#     # --- Obrazy ---
#     article.images = []  # opcjonalnie wyczyść stare obrazy
#     uploaded_urls = []
#     for thumb in previews or []:
#         img_src = thumb["props"]["children"][0]["props"]["src"]
#         rel_path = img_src.replace(current_app.static_url_path + "/", "")
#         img = Image(file_path=rel_path, is_main=(main_image in img_src))
#         article.images.append(img)
#         uploaded_urls.append(img_src)
#
#     db.session.commit()
#     return "✅ Artykuł zaktualizowany!"


# ========================
# UPLOAD OBRAZÓW
# ========================
# @callback(
#     Output("output_div", "children"),
    # Output("uploaded-images_", "children", allow_duplicate=True),
    # Output("article-editor_edit", "html", allow_duplicate=True),
    # Input("input_button", "n_clicks"),
    # Input("upload-image_edit", "contents"),
    # State("upload-image_edit", "filename"),
    # State("uploaded-images_", "children"),
    # State("article-editor_edit", "html"),
    # prevent_initial_call="initial_duplicate",
# )
# def verify_callback(n_click):
#     print(f"{n_click=}")
#     print("output")
    # print(f"{contents=}")
    # print(f"{children=}")
    # print(f"{html=}")
    # return "children", "html"
# def upload_image(contents, filename, current_preview, editor_content):
#     if not contents:
#         raise PreventUpdate
#
#     data = contents.split(",", 1)[1]
#     img_bytes = base64.b64decode(data)
#
#     upload_folder = get_upload_folder()
#     name, ext = os.path.splitext(filename)
#     safe_name = secure_filename(f"{uuid.uuid4().hex}{ext}")
#     save_path = os.path.join(upload_folder, safe_name)
#
#     with open(save_path, "wb") as f:
#         f.write(img_bytes)
#
#     img_url = url_for("static", filename=f"uploads/{safe_name}")
#     new_content = (editor_content or "") + f'<p><img src="{img_url}" style="max-width:700px;"></p>'
#
#     thumb = dmc.Paper(
#         [
#             html.Img(src=img_url, style={"width": "150px", "borderRadius": "8px"}),
#             dmc.Button(
#                 "⭐ Ustaw jako główny",
#                 id={"type": "set-main-btn", "index": safe_name},
#                 color="yellow",
#                 fullWidth=True,
#                 mt=5,
#             ),
#         ],
#         withBorder=True,
#         shadow="sm",
#         radius="md",
#         p="sm",
#         style={"display": "inline-block", "marginRight": "10px"},
#     )
#
#     return (current_preview or []) + [thumb], new_content


# ========================
# WYBÓR GŁÓWNEGO OBRAZU
# ========================
# @callback(
#     Output("main-image-store", "data"),
#     Output("uploaded-images_", "children"),
#     Input({"type": "set-main-btn", "index": dash.ALL}, "n_clicks"),
#     State({"type": "set-main-btn", "index": dash.ALL}, "id"),
#     State("uploaded-images_", "children"),
#     prevent_initial_call=True,
# )
# def set_main_image(n_clicks, btn_ids, previews):
#     if not n_clicks or all(v is None for v in n_clicks):
#         raise PreventUpdate
#
#     clicked_idx = [i for i, v in enumerate(n_clicks) if v][0]
#     selected = btn_ids[clicked_idx]["index"]
#
#     updated_previews = []
#     for thumb in previews:
#         img_src = thumb["props"]["children"][0]["props"]["src"]
#         fname = os.path.basename(img_src)
#         is_main = fname == selected
#
#         border_color = "gold" if is_main else "transparent"
#         btn_label = "🌟 Główny obraz" if is_main else "⭐ Ustaw jako główny"
#         btn_color = "yellow" if is_main else "gray"
#
#         new_thumb = dmc.Paper(
#             [
#                 html.Img(
#                     src=img_src,
#                     style={
#                         "width": "150px",
#                         "borderRadius": "8px",
#                         "border": f"3px solid {border_color}",
#                     },
#                 ),
#                 dmc.Button(
#                     btn_label,
#                     id={"type": "set-main-btn", "index": fname},
#                     color=btn_color,
#                     fullWidth=True,
#                     mt=5,
#                     variant="light",
#                     size="xs",
#                 ),
#             ],
#             withBorder=True,
#             shadow="sm",
#             radius="md",
#             p="sm",
#             style={"display": "inline-block", "marginRight": "10px"},
#         )
#         updated_previews.append(new_thumb)
#
#     return selected, updated_previews
