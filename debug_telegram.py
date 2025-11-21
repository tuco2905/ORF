#!/usr/bin/env python3
"""
Debug das configurações do Telegram usadas em monitoramento.py

Este script:
- Lê o arquivo .env na mesma pasta
- Carrega as variáveis de ambiente
- Mostra os valores usados e faz validações simples
"""

import os
from pathlib import Path


# Mesmo mecanismo de carregamento de .env do monitoramento.py
ENV_PATH = Path(__file__).with_name(".env")


def _load_env_file() -> None:
    """Carrega variáveis do arquivo .env para o os.environ, se existir."""
    if not ENV_PATH.exists():
        return

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


# Exatamente a mesma lógica do monitoramento.py
USE_TELEGRAM_ALERT = os.getenv("USE_TELEGRAM_ALERT", "1") not in ("0", "false", "False")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "NAO_EXISTO")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "NAO_EXISTO")

print("=== DEBUG TELEGRAM CONFIG (APÓS CARREGAR .env) ===")
print(f"USE_TELEGRAM_ALERT: {USE_TELEGRAM_ALERT}")
print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
print(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
print()

# Testes da lógica de validação (mesma ideia do monitoramento.py: rejeitar placeholders 'SEU_')
print("=== TESTES DE VALIDAÇÃO ===")
starts_with_seu = TELEGRAM_BOT_TOKEN.startswith("SEU_") or TELEGRAM_CHAT_ID.startswith("SEU_")
print(f"Token começa com 'SEU_': {TELEGRAM_BOT_TOKEN.startswith('SEU_')}")
print(f"Chat ID começa com 'SEU_': {TELEGRAM_CHAT_ID.startswith('SEU_')}")
print(f"Algum começa com 'SEU_': {starts_with_seu}")
print()

# Verificar variáveis de ambiente brutas
print("=== VARIÁVEIS DE AMBIENTE (os.getenv) ===")
env_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
print(f"Env TELEGRAM_BOT_TOKEN: {env_bot_token}")
print(f"Env TELEGRAM_CHAT_ID: {env_chat_id}")

if starts_with_seu:
    print("\n❌ PROBLEMA: Sistema detectou placeholders (valores começando com 'SEU_').")
elif TELEGRAM_BOT_TOKEN == "NAO_EXISTO" or TELEGRAM_CHAT_ID == "NAO_EXISTO":
    print("\n❌ PROBLEMA: Variáveis TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não foram definidas.")
else:
    print("\n✅ OK: Configuração validada com sucesso!")
