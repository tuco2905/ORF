#!/usr/bin/env python3
"""
Teste do monitoramento completo com alguns sites selecionados
"""

import sys
import logging
from pathlib import Path

# Configurar o diretório de trabalho
sys.path.insert(0, str(Path(__file__).parent))

import monitoramento

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def test_full_monitoring():
    """Teste do monitoramento completo com alguns sites"""
    
    # Sites para teste (apenas alguns)
    test_sites = [
        "https://4cta.eb.mil.br/",
        "https://cma.eb.mil.br/",
        "https://nee.cma.eb.mil.br/",
    ]
    
    print(f"=== TESTE DO MONITORAMENTO COMPLETO ===")
    print(f"Testando {len(test_sites)} sites...")
    
    # Fazer backup dos sites originais
    original_sites = monitoramento.SITES.copy()
    
    try:
        # Substituir temporariamente a lista de sites
        monitoramento.SITES = test_sites
        
        # Executar o monitoramento
        print("\nIniciando monitoramento...")
        monitoramento.main()
        
        print("\n[OK] Monitoramento executado com sucesso!")
        
        # Verificar se arquivos de hash foram criados
        hash_dir = Path("hashes")
        if hash_dir.exists():
            hash_files = list(hash_dir.glob("*.txt"))
            print(f"[OK] {len(hash_files)} arquivos de hash encontrados:")
            for hash_file in hash_files[:5]:  # Mostrar apenas os primeiros 5
                print(f"    - {hash_file.name}")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro durante o monitoramento: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restaurar lista original de sites
        monitoramento.SITES = original_sites

if __name__ == "__main__":
    success = test_full_monitoring()
    if success:
        print("\n[RESULTADO] Teste do monitoramento completo bem-sucedido!")
    else:
        print("\n[RESULTADO] Teste do monitoramento falhou.")