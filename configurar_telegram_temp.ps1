# Configuração temporária do Telegram (válida apenas para esta sessão)

# Substitua pelos seus valores reais:
$env:TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"
$env:TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

Write-Host "✅ Variáveis configuradas para esta sessão!" -ForegroundColor Green
Write-Host "Bot Token: $env:TELEGRAM_BOT_TOKEN" -ForegroundColor Yellow  
Write-Host "Chat ID: $env:TELEGRAM_CHAT_ID" -ForegroundColor Yellow