"""
Arquivo de configuração para o GesonelBot

Este módulo centraliza as configurações do projeto, carregando 
variáveis de ambiente do arquivo .env.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Tentar carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Configurações de pastas
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_docs")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Garantir que as pastas existam
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Configurações da aplicação (carregadas do .env se disponível)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))
MAX_FILES = int(os.getenv("MAX_FILES", 10))

# Configurações do modelo
MODEL_TYPE = os.getenv("MODEL_TYPE", "local")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", os.path.join(MODELS_DIR, "local_model"))

# Configurações de embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "local")

# Configurações de logging
ENABLE_DEBUG_LOGGING = os.getenv("ENABLE_DEBUG_LOGGING", "False").lower() == "true"

# Função para verificar se as configurações necessárias estão presentes
def verify_config():
    """
    Verifica se todas as configurações necessárias estão presentes.
    """
    if MODEL_TYPE == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("AVISO: Modelo OpenAI selecionado, mas OPENAI_API_KEY não configurada no arquivo .env")
        return False
    return True 