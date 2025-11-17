#!/usr/bin/env python3
"""
Debug das configurações do Telegram no monitoramento.py
"""
import os

# Exatamente como no monitoramento.py
USE_TELEGRAM_ALERT = os.getenv("USE_TELEGRAM_ALERT", "1") not in ("0", "false", "False")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8568563177:AAE2-LRMNzyEHGoX-SNVmul3gJ1ELiIjIsE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1464187966")

print("=== DEBUG TELEGRAM CONFIG ===")
print(f"USE_TELEGRAM_ALERT: {USE_TELEGRAM_ALERT}")
print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
print(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
print()

# Testes da lógica de validação
print("=== TESTES DE VALIDAÇÃO ===")
starts_with_seu = TELEGRAM_BOT_TOKEN.startswith("SEU_") or TELEGRAM_CHAT_ID.startswith("SEU_")
print(f"Token começa com 'SEU_': {TELEGRAM_BOT_TOKEN.startswith('SEU_')}")
print(f"Chat ID começa com 'SEU_': {TELEGRAM_CHAT_ID.startswith('SEU_')}")
print(f"Algum começa com 'SEU_': {starts_with_seu}")
print()

# Verificar variáveis de ambiente
print("=== VARIÁVEIS DE AMBIENTE ===")
env_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
print(f"Env TELEGRAM_BOT_TOKEN: {env_bot_token}")
print(f"Env TELEGRAM_CHAT_ID: {env_chat_id}")

if starts_with_seu:
    print("\n❌ PROBLEMA: Sistema detectou placeholders!")
else:
    print("\n✅ OK: Configuração validada com sucesso!")