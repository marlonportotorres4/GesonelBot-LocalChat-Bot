"""
Núcleo de funcionalidades do GesonelBot
 
Este módulo contém as funcionalidades centrais do GesonelBot:
- Processamento de documentos
- Motor de perguntas e respostas
- Gerenciamento de banco de dados vetorial
- Gerenciamento de embeddings
"""

# Exportar componentes principais para facilitar importação
from gesonelbot.core.document_processor import ingest_documents, get_processed_documents_info
from gesonelbot.core.qa_engine import answer_question
from gesonelbot.core.embeddings_manager import embeddings_manager 