@echo off
echo ============================================
echo GesonelBot - Assistente de IA Local
echo ============================================
echo.

REM Verificar se o ambiente virtual existe, caso contrário, fazer setup completo
if not exist venv (
    echo Primeira execucao detectada, realizando configuracao inicial...
    echo.
    python scripts\setup_helper.py setup
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERRO: Falha na configuracao inicial.
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Preparar ambiente para execução (verificar dependências e modelo)
echo Preparando ambiente para execucao...
python scripts\setup_helper.py prepare
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo AVISO: Houve um problema ao preparar o ambiente.
    echo O aplicativo pode nao funcionar corretamente.
    echo Sem o modelo local, voce pode configurar a OpenAI no arquivo .env:
    echo 1. Edite o arquivo .env
    echo 2. Altere MODEL_TYPE=openai
    echo 3. Adicione sua chave API: OPENAI_API_KEY=sua_chave_aqui
    echo.
    pause
)

REM Iniciar a aplicação
echo Iniciando GesonelBot...
python gesonelbot.py

pause 