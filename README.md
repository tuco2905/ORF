# Monitoramento de sites

Este repositório contém um script (`monitoramento.py`) que monitora uma lista de sites, calcula um hash do conteúdo HTML normalizado e notifica por Telegram quando mudanças são detectadas.

## Instalação
No PowerShell:

```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

## Variáveis de ambiente (recomendado)
Configure as seguintes variáveis de ambiente para habilitar notificações via Telegram:

```powershell
$env:TELEGRAM_BOT_TOKEN = "<seu_token_aqui>"
$env:TELEGRAM_CHAT_ID = "<seu_chat_id>"
$env:USE_TELEGRAM_ALERT = "1"  # 0 para desativar
```

## Como executar
```powershell
python .\monitoramento.py
```

## Observações
- É recomendado instalar o Google Chrome e, se não quiser instalar manualmente o ChromeDriver, instalar `webdriver-manager` (já listado no `requirements.txt`) para que o script gerencie automaticamente o driver.
- Se não quiser usar Selenium (para sites estáticos), é possível adaptar o script para usar `requests` + parsing, o que será mais rápido.
- Para executar periodicamente no Windows, use o Agendador de Tarefas (Task Scheduler) apontando para o comando acima.

## Push para GitHub
Para enviar o projeto para o repositório GitHub, execute os comandos em `comandos-git.txt` ou use:

```powershell
git init
git branch -M main
git remote add origin https://github.com/tuco2905/ORF.git
git add .
git commit -m "Primeira versão: monitoramento de múltiplos sites"
git push -u origin main
```

## Problemas comuns
- Se o Python não estiver no PATH, adicione-o ou execute pelo caminho completo do interpretador.
- Se houver erros na importação de `webdriver_manager` ou `bs4`, instale as dependências conforme `requirements.txt`.
- Se o Git não estiver instalado, baixe em: https://git-scm.com/download/win

