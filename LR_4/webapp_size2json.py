import base64
import io
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_file
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
APP_FILE = Path(__file__).resolve()

AUTHOR_LOGIN = "1154880"
last_upload = {
    "filename": None,
    "width": None,
    "height": None,
    "thumbnail_data_url": None,
}

INDEX_TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PNG size2json</title>
  <style>
    :root {
      --bg: #f2efe8;
      --panel: rgba(255, 252, 246, 0.92);
      --ink: #1f2a2e;
      --muted: #5b6669;
      --accent: #c65f38;
      --accent-dark: #8d3f23;
      --line: rgba(31, 42, 46, 0.12);
      --shadow: 0 24px 60px rgba(63, 47, 33, 0.16);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(198, 95, 56, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(57, 130, 120, 0.14), transparent 34%),
        linear-gradient(135deg, #ece5d8, #f6f3ed 55%, #ebe5dc);
      display: grid;
      place-items: center;
      padding: 24px;
    }

    .shell {
      width: min(980px, 100%);
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
    }

    .card {
      background: var(--panel);
      backdrop-filter: blur(12px);
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: var(--shadow);
      padding: 28px;
    }

    h1, h2, p { margin: 0; }

    h1 {
      font-size: clamp(2.2rem, 4vw, 3.6rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
      margin-bottom: 18px;
    }

    .lead {
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.6;
      max-width: 50ch;
      margin-bottom: 26px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      padding: 8px 14px;
      background: rgba(198, 95, 56, 0.1);
      color: var(--accent-dark);
      margin-bottom: 18px;
      font-size: 0.92rem;
    }

    form {
      display: grid;
      gap: 14px;
    }

    .upload {
      border: 1.5px dashed rgba(31, 42, 46, 0.24);
      border-radius: 22px;
      padding: 22px;
      background: rgba(255, 255, 255, 0.68);
    }

    input[type="file"] {
      width: 100%;
      font: inherit;
      color: var(--ink);
    }

    button {
      border: 0;
      border-radius: 16px;
      background: linear-gradient(135deg, var(--accent), #d17a34);
      color: white;
      padding: 14px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.18s ease, box-shadow 0.18s ease;
      box-shadow: 0 10px 22px rgba(198, 95, 56, 0.26);
    }

    button:hover {
      transform: translateY(-1px);
    }

    .meta {
      display: grid;
      gap: 12px;
      color: var(--muted);
      font-size: 0.95rem;
      margin-top: 18px;
    }

    .result {
      min-height: 96px;
      border-radius: 20px;
      background: #fff;
      border: 1px solid var(--line);
      padding: 18px;
      font-family: "SFMono-Regular", "Menlo", monospace;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .preview {
      margin-top: 16px;
      min-height: 180px;
      display: grid;
      place-items: center;
      border-radius: 24px;
      background:
        linear-gradient(45deg, rgba(31, 42, 46, 0.04) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(31, 42, 46, 0.04) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(31, 42, 46, 0.04) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(31, 42, 46, 0.04) 75%);
      background-size: 24px 24px;
      background-position: 0 0, 0 12px, 12px -12px, -12px 0;
      overflow: hidden;
    }

    .preview img {
      max-width: 100%;
      max-height: 320px;
      display: block;
      border-radius: 16px;
    }

    .empty {
      color: var(--muted);
      text-align: center;
      padding: 24px;
      line-height: 1.5;
    }

    @media (max-width: 820px) {
      .shell {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="card">
      <div class="badge">Flask • async upload • PNG only</div>
      <h1>size2json</h1>
      <p class="lead">Форма отправляет PNG по маршруту <code>/size2json</code> без перезагрузки страницы и показывает размер изображения, а сервер хранит сведения о последней успешной загрузке.</p>

      <form id="upload-form">
        <label class="upload">
          <strong>Поле формы: image</strong>
          <p class="meta">Принимается только PNG. Для не-PNG сервер вернёт JSON <code>{"result":"invalid filetype"}</code>.</p>
          <input id="image-input" type="file" name="image" accept="image/png">
        </label>
        <button type="submit">Отправить на сервер</button>
      </form>

      <div class="meta">
        <span>Логин: <code>{{ author }}</code></span>
        <span>Маршрут состояния: <code>/last-upload</code></span>
      </div>
    </section>

    <aside class="card">
      <h2>Ответ сервера</h2>
      <div id="result" class="result">Ожидание запроса...</div>
      <div id="preview" class="preview">
        <div class="empty">После успешной отправки здесь появится thumbnail последнего PNG.</div>
      </div>
    </aside>
  </main>

  <script>
    const form = document.getElementById("upload-form");
    const resultBox = document.getElementById("result");
    const previewBox = document.getElementById("preview");

    async function refreshLastUpload() {
      const response = await fetch("/last-upload");
      const data = await response.json();

      if (!data.filename) {
        previewBox.innerHTML = '<div class="empty">Последняя успешная загрузка пока отсутствует.</div>';
        return;
      }

      previewBox.innerHTML = '<img alt="Последняя загрузка" src="' + data.thumbnail_data_url + '">';
      resultBox.textContent = JSON.stringify({
        width: data.width,
        height: data.height,
        filename: data.filename
      }, null, 2);
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const fileInput = document.getElementById("image-input");
      if (!fileInput.files.length) {
        resultBox.textContent = JSON.stringify({ result: "select a file" }, null, 2);
        return;
      }

      const formData = new FormData();
      formData.append("image", fileInput.files[0]);

      resultBox.textContent = "Загрузка...";

      const response = await fetch("/size2json", {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      resultBox.textContent = JSON.stringify(data, null, 2);

      if (response.ok && data.width && data.height) {
        await refreshLastUpload();
      }
    });

    refreshLastUpload();
  </script>
</body>
</html>
"""


def png_thumbnail_data_url(raw_bytes):
    with Image.open(io.BytesIO(raw_bytes)) as image:
        thumbnail = image.copy()
        thumbnail.thumbnail((320, 320))
        buffer = io.BytesIO()
        thumbnail.save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


@app.get("/")
def index():
    return render_template_string(INDEX_TEMPLATE, author=AUTHOR_LOGIN)


@app.get("/login")
def login():
    return jsonify({"author": AUTHOR_LOGIN})


@app.get("/last-upload")
def get_last_upload():
    return jsonify(last_upload)


@app.get("/repo")
def repo():
    return jsonify(
        {
            "author": AUTHOR_LOGIN,
            "source_file": "/source/webapp_size2json.py",
            "download": "/source/archive",
        }
    )


@app.get("/source/webapp_size2json.py")
def source_file():
    return send_file(APP_FILE, mimetype="text/x-python; charset=utf-8")


@app.get("/source/archive")
def source_archive():
    buffer = io.BytesIO()
    source_bytes = APP_FILE.read_bytes()

    import zipfile

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("webapp_size2json.py", source_bytes)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="size2json_solution.zip",
    )


@app.post("/size2json")
def size2json():
    upload = request.files.get("image")
    if upload is None or upload.filename == "":
        return jsonify({"result": "invalid filetype"})

    raw_bytes = upload.read()
    if not raw_bytes:
        return jsonify({"result": "invalid filetype"})

    try:
        with Image.open(io.BytesIO(raw_bytes)) as image:
            if image.format != "PNG":
                return jsonify({"result": "invalid filetype"})
            width, height = image.size
    except UnidentifiedImageError:
        return jsonify({"result": "invalid filetype"})

    last_upload["filename"] = upload.filename
    last_upload["width"] = width
    last_upload["height"] = height
    last_upload["thumbnail_data_url"] = png_thumbnail_data_url(raw_bytes)

    return jsonify({"width": width, "height": height})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
