#!/usr/bin/env python3
"""
Teste da lógica de detecção de redirecionamento
"""

from urllib.parse import urlparse

def test_redirect_logic(original_url, final_url):
    """Testa a lógica de detecção de redirecionamento"""
    original_parsed = urlparse(original_url)
    final_parsed = urlparse(final_url)
    
    was_redirected = False
    redirect_info = ""
    
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
    
    return was_redirected, redirect_info

def run_tests():
    """Executa testes da lógica de redirecionamento"""
    
    test_cases = [
        # (original_url, final_url, expected_redirect, description)
        ("https://example.com", "https://example.com", False, "URL idêntica"),
        ("https://example.com/", "https://example.com", False, "Remoção de trailing slash"),
        ("https://example.com", "https://example.com/", False, "Adição de trailing slash"),
        ("https://example.com", "https://example.com/index.html", False, "Adição de index.html"),
        ("https://example.com", "https://example.com/home", False, "Adição de /home"),
        ("https://example.com", "https://example.com/novo-caminho", False, "Adição de novo caminho"),
        ("https://example.com/docs", "https://example.com/docs/tutorial", False, "Extensão de caminho existente"),
        ("https://example.com/old", "https://example.com/new", True, "Mudança de caminho"),
        ("https://example.com", "https://other.com", True, "Mudança de domínio"),
        ("https://example.com/path1", "https://example.com/path2", True, "Mudança para caminho diferente"),
        ("https://example.com/docs", "https://example.com/docs/", False, "Adição de trailing slash em subpath"),
        ("https://example.com/api", "https://example.com/api/v1/users", False, "Extensão de API path"),
    ]
    
    print("Testando lógica de detecção de redirecionamento:")
    print("=" * 60)
    
    for original, final, expected, description in test_cases:
        result, info = test_redirect_logic(original, final)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"{status} {description}")
        print(f"  Original: {original}")
        print(f"  Final: {final}")
        print(f"  Expected: {'Redirect' if expected else 'No Redirect'}")
        print(f"  Result: {'Redirect' if result else 'No Redirect'}")
        if info:
            print(f"  Info: {info}")
        print()

if __name__ == "__main__":
    run_tests()