#!/usr/bin/env python3
"""
Teste das configurações do Telegram
"""
import requests
import os

# Usar os mesmos valores do monitoramento.py
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8568563177:AAE2-LRMNzyEHGoX-SNVmul3gJ1ELiIjIsE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1464187966")

def test_telegram():
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")
    
    # Verificar se começam com "SEU_"
    if TELEGRAM_BOT_TOKEN.startswith("SEU_") or TELEGRAM_CHAT_ID.startswith("SEU_"):
        print("❌ Detectados placeholders!")
        return False
    
    print("✅ Configuração parece válida!")
    
    # Teste de envio
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🧪 <b>TESTE</b> - Sistema de monitoramento configurado com sucesso!",
        "parse_mode": "HTML",
    }
    
    try:
        print("📤 Enviando mensagem de teste...")
        resp = requests.post(url, data=payload, timeout=10)
        
        if resp.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            return True
        else:
            print(f"❌ Erro ao enviar: {resp.status_code}")
            print(f"📄 Resposta: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    test_telegram()