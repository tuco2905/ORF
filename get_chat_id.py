#!/usr/bin/env python3
"""
Script para descobrir o Chat ID do Telegram.
Execute este script depois de criar o bot e enviar uma mensagem para ele.
"""
import requests

def get_chat_id():
    # Substitua YOUR_BOT_TOKEN pelo token que o BotFather te deu
    bot_token = input("Cole o token do seu bot aqui: ").strip()
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("ok"):
            print("❌ Erro ao conectar com o bot. Verifique o token.")
            return
            
        updates = data.get("result", [])
        
        if not updates:
            print("❌ Nenhuma mensagem encontrada.")
            print("💡 Envie uma mensagem para o seu bot primeiro, depois execute novamente.")
            return
            
        print("✅ Chats encontrados:")
        for update in updates:
            message = update.get("message", {})
            chat = message.get("chat", {})
            
            chat_id = chat.get("id")
            chat_type = chat.get("type")
            first_name = chat.get("first_name", "")
            username = chat.get("username", "")
            
            print(f"   Chat ID: {chat_id}")
            print(f"   Tipo: {chat_type}")
            print(f"   Nome: {first_name}")
            if username:
                print(f"   Username: @{username}")
            print("   ---")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    get_chat_id()