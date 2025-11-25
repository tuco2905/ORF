# Monitoramento de sites

Este projeto faz **monitoramento de múltiplos sites** usando Selenium (Google Chrome headless).  
Para cada site ele:

- captura o HTML,
- normaliza o conteúdo (removendo partes muito dinâmicas),
- calcula um hash,
- compara com o hash anterior salvo em `hashes/`,
- envia **alertas opcionais via Telegram** quando detecta mudanças, problemas de conexão ou redirecionamentos.

A lista de sites é mantida em `lista_sites.json` e pode ser gerenciada por um **web app simples em Flask** (`app.py`).

---

## Instalação (desenvolvimento)

### Dependências básicas

- **Python 3.10+** (recomendado)
- **Google Chrome** instalado
- **ChromeDriver** (gerenciado automaticamente pelo `webdriver-manager`, já listado em `requirements.txt`)

### Instalar dependências Python

No PowerShell (Windows):

```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

No Linux:

```bash
python3 -m pip install -U pip
pip install -r requirements.txt
```

---

## Variáveis de ambiente / `.env`

O projeto lê variáveis de ambiente (diretamente do ambiente ou de um arquivo `.env` na raiz):

- **`TELEGRAM_BOT_TOKEN`**: token do bot Telegram
- **`TELEGRAM_CHAT_ID`**: chat ID (usuário ou grupo)
- **`USE_TELEGRAM_ALERT`**: `"1"` para ativar, `"0"` para desativar

Exemplo de `.env`:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCDEF...
TELEGRAM_CHAT_ID=123456789
USE_TELEGRAM_ALERT=1
```

Exemplo com variáveis no PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN = "<seu_token_aqui>"
$env:TELEGRAM_CHAT_ID = "<seu_chat_id>"
$env:USE_TELEGRAM_ALERT = "1"  # 0 para desativar
```

---

## Execução manual do monitoramento

No Windows (PowerShell), na raiz do projeto:

```powershell
python .\monitoramento.py
```

No Linux:

```bash
python3 monitoramento.py
```

O script irá:

- carregar `lista_sites.json`,
- visitar cada URL com Selenium/Chrome,
- atualizar arquivos de hash em `hashes/`,
- enviar um resumo via Telegram (se configurado).

---

## Geração de executável standalone (PyInstaller)

O projeto inclui um script `build_monitoramento_exe.py` que automatiza a criação de um executável único do `monitoramento.py`, pronto para distribuição.

### O que o script de build faz

Ao rodar:

```powershell
python build_monitoramento_exe.py
```

ele:

- **limpa** as pastas `dist/` e `build/` antes de cada build;
- roda o **PyInstaller** diretamente (sem depender de arquivo `.spec`);
- gera um executável único a partir de `monitoramento.py`;
- cria uma pasta final (por padrão `dist/monitoramento_app/`) contendo:
  - o executável:
    - no Windows: `monitoramento.exe`
    - no Linux: `monitoramento` (sem `.exe`)
  - o arquivo `.env` (se existir na raiz do projeto),
  - o arquivo `lista_sites.json`.

No final, a estrutura fica assim:

```text
dist/
  monitoramento_app/
    monitoramento(.exe)
    .env
    lista_sites.json
```

Essa pasta `dist/monitoramento_app/` é o **pacote completo** que você pode copiar para outra máquina e executar diretamente.  
Na primeira execução em cada máquina, a pasta `hashes/` será criada automaticamente pelo `monitoramento.py`, e os arquivos de hash serão gerados pela primeira vez para cada site monitorado.

### Requisitos para usar o script de build

- Dependências Python instaladas:

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

- Navegador compatível com o Selenium:
  - normalmente **Google Chrome** (ou Chromium) + `webdriver-manager` (já listado em `requirements.txt`).

### Como rodar o build

No Windows (PowerShell):

```powershell
cd C:\caminho\para\ORF
.\venvautomatizacao\Scripts\activate
python build_monitoramento_exe.py
```

No Linux:

```bash
cd /caminho/para/ORF
source venvautomatizacao/bin/activate  # se você tiver um venv copiado/criado
python3 build_monitoramento_exe.py
```

Depois disso, basta entrar na pasta `dist/monitoramento/` e executar o binário gerado.

---

## Agendamento no Linux com `crontab` (`executar_monitoramento.sh`)

O arquivo `executar_monitoramento.sh` foi feito para rodar o monitoramento em produção/servidor, com log automático:

```bash
#!/usr/bin/env bash

