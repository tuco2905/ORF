#!/usr/bin/env python3
"""
Teste rápido do monitoramento com um site real
"""

import sys
import logging
from pathlib import Path

# Configurar o diretório de trabalho
sys.path.insert(0, str(Path(__file__).parent))

from monitoramento import create_driver, get_page_hash_and_redirect_info

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def test_quick_monitoring():
    """Teste rápido com um site real"""
    print("=== TESTE RAPIDO DO MONITORAMENTO ===")
    
    try:
        # Criar driver
        driver = create_driver()
        print("[OK] Driver criado")
        
        # Testar com o site 4CTA
        test_url = "https://4cta.eb.mil.br/"
        print(f"Testando: {test_url}")
        
        # Obter hash e info de redirecionamento
        hash_result, redirect_info, was_redirected = get_page_hash_and_redirect_info(
            driver, test_url, wait_seconds=10
        )
        
        print(f"Hash: {hash_result[:32]}...")
        print(f"Redirecionamento: {'SIM' if was_redirected else 'NAO'}")
        
        if was_redirected:
            print(f"Info: {redirect_info}")
        else:
            print("Nenhum redirecionamento detectado")
        
        # Fechar driver
        driver.quit()
        print("[OK] Teste concluído com sucesso")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quick_monitoring()
    if success:
        print("\n[RESULTADO] Teste bem-sucedido! O sistema está funcionando.")
    else:
        print("\n[RESULTADO] Teste falhou. Verifique os erros acima.")