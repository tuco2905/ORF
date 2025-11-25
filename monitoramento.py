import os
import sys
import time
import hashlib
import logging
import requests
import re
from urllib.parse import urlparse
from pathlib import Path
from typing import List
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# Função para carregar variáveis do arquivo .env
def load_env_file():
    """Carrega variáveis do arquivo .env para o os.environ, se existir."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

# Carrega as variáveis de ambiente
load_env_file()

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _WD_MANAGER_AVAILABLE = True
except Exception:
    _WD_MANAGER_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except Exception:
    _BS4_AVAILABLE = False


# Funções para gerenciar sites via JSON
def load_sites_from_json():
    """Carrega lista de sites do arquivo JSON"""
    json_file = Path("lista_sites.json")
    if json_file.exists():
        try:
            import json
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Erro ao carregar lista_sites.json: {e}")
    # Garante que sempre retornamos uma lista, evitando None
    return []


def save_sites_to_json(sites):
    """Salva lista de sites no arquivo JSON"""
    json_file = Path("lista_sites.json")
    try:
        import json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sites, f, indent=2, ensure_ascii=False)
        logging.info(f"Lista de sites salva em {json_file}")
    except Exception as e:
        logging.error(f"Erro ao salvar lista_sites.json: {e}")

# diretório para armazenar arquivos de hash
HASH_DIR = Path("hashes")
HASH_DIR.mkdir(exist_ok=True)

# Telegram: configuração via variáveis de ambiente
USE_TELEGRAM_ALERT = os.getenv("USE_TELEGRAM_ALERT", "1") not in ("0", "false", "False")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def sanitize_for_filename(url: str) -> str:
    """Gera um nome de arquivo legível a partir da URL, removendo caracteres problemáticos."""
    p = urlparse(url)
    name = (p.netloc + p.path).strip()
    # substituir caracteres não alfanuméricos por _ e limitar tamanho
    name = re.sub(r"[^0-9a-zA-Z.-]", "_", name)
    if len(name) > 120:
        name = name[:120]
    return name


def create_driver():
    options = Options()
    # usar headless compatível com versões recentes do Chrome
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if _WD_MANAGER_AVAILABLE:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    return driver


def extract_image_sets(html: str) -> dict:
    """Extrai conjuntos de imagens de carousels/banners para detectar mudanças estruturais."""
    image_sets = {}
    
    if _BS4_AVAILABLE:
        soup = BeautifulSoup(html, "html.parser")
        
        # Identificar possíveis carousels/sliders/banners
        carousel_selectors = [
            '[class*="carousel"]',
            '[class*="slider"]', 
            '[class*="banner"]',
            '[class*="slideshow"]',
            '[id*="carousel"]',
            '[id*="slider"]',
            '[id*="banner"]'
        ]
        
        for selector in carousel_selectors:
            carousels = soup.select(selector)
            for i, carousel in enumerate(carousels):
                # Extrair todas as URLs de imagem dentro do carousel
                images = carousel.find_all('img')
                img_urls = []
                
                for img in images:
                    src = img.get('src', '')
                    data_src = img.get('data-src', '')  # lazy loading
                    
                    # Usar data-src se src estiver vazio (lazy loading)
                    url = data_src if data_src else src
                    
                    if url and not url.startswith('data:'):  # ignorar imagens base64
                        # Normalizar URL (remover parâmetros de cache)
                        url = re.sub(r'[?&](v|cache|t|timestamp)=[^&]*', '', url)
                        img_urls.append(url)
                
                if img_urls:
                    # Criar hash do conjunto (ordenado para consistência)
                    img_urls_sorted = sorted(set(img_urls))  # remove duplicatas e ordena
                    set_signature = '|'.join(img_urls_sorted)
                    image_sets[f"{selector}_{i}"] = hashlib.md5(set_signature.encode()).hexdigest()
    
    return image_sets


def normalize_html(html: str) -> str:
    """Normaliza HTML removendo scripts/styles e elementos dinâmicos, mas preservando estrutura de conteúdo."""
    if _BS4_AVAILABLE:
        soup = BeautifulSoup(html, "html.parser")
        
        # Remover scripts e styles
        for tag in soup(["script", "style"]):
            tag.decompose()
            
        # Remover comentários
        for comment in soup.find_all(text=lambda text: isinstance(text, type(soup.string)) and isinstance(text, str) and text.strip().startswith("<!--")):
            try:
                comment.extract()
            except Exception:
                pass
        
        # Normalizar carousels: remover classes dinâmicas mas manter estrutura
        carousel_elements = soup.select('[class*="carousel"], [class*="slider"], [class*="banner"]')
        for element in carousel_elements:
            # Remover classes que indicam estado (active, current, selected)
            if element.get('class'):
                classes = element.get('class', [])
                filtered_classes = [c for c in classes if not re.match(r'(active|current|selected|show|visible)', c, re.I)]
                if filtered_classes:
                    element['class'] = filtered_classes
                else:
                    del element['class']
            
            # Normalizar elementos filhos (imagens do carousel)
            for img in element.find_all('img'):
                # Remover classes dinâmicas das imagens
                if img.get('class'):
                    img_classes = img.get('class', [])
                    img_filtered = [c for c in img_classes if not re.match(r'(active|current|selected|show|visible)', c, re.I)]
                    if img_filtered:
                        img['class'] = img_filtered
                    else:
                        del img['class']
                
                # Remover atributos de estilo dinâmico
                if img.get('style'):
                    del img['style']
        
        # Remover timestamps e contadores dinâmicos do texto
        text = soup.get_text(separator=" ", strip=True)
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            # Ignorar linhas com padrões dinâmicos comuns
            if not re.search(r'(\d{1,2}[:/]\d{1,2}[:/]\d{2,4}|\d+:\d+|visualizaç|views?:|acess|visit|online)', line, re.I):
                filtered_lines.append(line)
        
        text = '\n'.join(filtered_lines)
    else:
        # Fallback sem BeautifulSoup
        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
    
    # Normalizar espaços
    normalized = " ".join(text.split())
    return normalized


def get_page_hash_and_redirect_info(driver, url: str, wait_seconds: int = 15) -> tuple[str, str, bool]:
    """Carrega a URL, espera o body e retorna sha256 do HTML normalizado + conjuntos de imagens + info de redirecionamento."""
    original_url = url
    driver.get(url)
    try:
        WebDriverWait(driver, wait_seconds).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        # continuar mesmo se a espera falhar; page_source pode estar disponível
        logging.debug("WebDriverWait expirou para %s", url)

    # pequena pausa para que JS assíncrono finalize (se necessário)
    time.sleep(1)
    
    # Verificar se houve redirecionamento
    final_url = driver.current_url
    was_redirected = False
    redirect_info = ""
    
    # Normalizar URLs para comparação (remover trailing slash, fragmentos, etc.)
    original_parsed = urlparse(original_url)
    final_parsed = urlparse(final_url)
    
    # Ignorar URLs especiais (data:, file:, about:, etc.)
    if original_parsed.scheme in ('http', 'https') and final_parsed.scheme in ('http', 'https'):
        # Comparar domínio e path principal
        original_domain = original_parsed.netloc.lower()
        final_domain = final_parsed.netloc.lower()
        
        if original_domain != final_domain:
            was_redirected = True
            redirect_info = f"Redirecionado de {original_domain} para {final_domain}"
        elif original_parsed.path.rstrip('/') != final_parsed.path.rstrip('/'):
            # Redirecionamento para path diferente no mesmo domínio
            # Ignorar redirecionamentos triviais (apenas adição de index.html, etc.)
            original_path = original_parsed.path.rstrip('/').lower()
            final_path = final_parsed.path.rstrip('/').lower()
            
            # Não considerar redirecionamento se:
            # 1. Apenas adicionou index.html ou similar
            # 2. A URL final é uma extensão da URL original (apenas adiciona caminhos)
            # 3. URL base sendo direcionada para um subpath (adição de caminho)
            is_trivial_redirect = (
                (original_path == '' and final_path in ('/index.html', '/index.php', '/index.htm', '/home')) or
                (original_path != '' and final_path.startswith(original_path + '/')) or
                (original_path == '' and final_path != '' and final_path.startswith('/'))
            )
            
            if not is_trivial_redirect:
                was_redirected = True
                redirect_info = f"Redirecionado para caminho diferente: {final_parsed.path}"
    
    html = driver.page_source
    
    # Normalizar conteúdo textual
    normalized_text = normalize_html(html)
    
    # Extrair conjuntos de imagens de carousels/banners
    image_sets = extract_image_sets(html)
    
    # Combinar conteúdo textual + estrutura de imagens
    combined_content = f"TEXT:{normalized_text}|IMAGES:{sorted(image_sets.items())}"
    page_hash = hashlib.sha256(combined_content.encode("utf-8")).hexdigest()
    
    # Log para debug (opcional - pode ser removido depois)
    if image_sets:
        logging.debug(f"Conjuntos de imagem detectados em {url}: {list(image_sets.keys())}")
    
    return page_hash, redirect_info, was_redirected


def get_page_hash(driver, url: str, wait_seconds: int = 15) -> str:
    """Carrega a URL, espera o body e retorna sha256 do HTML normalizado + conjuntos de imagens."""
    page_hash, _, _ = get_page_hash_and_redirect_info(driver, url, wait_seconds)
    return page_hash


def hash_file_for_url(url: str) -> Path:
    name = sanitize_for_filename(url)
    return HASH_DIR / f"{name}.txt"


def load_last_hash(hash_path: Path) -> str | None:
    if not hash_path.exists():
        return None
    return hash_path.read_text(encoding="utf-8").strip()


def save_hash(hash_path: Path, h: str):
    hash_path.write_text(h, encoding="utf-8")


def send_telegram_alert(message: str):
    if not USE_TELEGRAM_ALERT:
        logging.info("Alerta Telegram desativado. Mensagem seria: %s", message)
        return

    if TELEGRAM_BOT_TOKEN.startswith("SEU_") or TELEGRAM_CHAT_ID.startswith("SEU_"):
        logging.warning("Telegram configurado com placeholders. Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nas variáveis de ambiente.")
        logging.info("Mensagem (não enviada): %s", message)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            logging.info("Alerta enviado para Telegram.")
        else:
            logging.error("Falha ao enviar alerta Telegram: %s", resp.text)
    except Exception as e:
        logging.exception("Erro ao enviar alerta Telegram: %s", e)


def main():
    inicio = time.time()

    sites_to_monitor = load_sites_from_json()
    logging.info("Iniciando verificação de %d sites...", len(sites_to_monitor))

    try:
        driver = create_driver()
    except Exception as e:
        logging.exception("Não foi possível criar o driver do Selenium: %s", e)
        return

    mudancas: List[str] = []
    err_connections: List[str] = []
    redirecionamentos: List[str] = []
    err_desconhecido: List[str] = []

    try:
        for url in sites_to_monitor:
            logging.info("Verificando %s", url)
            try:
                current_hash, redirect_info, was_redirected = get_page_hash_and_redirect_info(driver, url)
            except WebDriverException as e:
                logging.exception(f"Erro no WebDriver: {e.msg}")
                err_connections.append(url)
                continue

            except Exception as e:
                logging.exception("Erro ao obter hash de %s: %s", url, e)
                err_desconhecido.append(url)
                continue

            hf = hash_file_for_url(url)
            last_hash = load_last_hash(hf)

            if last_hash is None:
                logging.info("Primeira execução para %s — salvando hash.", url)
                save_hash(hf, current_hash)
                # Verificar redirecionamento na primeira execução também
                if was_redirected:
                    logging.warning("REDIRECIONAMENTO DETECTADO na primeira execução de %s: %s", url, redirect_info)
                    # redirect_msg = (
                    #     "🔄 <b>REDIRECIONAMENTO DETECTADO</b>\n"
                    #     f"Site: {url}\n"
                    #     f"Info: {redirect_info}\n"
                    #     "⚠️ Este site está sendo redirecionado para outro domínio."
                    # )
                    # send_telegram_alert(redirect_msg)

                    redirecionamentos.append(redirect_info)
                continue
            
            if current_hash != last_hash:
                logging.warning("MUDANÇA DETECTADA em %s", url)
                save_hash(hf, current_hash)
                # msg_parts.append(
                #     "⚠ <b>MUDANÇA DETECTADA</b>\n"
                #     f"Site: {url}\n"
                #     "O conteúdo principal da página foi alterado."
                # )

                mudancas.append(url)

            # Adicionar aviso de redirecionamento se detectado
            if was_redirected:
                logging.warning("REDIRECIONAMENTO DETECTADO em %s: %s", url, redirect_info)

                redirecionamentos.append(redirect_info)

        # Enviar mensagem se houver algo para reportar


        if mudancas or err_connections or redirecionamentos or err_desconhecido:
            msg = f"Varredura realizada em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n"
            
            if mudancas:
                msg += "\n⚠ <b>MUDANÇAS DETECTADAS</b>\n"

                for site in mudancas:
                    msg += f"{site}\n"

            if err_connections:
                msg += "\n⚠ <b>PROBLEMAS DE CONEXÃO</b>\n"

                for site in err_connections:
                    msg += f"{site}\n"

            if redirecionamentos:
                msg += "\n🔄 <b>REDIRECIONAMENTOS DETECTADOS</b>\n"

                for info in redirecionamentos:
                    msg += f"{info}\n"

            if err_desconhecido:
                msg += "\n❌ <b>ERROS DESCONHECIDOS</b>\n"

                for site in err_desconhecido:
                    msg += f"{site}\n"
        else:
            msg = (
                f"Varredura realizada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                "Verificação de páginas realizada. Nenhuma alteração encontrada."
            )

        send_telegram_alert(msg)

        fim = time.time()
        minutos, segundos = divmod((fim - inicio), 60)
        logging.info(f"Tempo de execuação: {int(minutos)} minutos e {int(segundos)} segundos")
            
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001 - queremos logar qualquer erro aqui
        logging.exception("Erro inesperado na execução do monitoramento: %s", e)
    finally:
        # Manter o console aberto no final da execução (útil ao rodar o .exe via duplo clique)
        try:
            if os.name == "nt":
                os.system("pause")
            else:
                input("Pressione Enter para sair...")
        except Exception:
            # Se até o pause falhar, apenas sair silenciosamente
            pass