BASE_DIR="/home/admin/monitoramento-site"
PYTHON="$BASE_DIR/venvautomatizacao/bin/python3"
SCRIPT="$BASE_DIR/monitoramento.py"
LOG_DIR="$BASE_DIR/logs"
...
"$PYTHON" "$SCRIPT" >> "$LOG_FILE" 2>&1
```

### 1. Ajustar caminhos

- **`BASE_DIR`**: caminho da pasta do projeto no servidor (por exemplo: `/opt/monitoramento-site`).
- **`PYTHON`**: interpretador Python do virtualenv (ou do sistema), compatível com as libs do projeto.
- **`SCRIPT`**: caminho absoluto para `monitoramento.py`.
- **`LOG_DIR`**: pasta onde serão gravados os logs (o script já cria se não existir).

Exemplo de ajuste para `/opt/monitoramento-site`:

```bash
BASE_DIR="/opt/monitoramento-site"
PYTHON="$BASE_DIR/venvautomatizacao/bin/python3"
SCRIPT="$BASE_DIR/monitoramento.py"
LOG_DIR="$BASE_DIR/logs"
```

### 2. Dar permissão de execução

Na raiz do projeto no servidor:

```bash
chmod +x executar_monitoramento.sh
```

### 3. Criar entrada no `crontab`

Edite o `crontab` do usuário que vai executar o script:

```bash
crontab -e
```

Exemplos de agendamento:

- **A cada 15 minutos**:

```bash
*/15 * * * * /opt/monitoramento-site/executar_monitoramento.sh
```

- **De hora em hora, entre 8h e 18h (dias úteis)**:

```bash
0 8-18 * * 1-5 /opt/monitoramento-site/executar_monitoramento.sh
```

> **Importante:**  
> - Use o caminho **absoluto** para o script.  
> - O script já faz `cd "$BASE_DIR"` e grava logs em `logs/monitoramento_YYYYMMDD_HHMMSS.log`.

### 4. Verificar logs

Depois que o cron rodar, verifique a pasta de logs:

```bash
ls /opt/monitoramento-site/logs
tail -n 100 /opt/monitoramento-site/logs/monitoramento_2025....log
```

---

## Web app para gerenciar a lista de sites

O web app (`app.py`) é um **painel simples em Flask** para cadastrar/remover URLs, atualizando diretamente o `lista_sites.json` usado por `monitoramento.py`.

### Endpoints principais

- **UI**
  - `GET /` → renderiza `templates/index.html` (interface web).
- **API**
  - `GET /api/sites` → retorna lista de URLs em JSON.
  - `POST /api/sites` → adiciona uma URL.
  - `DELETE /api/sites` → remove uma URL.

Internamente, o app usa:

- `monitoramento.load_sites_from_json()` e
- `monitoramento.save_sites_to_json(sites)`

para ler/escrever `lista_sites.json` (arquivo compartilhado com o monitoramento).

### Subir o servidor Flask

No Windows (PowerShell), na raiz:

```powershell
# (opcional) ativar virtualenv
# .\venvautomatizacao\Scripts\Activate.ps1

python .\app.py
```

No Linux:

```bash
# (opcional) source venvautomatizacao/bin/activate
python3 app.py
```

O servidor ouvirá, por padrão:

- `http://localhost:5000/`

---

## Usando o web app para adicionar/remover sites

### Interface web (`/`)

Abra no browser:

- `http://localhost:5000/`

Na tela principal:

- **“Sites monitorados: N”** → contador de URLs atuais.
- **Formulário “Nova URL”**:
  - Campo de texto: `https://exemplo.com`
  - Botão **“Adicionar”**

**Fluxo para adicionar:**

1. Digite a URL completa no campo (ex: `https://cma.eb.mil.br`).
2. Clique em **“Adicionar”**.
3. Se a URL for válida e não duplicada:
   - ela é inserida no topo da lista,
   - o contador é atualizado,
   - `lista_sites.json` é salvo automaticamente.

**Fluxo para remover:**

1. Na lista de sites, cada item aparece assim:
   - `1. https://exemplo.com    [Remover]`
2. Clique em **“Remover”**.
3. Confirme no diálogo do navegador.
4. A URL é removida da lista e de `lista_sites.json`.

Após essas operações, o próximo `monitoramento.py` (manual ou via cron) usará essa lista atualizada.

### Exemplos de uso via API (para integrações)

**Listar sites:**

```bash
curl http://localhost:5000/api/sites
```

**Adicionar site:**

```bash
curl -X POST http://localhost:5000/api/sites \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com"}'
```

Respostas possíveis:

- **200 OK** (sucesso):

  ```json
  {
    "success": true,
    "sites": ["https://exemplo.com", "..."]
  }
  ```

- **400 Bad Request** (URL vazia):

  ```json
  { "error": "URL obrigatória" }
  ```

- **409 Conflict** (URL já cadastrada):

  ```json
  { "error": "URL já cadastrada" }
  ```

**Remover site:**

```bash
curl -X DELETE http://localhost:5000/api/sites \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com"}'
```

- **200 OK**:

  ```json
  {
    "success": true,
    "sites": ["..."]
  }
  ```

- **404 Not Found** (URL inexistente):

  ```json
  { "error": "URL inexistente" }
  ```

---

## Integração entre monitoramento, JSON e web app

- **`lista_sites.json`** é a **fonte de verdade** para os sites monitorados.
- **`monitoramento.py`**:
  - usa `load_sites_from_json()` para obter a lista.
  - salva hashes individuais por URL em `hashes/`.
- **`app.py`**:
  - expõe UI e API para manipular `lista_sites.json`.
  - mantém compatibilidade total com o módulo de monitoramento.

Fluxo típico em produção:

1. Dev/operador usa o web app (`http://servidor:5000/`) para manter a lista.
2. `crontab` executa periodicamente `executar_monitoramento.sh`.
3. `monitoramento.py` lê `lista_sites.json`, monitora e envia alertas Telegram/logs.

---

## Push para GitHub

Para enviar o projeto para o repositório GitHub use:

```powershell
git init
git branch -M main
git remote add origin https://github.com/tuco2905/ORF.git
git add .
git commit -m "Primeira versão: monitoramento de múltiplos sites"
git push -u origin main
```

---

## Problemas comuns

- Se o Python não estiver no PATH, adicione-o ou execute pelo caminho completo do interpretador.
- Se houver erros na importação de `webdriver_manager` ou `bs4`, instale as dependências conforme `requirements.txt`.
- Se o Git não estiver instalado, baixe em: <https://git-scm.com/download/win>
