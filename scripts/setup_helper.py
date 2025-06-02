import os
import sys
import requests
import subprocess
import importlib.util
from tqdm import tqdm

# Constantes
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_DEST = os.path.join("data", "models", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
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
    packages = ['python-dotenv', 'openai', 'ctransformers', 'gradio']
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
            f.write("# Configuracoes do GesonelBot\n")
            f.write("MODEL_TYPE=local\n")
            f.write("LOCAL_MODEL_NAME=tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf\n")
            f.write("# Para usar OpenAI, adicione sua chave API abaixo e mude MODEL_TYPE para 'openai'\n")
            f.write("# OPENAI_API_KEY=sua_chave_aqui\n")
            f.write("# OPENAI_MODEL=gpt-3.5-turbo\n")
    return True

# Baixar modelo se não existir
def download_model():
    if os.path.exists(MODEL_DEST):
        print(f"\nModelo local já existe em: {MODEL_DEST}")
        print("Modelo encontrado, pulando download.")
        return True
    
    print("\n============================================")
    print("Baixando modelo local (necessário para modo offline)...")
    print("============================================")
    
    print(f"Baixando modelo de {MODEL_URL}")
    print(f"Destino: {MODEL_DEST}")
    print("Tamanho aproximado: 700MB")
    print("Este processo pode demorar alguns minutos...\n")
    
    try:
        response = requests.get(MODEL_URL, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        
        with open(MODEL_DEST, 'wb') as f:
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
            for chunk in response.iter_content(block_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
            progress_bar.close()
        
        if os.path.exists(MODEL_DEST):
            print("\nModelo baixado com sucesso!")
            return True
        else:
            print("\nERRO: Falha ao baixar o modelo.")
            return False
    except Exception as e:
        print(f"\nERRO ao baixar o modelo: {str(e)}")
        return False

# Verificar se o modelo local é necessário e está disponível
def check_model_availability():
    # Aqui tentamos importar as configurações, mas se falhar (por exemplo, na primeira execução)
    # assumimos que o modelo local será necessário
    try:
        sys.path.append(os.getcwd())
        from gesonelbot.config.settings import MODEL_TYPE, LOCAL_MODEL_PATH
        if MODEL_TYPE == 'local':
            if not os.path.exists(LOCAL_MODEL_PATH):
                print("Modelo local configurado, mas arquivo não encontrado.")
                return download_model()
    except (ImportError, ModuleNotFoundError):
        # Se não conseguimos importar as configurações, verificamos se o modelo padrão existe
        if not os.path.exists(MODEL_DEST):
            print("Configurações não encontradas, verificando modelo padrão.")
            return download_model()
    
    return True

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
    
    if not download_model():
        print("AVISO: Modelo não foi baixado, mas a configuração continuará.")
    
    if not install_all_deps():
        print("AVISO: Algumas dependências podem não ter sido instaladas.")
    
    print("\n============================================")
    print("Configuração concluída com sucesso!")
    print("\nPara usar o GesonelBot:")
    print("1. Execute scripts\\run.bat para iniciar o chatbot")
    print("2. Adicione seus documentos na pasta data\\docs")
    print("\nPara alternar entre modos online/offline:")
    print("- Edite o arquivo .env e altere MODEL_TYPE entre \"local\" e \"openai\"")
    print("- Ou use a aba Configurações na interface do GesonelBot")
    print("============================================")
    
    return True

# Usado pelo script run.bat
def prepare_for_run():
    success = True
    
    # Verificar dependências críticas
    if not check_critical_deps():
        success = False
    
    # Verificar disponibilidade do modelo
    if not check_model_availability():
        success = False
    
    return success

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            return setup()
        elif sys.argv[1] == "prepare":
            return prepare_for_run()
        elif sys.argv[1] == "download":
            return download_model()
    else:
        # Comportamento padrão (executado quando chamado sem argumentos)
        return setup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 