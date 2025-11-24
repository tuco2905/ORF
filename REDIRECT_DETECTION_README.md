# Implementação de Detecção de Redirecionamentos - README

## Resumo das Modificações

Foi implementada a funcionalidade de detecção de redirecionamentos no sistema de monitoramento. O sistema agora detecta quando um site é redirecionado para outro domínio ou caminho e inclui essa informação nas mensagens de alerta do Telegram.

## Principais Modificações

### 1. Nova Função: `get_page_hash_and_redirect_info()`

```python
def get_page_hash_and_redirect_info(driver, url: str, wait_seconds: int = 15) -> tuple[str, str, bool]:
```

Esta função substitui a função `get_page_hash()` original e retorna:
- `str`: Hash da página (mesmo comportamento anterior)
- `str`: Informações sobre o redirecionamento (se houver)
- `bool`: Se houve redirecionamento ou não

### 2. Lógica de Detecção de Redirecionamento

O sistema detecta redirecionamentos comparando:
- **Domínios diferentes**: `example.com` → `newsite.com`
- **Caminhos diferentes**: `site.com/` → `site.com/home`
- **Protocolos/subdomínios**: `http://site.com` → `https://www.site.com`

### 3. Mensagens de Alerta Aprimoradas

As mensagens do Telegram agora incluem:

#### Para redirecionamentos detectados:
```
🔄 ATENÇÃO - REDIRECIONAMENTO
Info: Redirecionado de example.com para newsite.com
⚠️ Este site está sendo redirecionado para outro domínio.
```

#### Para mudanças de conteúdo + redirecionamento:
```
⚠ MUDANÇA DETECTADA
Site: https://example.com
O conteúdo principal da página foi alterado.

🔄 ATENÇÃO - REDIRECIONAMENTO
Info: Redirecionado de example.com para newsite.com
⚠️ Este site está sendo redirecionado para outro domínio.
```

### 4. Detecção na Primeira Execução

O sistema também detecta redirecionamentos na primeira execução (quando ainda não há hash salvo), enviando um alerta imediato se um site estiver redirecionando.

## Benefícios da Implementação

1. **Segurança**: Detecta possíveis comprometimentos de sites que podem estar redirecionando para domínios maliciosos
2. **Transparência**: Informa claramente quando um site oficial está redirecionando
3. **Monitoramento Proativo**: Permite acompanhar mudanças na infraestrutura dos sites monitorados

## Casos de Uso Detectados

- ✅ Redirecionamentos HTTP → HTTPS
- ✅ Mudanças de domínio (compromentimento ou migração)
- ✅ Redirecionamentos para subdiretórios
- ✅ Adição/remoção de subdomínios (www, etc.)
- ❌ Ignora diferenças apenas na barra final (/site vs /site/)

## Arquivos Modificados

- `monitoramento.py`: Implementação principal
- `test_monitoring_redirects.py`: Script de teste criado
- `test_redirect_detection.py`: Teste complementar criado

## Como Testar

Execute o script de teste para verificar a funcionalidade:

```bash
python test_monitoring_redirects.py
```

Ou execute o monitoramento normal - a detecção de redirecionamento será automática:

```bash
python monitoramento.py
```

## Compatibilidade

A implementação mantém total compatibilidade com o código existente:
- A função `get_page_hash()` original ainda existe e funciona normalmente
- Todas as funcionalidades anteriores são preservadas
- Apenas adiciona a nova funcionalidade de detecção de redirecionamento