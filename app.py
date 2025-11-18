import importlib
import os
import re
from pathlib import Path
from flask import Flask, jsonify, render_template, request
import monitoramento  # usa o módulo existente

BASE_DIR = Path(__file__).parent
app = Flask(__name__, template_folder="templates", static_folder="static")
MONITORAMENTO_PATH = BASE_DIR / "monitoramento.py"
ENV_PATH = BASE_DIR / ".env"


def load_env_file():
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def update_env_file(values: dict[str, str]):
    existing_lines = []
    if ENV_PATH.exists():
        existing_lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    updated_lines: list[str] = []
    handled_keys = set()

    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            updated_lines.append(line)
            continue

        key, _ = stripped.split("=", 1)
        key = key.strip()
        if key in values:
            updated_lines.append(f"{key}={values[key]}")
            handled_keys.add(key)
        else:
            updated_lines.append(line)

    for key, value in values.items():
        if key not in handled_keys:
            updated_lines.append(f"{key}={value}")

    updated_text = "\n".join(updated_lines).strip()
    ENV_PATH.write_text((updated_text + "\n") if updated_text else "", encoding="utf-8")


load_env_file()

def load_sites():
    importlib.reload(monitoramento)
    return monitoramento.SITES


def persist_sites(sites):
    text = MONITORAMENTO_PATH.read_text(encoding="utf-8")
    new_body = ",\n    ".join(f'"{url}"' for url in sites)
    text = re.sub(
        r"SITES\s*=\s*\[(?:.|\n)*?\]",
        f'SITES = [\n    {new_body}\n]',
        text,
        count=1,
    )
    MONITORAMENTO_PATH.write_text(text, encoding="utf-8")
    importlib.reload(monitoramento)


def load_user():
    return {
        "name": os.getenv("APP_USER_NAME", "Usuário"),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "NÃO CONFIGURADO"),
    }


def persist_user(name: str, chat_id: str):
    os.environ["APP_USER_NAME"] = name
    os.environ["TELEGRAM_CHAT_ID"] = chat_id
    update_env_file({"APP_USER_NAME": name, "TELEGRAM_CHAT_ID": chat_id})


@app.route("/")
def index():
    return render_template(
        "index.html",
        user=load_user(),
        sites_count=len(load_sites()),
    )


@app.get("/api/sites")
def api_list_sites():
    return jsonify(load_sites())


@app.post("/api/sites")
def api_add_site():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    if not url:
        return {"error": "URL obrigatória"}, 400
    sites = load_sites()
    if url in sites:
        return {"error": "URL já cadastrada"}, 409
    sites.insert(0, url)
    persist_sites(sites)
    return {"success": True, "sites": sites}


@app.delete("/api/sites")
def api_remove_site():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    sites = load_sites()
    if url not in sites:
        return {"error": "URL inexistente"}, 404
    sites.remove(url)
    persist_sites(sites)
    return {"success": True, "sites": sites}


@app.get("/api/user")
def api_get_user():
    return jsonify(load_user())


@app.post("/api/user")
def api_update_user():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    chat_id = data.get("chat_id", "").strip()

    if not name or not chat_id:
        return {"error": "Nome e Chat ID são obrigatórios."}, 400

    persist_user(name, chat_id)
    return {"success": True, "user": load_user()}


if __name__ == "__main__":
    app.run(debug=True)