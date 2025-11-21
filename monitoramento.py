import os
import time
import hashlib
import logging
import requests
import re
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

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

ENV_PATH = Path(__file__).with_name(".env")


def _load_env_file():
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


# Lista de sites a monitorar
SITES = [
    "https://cma.eb.mil.br/",
    "https://4cta.eb.mil.br/",
    "https://nee.cma.eb.mil.br/",
    "https://cma.eb.mil.br/operacoes",
    "http://12rm.eb.mil.br/",
    "http://2gpte.eb.mil.br/",
    "http://cecma.eb.mil.br/",
    "http://1bcomgesl.eb.mil.br/",
    "https://5gaaaesl.eb.mil.br/",
    "http://12cgcfex.eb.mil.br/",
    "http://cmm.eb.mil.br/",
    "https://cmm.eb.mil.br/ead",
    "http://ava.cmm.eb.mil.br/",
    "http://avadepa.cmm.eb.mil.br/",
    "http://avasead.cmm.eb.mil.br/",
    "http://12bsup.eb.mil.br/",
    "http://4cgeo.eb.mil.br/",
    "http://4bavex.eb.mil.br/",
    "http://10gacsl.eb.mil.br/",
    "http://cro12.eb.mil.br/",
    "http://1bdainfsl.eb.mil.br/",
    "http://2bdainfsl.eb.mil.br/",
    "http://16bdainfsl.eb.mil.br/",
    "http://17bdainfsl.eb.mil.br/",
    "http://hmam.eb.mil.br/",
    "http://sau.hmam.eb.mil.br/",
    "https://agendasame.hmam.eb.mil.br/",
    "http://hgupv.eb.mil.br/",
    "http://hgusgc.eb.mil.br/",
    "http://hgut.eb.mil.br/",
    "http://1bis.eb.mil.br/",
    "http://4bis.eb.mil.br/",
    "http://5bis.eb.mil.br/",
    "http://6bis.eb.mil.br/",
    "http://7bis.eb.mil.br",
    "http://8bis.eb.mil.br/",
    "http://54bis.eb.mil.br/",
    "http://61bis.eb.mil.br/",
    "http://5bec.eb.mil.br/",
    "http://6bec.eb.mil.br/",
    "http://7bec.eb.mil.br/",
    "http://21ciaecnst.eb.mil.br/",
    "http://1blogsl.eb.mil.br/",
    "http://17blogsl.eb.mil.br/",
    "http://cigs.eb.mil.br/",
    "https://zoo.cigs.eb.mil.br/",
    "https://licitacoeseb.12rm.eb.mil.br/community-list",
    "http://ftloghum.eb.mil.br"
]

# diretório para armazenar arquivos de hash
HASH_DIR = Path("hashes")
HASH_DIR.mkdir(exist_ok=True)

# Telegram: ler de variáveis de ambiente para segurança
USE_TELEGRAM_ALERT = os.getenv("USE_TELEGRAM_ALERT", "1") not in ("0", "false", "False")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "NAO_EXISTO")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "NAO_EXISTO")

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
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logging.exception("Erro ao instalar o ChromeDriver")
            logging.info("Tentando usar o ChromeDriver instalado no sistema")

            CHROMEDRIVER_PATH = r"C:\Users\Administrador\.wdm\drivers\chromedriver\win64\142.0.7444.175\chromedriver-win32\chromedriver.exe"
            service = Service(CHROMEDRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=options)
    else:
        # fallback: assume ChromeDriver está no PATH
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


def get_page_hash(driver, url: str, wait_seconds: int = 15) -> str:
    """Carrega a URL, espera o body e retorna sha256 do HTML normalizado + conjuntos de imagens."""
    driver.get(url)
    try:
        WebDriverWait(driver, wait_seconds).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        # continuar mesmo se a espera falhar; page_source pode estar disponível
        logging.debug("WebDriverWait expirou para %s", url)

    # pequena pausa para que JS assíncrono finalize (se necessário)
    time.sleep(1)
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
        logging.info("Enviando alerta para Telegram com o token: %s", TELEGRAM_BOT_TOKEN)
        logging.info("Enviando alerta para Telegram com o chat_id: %s", TELEGRAM_CHAT_ID)
        if resp.status_code == 200:
            logging.info("Alerta enviado para Telegram.")
        else:
            logging.error("Falha ao enviar alerta Telegram: %s", resp.text)
    except Exception as e:
        logging.exception("Erro ao enviar alerta Telegram: %s", e)


def main():
    inicio = time.time()
    logging.info("Iniciando verificação de %d sites...", len(SITES))

    got_changes_in_any_page: bool = False
    mudancas = open("mudancas.txt", "w", encoding="UTF-8")
    err_conection = open("err_conection.txt", "w", encoding="UTF-8")


    try:
        driver = create_driver()
    except Exception as e:
        logging.exception("Não foi possível criar o driver do Selenium: %s", e)
        return

    try:
        for url in SITES:
            logging.info("Verificando %s", url)
            try:
                current_hash = get_page_hash(driver, url)
            

                hf = hash_file_for_url(url)
                last_hash = load_last_hash(hf)

                if last_hash is None:
                    logging.info("Primeira execução para %s — salvando hash.", url)
                    save_hash(hf, current_hash)
                    continue

                if current_hash != last_hash:
                    got_changes_in_any_page = True
                    logging.warning("MUDANÇA DETECTADA em %s", url)
                    mudancas.write(f"{url}\n")
                    save_hash(hf, current_hash)
                else:
                    logging.info("Nenhuma mudança detectada em %s", url)

            except WebDriverException as e:
                logging.exception(f"Erro no WebDriver: {e.msg}")
                err_conection.write(f"{url}\n")
            except Exception as e:
                logging.exception("Erro ao obter hash de %s: %s", url, e)
                err_conection.write(f"{url}\n")
                continue

        mudancas.close()
        err_conection.close()

        if got_changes_in_any_page:
            mudancas = open("mudancas.txt", "r", encoding="UTF-8")
            err_conection = open("err_conection.txt", "r", encoding="UTF-8")
            
            msg = (
                f"Varredura realizada em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n\n"
                "⚠ <b>MUDANÇAS DETECTADAS</b>\n"
            )

            mudancas_sites = mudancas.read().splitlines()

            for site in mudancas_sites:
                msg += f"{site}\n"

            msg += "\n⚠ <b>PROBLEMAS DE CONEXÃO</b>\n"

            err_conection_sites = err_conection.read().splitlines()

            for site in err_conection_sites:
                msg += f"{site}\n"

            send_telegram_alert(msg)

        if not got_changes_in_any_page:
            msg = (
                f"Varredura realizada em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n\n"
                "Verificação de páginas realizada. Nenhuma alteração encontrada."
            )

            send_telegram_alert(msg)
            logging.info("Verificação de páginas realizada. Nenhuma alteração encontrada.")
        
        fim = time.time()
        minutos, segundos = divmod((fim - inicio), 60)
        logging.info(f"Tempo de execuação: {int(minutos)} minutos e {int(segundos)} segundos")

    finally:
        try:
            mudancas.close()
            err_conection.close()
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()