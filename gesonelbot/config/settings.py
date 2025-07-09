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

# Configurações do modelo local
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", os.path.join(DATA_DIR, "models"))
USE_8BIT_QUANTIZATION = os.getenv("USE_8BIT_QUANTIZATION", "True").lower() in ('true', '1', 't')
USE_4BIT_QUANTIZATION = os.getenv("USE_4BIT_QUANTIZATION", "False").lower() in ('true', '1', 't')
USE_CPU_ONLY = os.getenv("USE_CPU_ONLY", "False").lower() in ('true', '1', 't')

# Configurações de geração de resposta
QA_MAX_TOKENS = int(os.getenv("QA_MAX_TOKENS", "512"))
QA_TEMPERATURE = float(os.getenv("QA_TEMPERATURE", "0.7"))
RETRIEVER_SEARCH_TYPE = os.getenv("RETRIEVER_SEARCH_TYPE", "similarity")  # similarity, mmr, threshold
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "4"))  # Número de documentos a serem recuperados
RETRIEVER_THRESHOLD = float(os.getenv("RETRIEVER_THRESHOLD", "0.7"))  # Limiar de similaridade

# Templates de prompts
SYSTEM_TEMPLATE = os.getenv("SYSTEM_TEMPLATE", """Você é um assistente de IA chamado {app_name}, especializado em responder perguntas com base em documentos.

INSTRUÇÕES IMPORTANTES:
1. Use APENAS as informações contidas nos documentos fornecidos para responder às perguntas.
2. Se a informação não estiver presente nos documentos, diga uma resposta simples e direta, por exemplo se um usuário perguntar se você sabe conjurar magia, responda: "Não sei conjurar magia, Estou aqui para responder perguntas sobre os documentos fornecidos" ou se perguntar "olá tudo bem com você?" responda: "Estou bem! E você? Estou aqui para responder perguntas sobre os documentos fornecidos".
3. NÃO invente informações ou use seu conhecimento geral quando os documentos não contêm a resposta.
4. Cite as fontes específicas dos documentos de onde extraiu as informações, somente dos DOCUMENTOS QUE VOCÊ EXTRAIU AS INFORMAÇÕES, não cite fontes de outros documentos caso não tenha extraído informações de outros documentos.
5. Forneça respostas Objetivas e precisas quando os documentos contiverem as informações solicitadas.
6. Analise cuidadosamente todo o conteúdo dos documentos antes de responder.
""")

USER_TEMPLATE = os.getenv("USER_TEMPLATE", "padrao")
if USER_TEMPLATE == "padrao":
    USER_TEMPLATE = """Documentos relevantes:
{context}

Pergunta: {query}
"""

# Configurações da interface de usuário
UI_TITLE = os.getenv("UI_TITLE", APP_NAME)
UI_SUBTITLE = os.getenv("UI_SUBTITLE", APP_DESCRIPTION)
UI_THEME = os.getenv("UI_THEME", "light")  # light ou dark
UI_PRIMARY_COLOR = os.getenv("UI_PRIMARY_COLOR", "#2563eb")  # Azul por padrão

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_DEBUG_LOGGING = os.getenv("ENABLE_DEBUG_LOGGING", "False").lower() in ('true', '1', 't')

# Ajustar nível de logging se necessário
if ENABLE_DEBUG_LOGGING:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL))

# Função para verificar se as configurações necessárias estão presentes
def verify_config():
    """
    Verifica se todas as configurações necessárias estão presentes.
    """
    all_ok = True
    
    # Verificar diretórios
    for dir_path in [DATA_DIR, DOCS_DIR, INDEXES_DIR, MODELS_DIR, LOGS_DIR]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Diretório criado: {dir_path}")
            except Exception as e:
                print(f"AVISO: Não foi possível criar o diretório {dir_path}: {str(e)}")
                all_ok = False
    
    return all_ok 