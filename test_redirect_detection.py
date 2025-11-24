#!/usr/bin/env python3
"""
Script de teste para verificar a detecção de redirecionamentos
"""

import sys
from pathlib import Path
import logging
from monitoramento import create_driver, get_page_hash_and_redirect_info

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def test_redirect_detection():
    """Testa a detecção de redirecionamentos com URLs conhecidas"""
    
    # URLs de teste - algumas que podem redirecionar
    test_urls = [
        "http://google.com",  # Redireciona para https://www.google.com
        "http://facebook.com",  # Redireciona para https://www.facebook.com
        "https://4cta.eb.mil.br/",  # URL militar - pode não redirecionar
        "http://httpbin.org/redirect/1",  # Serviço que sempre redireciona
        "http://httpbin.org/status/200",  # Serviço que não redireciona
    ]
    
    print("🔄 Testando detecção de redirecionamentos...")
    print("=" * 60)
    
    try:
        driver = create_driver()
        
        for url in test_urls:
            print(f"\n📍 Testando: {url}")
            try:
                page_hash, redirect_info, was_redirected = get_page_hash_and_redirect_info(driver, url, wait_seconds=10)
                
                print(f"   Hash: {page_hash[:16]}...")
                print(f"   Redirecionado: {'✅ SIM' if was_redirected else '❌ NÃO'}")
                
                if was_redirected:
                    print(f"   📋 Info: {redirect_info}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                
    except Exception as e:
        print(f"❌ Erro ao criar driver: {e}")
        return
    
    finally:
        try:
            driver.quit()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_redirect_detection()