#!/usr/bin/env python3
"""
Teste do sistema Telegram com simulação de mudança
"""
import os
import sys
import logging

# Adicionar o diretório atual ao path
sys.path.append('.')

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Importar função do monitoramento
try:
    from monitoramento import send_telegram_alert
    
    print("🧪 === TESTE DO SISTEMA TELEGRAM ===")
    
    # Simular uma mudança detectada
    site_teste = "https://4cta.eb.mil.br/"
    mensagem = f"""⚠ <b>MUDANÇA DETECTADA</b>
Site: {site_teste}
O conteúdo principal da página foi alterado.

🧪 <i>Esta é uma mensagem de teste do sistema de monitoramento.</i>"""
    
    print(f"📤 Enviando alerta de teste para: {site_teste}")
    
    # Enviar alerta
    send_telegram_alert(mensagem)
    
    print("✅ Teste concluído! Verifique seu Telegram.")
    
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
except Exception as e:
    print(f"❌ Erro durante o teste: {e}")