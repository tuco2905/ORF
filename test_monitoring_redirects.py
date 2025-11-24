#!/usr/bin/env python3
"""
Script de exemplo para testar o monitoramento com detecção de redirecionamento
Executa apenas alguns sites para teste rápido
"""

import logging
import sys
from pathlib import Path

# Adicionar o diretório atual ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent))

from monitoramento import create_driver, get_page_hash_and_redirect_info, send_telegram_alert

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Sites de teste - incluindo alguns que podem redirecionar
TEST_SITES = [
    "https://4cta.eb.mil.br/",  # Site militar
    "http://httpbin.org/status/200",  # Site de teste que não redireciona
    "http://httpbin.org/redirect/1",  # Site de teste que sempre redireciona
]

def test_monitoring_with_redirects():
    """Testa o monitoramento incluindo detecção de redirecionamentos"""
    
    print("Iniciando teste de monitoramento com detecção de redirecionamento...")
    print("=" * 70)
    
    try:
        driver = create_driver()
        logging.info("Driver do Selenium criado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao criar driver: {e}")
        return
    
    try:
        for i, url in enumerate(TEST_SITES, 1):
            print(f"\n[{i}/{len(TEST_SITES)}] Testando: {url}")
            logging.info("Verificando %s", url)
            
            try:
                # Obter hash e informações de redirecionamento
                current_hash, redirect_info, was_redirected = get_page_hash_and_redirect_info(driver, url, wait_seconds=10)
                
                print(f"   Hash obtido: {current_hash[:16]}...")
                
                if was_redirected:
                    print(f"   REDIRECIONAMENTO DETECTADO!")
                    print(f"   Info: {redirect_info}")
                    
                    # Simular envio de mensagem (sem enviar realmente)
                    msg = (
                        f"🔄 REDIRECIONAMENTO DETECTADO\n"
                        f"Site: {url}\n"
                        f"Info: {redirect_info}\n"
                        "⚠️ Este site está sendo redirecionado para outro domínio."
                    )
                    print(f"   Mensagem que seria enviada:")
                    print(f"   {msg.replace(chr(10), chr(10) + '   ')}")
                else:
                    print("   Nenhum redirecionamento detectado.")
                
            except Exception as e:
                logging.error("Erro ao verificar %s: %s", url, e)
                print(f"   ERRO: {e}")
                
    finally:
        try:
            driver.quit()
            logging.info("Driver fechado.")
        except Exception:
            pass
    
    print("\n" + "=" * 70)
    print("Teste concluído!")

if __name__ == "__main__":
    test_monitoring_with_redirects()