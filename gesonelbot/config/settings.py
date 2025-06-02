"""
Configurações do GesonelBot.

Este módulo contém todas as configurações e parâmetros do sistema,
carregados do arquivo .env e com valores padrão quando não definidos.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "docs")
INDEXES_DIR = os.path.join(DATA_DIR, "indexes")
MODELS_DIR = os.path.join(DATA_DIR, "models")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
VECTORSTORE_DIR = os.path.join(INDEXES_DIR, "vectorstore")

# Garantir que os diretórios existam
for directory in [DATA_DIR, DOCS_DIR, INDEXES_DIR, MODELS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configurações gerais
APP_NAME = os.getenv("APP_NAME", "GesonelBot")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Assistente de IA para responder perguntas com base em documentos locais")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ('true', '1', 't')

# Configurações de documentos
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md', '.csv', '.json', '.html']

# Configurações do modelo de embeddings
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
EMBEDDINGS_DIMENSIONS = int(os.getenv("EMBEDDINGS_DIMENSIONS", "384"))
EMBEDDINGS_NORMALIZE = os.getenv("EMBEDDINGS_NORMALIZE", "True").lower() in ('true', '1', 't')

# Configurações do modelo de linguagem (LLM)
MODEL_TYPE = os.getenv("MODEL_TYPE", "local")  # 'local' ou 'openai'

# Configurações para API da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Configurações para modelo local
LOCAL_MODEL_TYPE = os.getenv("LOCAL_MODEL_TYPE", "llama")  # llama é o padrão para TinyLlama
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
LOCAL_MODEL_PATH = os.path.join(MODELS_DIR, LOCAL_MODEL_NAME)

# Configurações de geração de resposta
QA_MAX_TOKENS = int(os.getenv("QA_MAX_TOKENS", "512"))
QA_TEMPERATURE = float(os.getenv("QA_TEMPERATURE", "0.7"))
RETRIEVER_SEARCH_TYPE = os.getenv("RETRIEVER_SEARCH_TYPE", "similarity")  # similarity, mmr, threshold
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "4"))  # Número de documentos a serem recuperados
RETRIEVER_THRESHOLD = float(os.getenv("RETRIEVER_THRESHOLD", "0.7"))  # Limiar de similaridade

# Templates de prompts
SYSTEM_TEMPLATE = """Você é um assistente de IA chamado {app_name}. 
Seu objetivo é fornecer respostas precisas com base nos documentos fornecidos.
Use apenas as informações nos documentos para responder. Se não souber a resposta, admita isso claramente.
Seja conciso e direto, mas completo. Não invente informações."""

USER_TEMPLATE = """Documentos relevantes:
{context}

Pergunta: {query}
"""

# Configurações da interface de usuário
UI_TITLE = os.getenv("UI_TITLE", APP_NAME)
UI_SUBTITLE = os.getenv("UI_SUBTITLE", APP_DESCRIPTION)
UI_THEME = os.getenv("UI_THEME", "light")  # light ou dark
UI_PRIMARY_COLOR = os.getenv("UI_PRIMARY_COLOR", "#2563eb")  # Azul por padrão

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
        
    if EMBEDDINGS_MODEL == "openai" and not OPENAI_API_KEY:
        print("AVISO: Embeddings OpenAI selecionados, mas OPENAI_API_KEY não configurada no arquivo .env")
        all_ok = False
    
    # Verificar diretórios
    for dir_path in [DATA_DIR, DOCS_DIR, INDEXES_DIR, MODELS_DIR, LOGS_DIR]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Diretório criado: {dir_path}")
            except Exception as e:
                print(f"AVISO: Não foi possível criar o diretório {dir_path}: {str(e)}")
                all_ok = False
    
    # Verificar modelo local
    if MODEL_TYPE in ["local", "ctransformers", "llama_cpp", "transformers"]:
        if not os.path.exists(LOCAL_MODEL_PATH):
            print(f"AVISO: Modelo local selecionado, mas arquivo não encontrado: {LOCAL_MODEL_PATH}")
            print(f"Você pode baixar um modelo compatível em: {LOCAL_MODEL_PATH}")
            all_ok = False
    
    return all_ok 