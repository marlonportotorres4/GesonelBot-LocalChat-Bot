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
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Diretório de dados
DATA_DIR = os.path.join(BASE_DIR, "gesonelbot", "data")

# Configurações de pastas
UPLOAD_DIR = os.path.join(DATA_DIR, "uploaded_docs")
VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstore")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Garantir que as pastas existam
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Configurações da aplicação (carregadas do .env se disponível)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))
MAX_FILES = int(os.getenv("MAX_FILES", 10))

# Configurações do modelo
MODEL_TYPE = os.getenv("MODEL_TYPE", "local")  # local, openai, huggingface
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", os.path.join(MODELS_DIR, "local_model"))

# Configurações de embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "local")  # local, openai, ou um nome específico de modelo HF
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 384))  # Dimensão padrão para all-MiniLM-L6-v2

# Configurações do banco de dados vetorial
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "gesonelbot_docs")
DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", "cosine")  # cosine, l2, ip

# Configurações de processamento de documentos
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))  # Tamanho do chunk em caracteres
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))  # Sobreposição entre chunks

# Configurações do retriever (sistema de recuperação de informações)
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", 4))  # Número de documentos a recuperar
RETRIEVER_SEARCH_TYPE = os.getenv("RETRIEVER_SEARCH_TYPE", "similarity")  # similarity, mmr, similarity_score_threshold
RETRIEVER_SCORE_THRESHOLD = float(os.getenv("RETRIEVER_SCORE_THRESHOLD", 0.5))  # Limite de score para similaridade

# Configurações de LLM para QA
QA_PROMPT_TEMPLATE = os.getenv("QA_PROMPT_TEMPLATE", "padrao")  # Nome do template de prompt a usar
QA_TEMPERATURE = float(os.getenv("QA_TEMPERATURE", 0.1))  # Temperatura para geração (menor = mais determinístico)
QA_MAX_TOKENS = int(os.getenv("QA_MAX_TOKENS", 512))  # Máximo de tokens na resposta

# Configurações da OpenAI (se aplicável)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Configurações de logging
ENABLE_DEBUG_LOGGING = os.getenv("ENABLE_DEBUG_LOGGING", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Função para verificar se as configurações necessárias estão presentes
def verify_config():
    """
    Verifica se todas as configurações necessárias estão presentes.
    """
    all_ok = True
    
    # Verificar API keys se necessário
    if MODEL_TYPE == "openai" and not OPENAI_API_KEY:
        print("AVISO: Modelo OpenAI selecionado, mas OPENAI_API_KEY não configurada no arquivo .env")
        all_ok = False
        
    if EMBEDDING_MODEL == "openai" and not OPENAI_API_KEY:
        print("AVISO: Embeddings OpenAI selecionados, mas OPENAI_API_KEY não configurada no arquivo .env")
        all_ok = False
    
    # Verificar diretórios
    for dir_path in [UPLOAD_DIR, VECTORSTORE_DIR, MODELS_DIR]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Diretório criado: {dir_path}")
            except Exception as e:
                print(f"AVISO: Não foi possível criar o diretório {dir_path}: {str(e)}")
                all_ok = False
    
    return all_ok 