#!/usr/bin/env bash

# Caminho base do projeto (ajuste conforme o seu ambiente)
BASE_DIR="/home/admin/monitoramento-site"
PYTHON="$BASE_DIR/venvautomatizacao/bin/python3"
SCRIPT="$BASE_DIR/monitoramento.py"
LOG_DIR="$BASE_DIR/logs"

# Verifica se o Python existe
if [ ! -x "$PYTHON" ]; then
  echo "Nao foi encontrado o interpretador Python esperado em:"
  echo "  $PYTHON"
  echo "Verifique a instalacao do ambiente virtual antes de continuar."
  exit 1
fi

# Verifica se o script existe
if [ ! -f "$SCRIPT" ]; then
  echo "Nao foi encontrado o script monitoramento.py em:"
  echo "  $SCRIPT"
  exit 1
fi

# Cria o diretório de logs, se necessário
if [ ! -d "$LOG_DIR" ]; then
  mkdir -p "$LOG_DIR"
fi

# Gera timestamp para o nome do arquivo de log
timestamp="$(date '+%Y%m%d_%H%M%S')"
LOG_FILE="$LOG_DIR/monitoramento_${timestamp}.log"

# Vai para o diretório base
cd "$BASE_DIR" || exit 1

# Registra início
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando monitoramento" >> "$LOG_FILE"

# Executa o script e redireciona saída e erros para o log
"$PYTHON" "$SCRIPT" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Registra fim
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finalizado com codigo $EXIT_CODE" >> "$LOG_FILE"

exit "$EXIT_CODE"