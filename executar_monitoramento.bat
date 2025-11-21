@echo off
setlocal

rem Caminho base do projeto
set "BASE_DIR=C:\Users\Administrador\Documents\bruce-orf\programacao\ORF"
set "PYTHON=%BASE_DIR%\venvautomatizacao\Scripts\python.exe"
set "SCRIPT=%BASE_DIR%\monitoramento.py"
set "LOG_DIR=%BASE_DIR%\logs"

if not exist "%PYTHON%" (
    echo Nao foi encontrado o interpretador Python esperado em:
    echo   %PYTHON%
    echo Verifique a instalacao do ambiente virtual antes de continuar.
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo Nao foi encontrado o script monitoramento.py em:
    echo   %SCRIPT%
    exit /b 1
)

if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "timestamp=%%I"
set "LOG_FILE=%LOG_DIR%\monitoramento_%timestamp%.log"

cd /d "%BASE_DIR%"
echo [%date% %time%] Iniciando monitoramento >> "%LOG_FILE%"
"%PYTHON%" "%SCRIPT%" >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo [%date% %time%] Finalizado com codigo %EXIT_CODE% >> "%LOG_FILE%"

endlocal & exit /b %EXIT_CODE%

