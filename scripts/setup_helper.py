"""
Configuração inicial do GesonelBot.

Este script ajuda na instalação e configuração inicial do GesonelBot.
"""
import os
import sys
import shutil
import subprocess
import importlib.util
from tqdm import tqdm
from pathlib import Path

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
    """Executa a configuração inicial do GesonelBot."""
    print("=" * 50)
    print(" 📚 GesonelBot - Assistente Local de Documentos")
    print("=" * 50)
    print("\nBem-vindo ao assistente de configuração do GesonelBot!")
    print("\nEste script irá ajudá-lo a configurar o ambiente necessário para executar o GesonelBot.")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("\n❌ Versão do Python incompatível!")
        print(f"Versão atual: {python_version.major}.{python_version.minor}.{python_version.micro}")
        print("GesonelBot requer Python 3.8 ou superior.")
        sys.exit(1)
    else:
        print(f"\n✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detectado.")
    
    # Criar diretórios
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    docs_dir = data_dir / "docs"
    indexes_dir = data_dir / "indexes"
    models_dir = data_dir / "models"
    vectorstore_dir = indexes_dir / "vectorstore"
    
    print("\nCriando diretórios necessários...")
    
    for directory in [data_dir, docs_dir, indexes_dir, models_dir, vectorstore_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório criado: {directory}")
    
    # Criar ambiente virtual
    print("\nDeseja criar um ambiente virtual Python para o GesonelBot?")
    choice = input("Isso é recomendado para isolar as dependências [S/n]: ").strip().lower()
    
    if choice in ['', 's', 'sim', 'y', 'yes']:
        print("\nCriando ambiente virtual...")
        venv_dir = base_dir / "venv"
        
        # Verificar se já existe
        if venv_dir.exists():
            print("Um ambiente virtual já existe. Deseja recriá-lo?")
            recreate = input("Isso irá remover o ambiente existente [s/N]: ").strip().lower()
            
            if recreate in ['s', 'sim', 'y', 'yes']:
                print("Removendo ambiente virtual existente...")
                shutil.rmtree(venv_dir)
            else:
                print("Mantendo ambiente virtual existente.")
                venv_dir = None
        
        # Criar novo ambiente se necessário
        if venv_dir:
            try:
                subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
                print("✅ Ambiente virtual criado com sucesso!")
                
                # Determinar o script de ativação
                if os.name == 'nt':  # Windows
                    activate_script = venv_dir / "Scripts" / "activate.bat"
                    pip_path = venv_dir / "Scripts" / "pip"
                else:  # Unix/Linux/Mac
                    activate_script = venv_dir / "bin" / "activate"
                    pip_path = venv_dir / "bin" / "pip"
                
                print(f"\nPara ativar o ambiente virtual, execute:")
                if os.name == 'nt':
                    print(f"    {activate_script}")
                else:
                    print(f"    source {activate_script}")
            except Exception as e:
                print(f"❌ Erro ao criar ambiente virtual: {str(e)}")
    else:
        print("Pulando a criação do ambiente virtual.")
    
    # Instalar dependências
    print("\nDeseja instalar as dependências necessárias?")
    choice = input("Isso instalará as bibliotecas Python requeridas pelo GesonelBot [S/n]: ").strip().lower()
    
    if choice in ['', 's', 'sim', 'y', 'yes']:
        print("\nInstalando dependências...")
        try:
            packages = ['python-dotenv', 'transformers', 'torch', 'gradio', 'langchain', 'langchain_community', 'sentence-transformers', 'chromadb']
            
            # Usar pip do ambiente virtual, se foi criado
            if 'venv_dir' in locals() and venv_dir:
                if os.name == 'nt':  # Windows
                    pip_cmd = str(venv_dir / "Scripts" / "pip")
                else:  # Unix/Linux/Mac
                    pip_cmd = str(venv_dir / "bin" / "pip")
            else:
                pip_cmd = "pip"
            
            # Atualizar pip primeiro
            subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
            
            # Instalar cada pacote separadamente para melhor tratamento de erros
            for package in packages:
                print(f"Instalando {package}...")
                subprocess.run([pip_cmd, "install", package], check=True)
            
            print("✅ Dependências instaladas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao instalar dependências: {str(e)}")
            print("\nVocê pode instalá-las manualmente com:")
            print("    pip install -r requirements.txt")
    else:
        print("Pulando a instalação de dependências.")
    
    # Configurar arquivo .env
    env_file = base_dir / ".env"
    env_example = base_dir / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("\nArquivo .env não encontrado. Deseja criar um com as configurações padrão?")
        choice = input("Isso criará o arquivo .env necessário para o GesonelBot [S/n]: ").strip().lower()
        
        if choice in ['', 's', 'sim', 'y', 'yes']:
            print("\nCriando arquivo .env...")
            try:
                shutil.copy(env_example, env_file)
                print("✅ Arquivo .env criado com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao criar arquivo .env: {str(e)}")
                print(f"Por favor, copie manualmente o arquivo {env_example} para {env_file}")
    else:
        print("\nArquivo .env já existe. Mantendo configurações existentes.")
    
    # Verificar modelo TinyLlama
    print("\nDeseja baixar o modelo TinyLlama agora?")
    print("Isso ocupará aproximadamente 2GB de espaço em disco.")
    choice = input("O download é recomendado para um funcionamento mais rápido na primeira execução [S/n]: ").strip().lower()
    
    if choice in ['', 's', 'sim', 'y', 'yes']:
        print("\nBaixando modelo TinyLlama. Isso pode levar alguns minutos...")
        try:
            # Comando para baixar o modelo usando a biblioteca Transformers
            download_cmd = (
                "from transformers import AutoTokenizer, AutoModelForCausalLM; "
                "tokenizer = AutoTokenizer.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0'); "
                "model = AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0', device_map='auto', load_in_8bit=True)"
            )
            
            # Executar comando usando o Python do ambiente virtual, se disponível
            if 'venv_dir' in locals() and venv_dir:
                if os.name == 'nt':  # Windows
                    python_cmd = str(venv_dir / "Scripts" / "python")
                else:  # Unix/Linux/Mac
                    python_cmd = str(venv_dir / "bin" / "python")
            else:
                python_cmd = sys.executable
            
            subprocess.run([python_cmd, "-c", download_cmd], check=True)
            print("✅ Modelo TinyLlama baixado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao baixar o modelo: {str(e)}")
            print("O modelo será baixado automaticamente na primeira execução do GesonelBot.")
    else:
        print("Pulando o download do modelo.")
    
    # Concluir
    print("\n" + "=" * 50)
    print(" 🎉 Configuração do GesonelBot concluída!")
    print("=" * 50)
    print("\nPara iniciar o GesonelBot, execute:")
    print("    python gesonelbot.py")
    print("\nOu use o script batch no Windows:")
    print("    scripts\\executar.bat")

if __name__ == "__main__":
    main() 