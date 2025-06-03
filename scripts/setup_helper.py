import os
import sys
import subprocess
import importlib.util
from tqdm import tqdm

# Constantes
ENV_FILE = ".env"
REQUIREMENTS_FILE = "requirements.txt"

# Verificar se o Python está instalado (já deve estar se este script está rodando)
def check_python():
    print("Verificando versão do Python...")
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 8):
        print(f"ERRO: Python 3.8 ou superior é necessário. Versão atual: {major}.{minor}")
        return False
    print(f"Python {major}.{minor} encontrado.")
    return True

# Criar ou ativar ambiente virtual
def setup_venv():
    if not os.path.exists("venv"):
        print("Criando ambiente virtual...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"ERRO ao criar ambiente virtual: {str(e)}")
            return False
    
    # Ativar o ambiente virtual não é possível diretamente do Python
    # Isso será feito pelo script batch
    print("Ambiente virtual pronto.")
    return True

# Instalar dependências básicas
def install_basic_deps():
    print("Instalando dependências básicas...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "tqdm", "colorama", "python-dotenv"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao instalar dependências básicas: {str(e)}")
        return False

# Instalar todas as dependências do projeto
def install_all_deps():
    if os.path.exists(REQUIREMENTS_FILE):
        print("Instalando todas as dependências do projeto...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERRO ao instalar dependências do projeto: {str(e)}")
            return False
    else:
        print(f"AVISO: Arquivo {REQUIREMENTS_FILE} não encontrado.")
        return False

# Verificar dependências críticas para execução
def check_critical_deps():
    print("Verificando dependências críticas...")
    packages = ['python-dotenv', 'together', 'gradio', 'langchain']
    missing = []
    
    for package in packages:
        if importlib.util.find_spec(package.replace('-', '_')) is None:
            missing.append(package)
    
    if missing:
        print(f"Dependências faltando: {', '.join(missing)}")
        print("Instalando dependências críticas...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERRO ao instalar dependências críticas: {str(e)}")
            return False
    else:
        print("Todas as dependências críticas estão instaladas.")
        return True

# Criar estrutura de diretórios
def create_directories():
    print("Criando estrutura de diretórios...")
    directories = [
        os.path.join("data"),
        os.path.join("data", "docs"),
        os.path.join("data", "indexes"),
        os.path.join("data", "models"),
        os.path.join("data", "logs")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    return True

# Criar arquivo .env se não existir
def create_env_file():
    if not os.path.exists(ENV_FILE):
        print("Criando arquivo de configuração .env...")
        with open(ENV_FILE, "w") as f:
            f.write("# Configurações do GesonelBot\n")
            f.write("# API Provider\n")
            f.write("API_PROVIDER=together\n\n")
            f.write("# Chave API da Together.ai\n")
            f.write("TOGETHER_API_KEY=\n")
            f.write("TOGETHER_MODEL=lgai/exaone-3-5-32b-instruct\n\n")
    return True

# Verificar configuração da API
def check_api_config():
    print("\n============================================")
    print("Verificando configuração da API...")
    print("============================================")
    
    try:
        import dotenv
        dotenv.load_dotenv(ENV_FILE)
        
        together_api_key = os.getenv("TOGETHER_API_KEY")
        
        if not together_api_key:
            print("\nAVISO: Chave API da Together.ai não configurada!")
            print("Por favor, edite o arquivo .env e adicione sua chave TOGETHER_API_KEY.")
            print("Você pode obter uma chave em: https://api.together.xyz/settings/api-keys")
            return False
        else:
            print("\nChave API da Together.ai encontrada!")
            return True
    except Exception as e:
        print(f"\nERRO ao verificar configuração da API: {str(e)}")
        return False

# Configuração inicial completa (usado pelo script setup.bat)
def setup():
    if not check_python():
        return False
    
    if not setup_venv():
        return False
    
    if not install_basic_deps():
        return False
    
    if not create_directories():
        return False
    
    if not create_env_file():
        return False
    
    if not install_all_deps():
        print("AVISO: Algumas dependências podem não ter sido instaladas.")
    
    if not check_api_config():
        print("AVISO: Configuração da API incompleta.")
    
    print("\n============================================")
    print("Configuração concluída com sucesso!")
    print("\nPara usar o GesonelBot:")
    print("1. Certifique-se de que sua chave API está configurada no arquivo .env")
    print("2. Execute gesonelbot.py para iniciar o chatbot")
    print("3. Adicione seus documentos na pasta data\\docs")
    print("============================================")
    
    return True

# Usado pelo script run.bat
def prepare_for_run():
    success = True
    
    # Verificar dependências críticas
    if not check_critical_deps():
        success = False
    
    # Verificar configuração da API
    if not check_api_config():
        success = False
    
    return success

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            return setup()
        elif sys.argv[1] == "prepare":
            return prepare_for_run()
    else:
        # Comportamento padrão (executado quando chamado sem argumentos)
        return setup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 