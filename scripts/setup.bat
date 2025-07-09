@echo off
echo ===============================================
echo Configurando ambiente para GesonelBot
echo ===============================================
echo.

:: Verificar se Python está instalado
python --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Python nao encontrado. Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

:: Criar ambiente virtual
echo Criando ambiente virtual...
if exist venv (
    echo Ambiente virtual ja existe. Deseja recria-lo? (S/N)
    choice /C SN /M "Recriar ambiente virtual"
    if !ERRORLEVEL! EQU 1 (
        echo Removendo ambiente virtual antigo...
        rmdir /s /q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)

:: Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip

:: Instalar as dependências
echo Instalando dependencias...
pip install -r requirements.txt

:: Criar diretórios necessários
echo Criando diretorios do projeto...
mkdir data\docs 2>nul
mkdir data\indexes 2>nul
mkdir data\models 2>nul
mkdir data\logs 2>nul
mkdir data\indexes\vectorstore 2>nul

:: Baixar modelo TinyLlama se o usuário desejar
echo.
echo Deseja baixar o modelo TinyLlama agora? (Recomendado)
echo Isso vai ocupar aproximadamente 2GB de espaço em disco.
choice /C SN /M "Baixar modelo agora"
if %ERRORLEVEL% EQU 1 (
    echo.
    echo Baixando o modelo TinyLlama. Isso pode levar alguns minutos...
    python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; tokenizer = AutoTokenizer.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0'); model = AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0', device_map='auto', load_in_8bit=True)"
    echo Modelo baixado com sucesso!
) else (
    echo Modelo não será baixado agora. Ele será baixado automaticamente na primeira execução.
)

:: Criar arquivo .env se não existir
if not exist .env (
    echo Criando arquivo .env...
    copy env.example .env
    echo Arquivo .env criado. Por favor, verifique as configurações.
) else (
    echo Arquivo .env já existe. Verifique se as configurações estão corretas.
)

echo.
echo ===============================================
echo Configuração concluída!
echo.
echo Para executar o GesonelBot, utilize:
echo   scripts\executar.bat
echo ===============================================

:: Pausar para o usuário ver a mensagem
pause 