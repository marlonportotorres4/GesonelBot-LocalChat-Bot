@echo off
echo ===============================================
echo Iniciando GesonelBot
echo ===============================================
echo.

:: Verificar se o ambiente virtual existe
if not exist venv\Scripts\activate.bat (
    echo Ambiente virtual não encontrado. Execute primeiro o script setup.bat.
    pause
    exit /b 1
)

:: Ativar ambiente virtual
call venv\Scripts\activate.bat

:: Verificar se as pastas essenciais existem
if not exist data\docs (
    mkdir data\docs
    echo Pasta de documentos criada em data\docs
)

if not exist data\indexes\vectorstore (
    mkdir data\indexes\vectorstore
    echo Pasta do banco de dados vetorial criada em data\indexes\vectorstore
)

:: Verificar se o arquivo .env existe
if not exist .env (
    echo Arquivo .env não encontrado. Criando um arquivo .env básico...
    copy env.example .env
    echo.
    echo Arquivo .env criado a partir do exemplo.
)

:: Executar o bot
echo Iniciando GesonelBot...
python gesonelbot.py

:: Manter a janela aberta em caso de erro
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro durante a execução.
    pause
) 