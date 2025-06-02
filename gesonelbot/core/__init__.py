"""
Núcleo de funcionalidades do GesonelBot
 
Este módulo contém as funcionalidades centrais do GesonelBot:
- Processamento de documentos
- Motor de perguntas e respostas
- Gerenciamento de banco de dados vetorial
- Gerenciamento de embeddings
- Sistema de recuperação de informações
- Gerenciamento de modelos de linguagem
"""

# Exportar componentes principais para facilitar importação
from gesonelbot.core.document_processor import ingest_documents, get_processed_documents_info
from gesonelbot.core.qa_engine import answer_question, get_model_info, list_available_models
from gesonelbot.core.embeddings_manager import embeddings_manager
from gesonelbot.core.retriever import document_retriever
from gesonelbot.core.llm_manager import llm_manager 