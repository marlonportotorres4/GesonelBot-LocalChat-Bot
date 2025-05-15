@echo off
echo ===================================================
echo    Configurando ambiente para o GesonelBot
echo ===================================================
echo.

:: Verificar Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python nao encontrado. Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

:: Criar ambiente virtual
echo Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo Erro ao criar ambiente virtual. Verifique sua instalacao do Python.
    pause
    exit /b 1
)

:: Ativar ambiente virtual e instalar dependências
echo Instalando dependencias...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Erro ao instalar dependencias. Verifique o arquivo requirements.txt.
    pause
    exit /b 1
)

:: Criar arquivo .env a partir do exemplo, se não existir
if not exist .env (
    if exist env.example (
        echo Criando arquivo .env a partir do modelo...
        copy env.example .env
    ) else (
        echo AVISO: Arquivo env.example nao encontrado. Voce precisara criar o arquivo .env manualmente.
    )
)

echo.
echo ===================================================
echo Instalacao concluida com sucesso!
echo.
echo Para executar o GesonelBot:
echo   1. Execute o arquivo 'executar.bat'
echo   2. Ou, a partir da linha de comando: 
echo      - venv\Scripts\activate
echo      - python gesonelbot.py
echo ===================================================
echo.

pause 