@echo off
echo Configurando variáveis de ambiente do Telegram...
echo.

set /p BOT_TOKEN="Digite o token do seu bot: "
set /p CHAT_ID="Digite o chat ID: "

echo.
echo Definindo variáveis de ambiente...

setx TELEGRAM_BOT_TOKEN "%BOT_TOKEN%"
setx TELEGRAM_CHAT_ID "%CHAT_ID%"

echo.
echo ✅ Variáveis configuradas!
echo ⚠️ Feche e abra o PowerShell novamente para aplicar as mudanças.
echo.
pause