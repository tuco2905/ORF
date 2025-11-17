# Script para inicializar Git e fazer push para GitHub
# Repositório: https://github.com/tuco2905/ORF.git

param(
    [string]$Message = "Atualização do monitoramento: suporte a múltiplos sites e melhorias",
    [switch]$Force = $false
)

$RepoUrl = "https://github.com/tuco2905/ORF.git"
$Branch = "main"

Write-Host "Iniciando push para GitHub..." -ForegroundColor Green
Write-Host "Repositório: $RepoUrl" -ForegroundColor Cyan

# Verificar se Git está instalado
try {
    git --version | Out-Null
    Write-Host "Git encontrado" -ForegroundColor Green
} catch {
    Write-Host "Git não está instalado ou não está no PATH" -ForegroundColor Red
    Write-Host "Instale o Git em: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Inicializar repositório se não existir
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    git branch -M $Branch
} else {
    Write-Host "Repositório Git já existe" -ForegroundColor Green
}

# Configurar remote se não existir
$remoteExists = git remote get-url origin 2>$null
if (-not $remoteExists) {
    Write-Host "Adicionando remote origin..." -ForegroundColor Yellow
    git remote add origin $RepoUrl
} else {
    Write-Host "Remote origin já configurado: $remoteExists" -ForegroundColor Green
    # Verificar se o remote está correto
    if ($remoteExists -ne $RepoUrl) {
        Write-Host "Remote atual difere do esperado. Atualizando..." -ForegroundColor Yellow
        git remote set-url origin $RepoUrl
    }
}

# Adicionar todos os arquivos
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add .

# Verificar se há mudanças para commit
$status = git status --porcelain
if (-not $status) {
    Write-Host "Nenhuma mudança detectada para commit" -ForegroundColor Blue
    if (-not $Force) {
        Write-Host "Use -Force para forçar push mesmo sem mudanças" -ForegroundColor Gray
        exit 0
    }
} else {
    Write-Host "Arquivos modificados:" -ForegroundColor Blue
    $status | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
}

# Fazer commit
Write-Host "Fazendo commit..." -ForegroundColor Yellow
git commit -m $Message

# Fazer push
Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
try {
    git push -u origin $Branch
    Write-Host "Push realizado com sucesso!" -ForegroundColor Green
    Write-Host "Repositório: $RepoUrl" -ForegroundColor Cyan
} catch {
    Write-Host "Erro durante o push. Possíveis causas:" -ForegroundColor Red
    Write-Host "   - Credenciais não configuradas" -ForegroundColor Yellow
    Write-Host "   - Repositório não existe no GitHub" -ForegroundColor Yellow
    Write-Host "   - Sem permissão de escrita" -ForegroundColor Yellow
    Write-Host "" 
    Write-Host "Para configurar credenciais HTTPS:" -ForegroundColor Blue
    Write-Host "   git config --global user.name `"Seu Nome`"" -ForegroundColor Gray
    Write-Host "   git config --global user.email `"seu.email@exemplo.com`"" -ForegroundColor Gray
    Write-Host "   git config --global credential.helper manager-core" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ou configure SSH seguindo: https://docs.github.com/pt/authentication/connecting-to-github-with-ssh" -ForegroundColor Blue
    exit 1
}

Write-Host ""
Write-Host "Processo concluído!" -ForegroundColor Green