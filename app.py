import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request
import monitoramento  # usa o módulo existente

BASE_DIR = Path(__file__).parent
app = Flask(__name__, template_folder="templates", static_folder="static")
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


load_env_file()


def load_sites():
    # Sempre carrega a lista atualizada a partir do arquivo JSON
    return monitoramento.load_sites_from_json()


def persist_sites(sites):
    # Persiste a lista de sites diretamente no arquivo JSON usado por monitoramento.py
    monitoramento.save_sites_to_json(sites)


@app.route("/")
def index():
    return render_template(
        "index.html",
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


if __name__ == "__main__":
    app.run(debug=True)