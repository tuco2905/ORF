#!/usr/bin/env python3
"""
Teste específico para casos de adição de caminho
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from monitoramento import get_page_hash_and_redirect_info
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_with_real_selenium():
    """Testa a função real com casos simulados"""
    
    print("Testando função real get_page_hash_and_redirect_info...")
    print("=" * 60)
    
    # Configurar driver (modo headless para teste)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Teste com um site que sabemos que funciona
        test_url = "https://httpbin.org/get"
        print(f"Testando com URL: {test_url}")
        
        page_hash, redirect_info, was_redirected = get_page_hash_and_redirect_info(driver, test_url, 10)
        
        print(f"Hash da página: {page_hash[:16]}...")
        print(f"Foi redirecionado: {was_redirected}")
        if redirect_info:
            print(f"Info do redirecionamento: {redirect_info}")
        else:
            print("Nenhum redirecionamento detectado")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_with_real_selenium()