"""
Motor de perguntas e respostas

Este módulo é responsável por responder perguntas com base nos documentos processados,
utilizando o sistema de recuperação de informações e templates de prompts.
"""
import os
import logging
import time
from typing import List, Dict, Any, Optional, Union

# Componentes do GesonelBot
from gesonelbot.core.retriever import document_retriever
from gesonelbot.core.llm_manager import llm_manager
from gesonelbot.config.settings import (
    USER_TEMPLATE as QA_PROMPT_TEMPLATE,
    QA_TEMPERATURE,
    QA_MAX_TOKENS,
    SYSTEM_TEMPLATE as QA_SYSTEM_PROMPT,
    MODEL_TYPE
)

# Configurar logging
logger = logging.getLogger(__name__)

# Template de prompt padrão para QA
PROMPT_TEMPLATES = {
    "padrao": """
{system_prompt}

Use apenas as informações fornecidas nos contextos abaixo para responder à pergunta.
Se a informação não estiver presente nos contextos, diga que não tem informações suficientes para responder.
Não invente ou suponha informações que não estejam explicitamente nos contextos.
Cite as fontes dos documentos de onde você extraiu as informações, usando os nomes dos arquivos fornecidos.

Contextos:
{contexts}

Pergunta: {question}

Resposta:
""",
    "conciso": """
{system_prompt}

Responda à pergunta de forma concisa usando apenas os contextos fornecidos.
Contextos: {contexts}
Pergunta: {question}
Resposta (cite as fontes):
""",
    "academico": """
{system_prompt}

Você é um assistente acadêmico respondendo a uma pergunta com base em documentos fornecidos.
Use um tom formal e estruturado, citando apropriadamente as fontes.
Organize sua resposta em parágrafos lógicos e inclua uma conclusão.

Contextos disponíveis:
{contexts}

Pergunta: {question}

Resposta acadêmica:
"""
}

def answer_question(question: str, top_k: int = None) -> Dict[str, Any]:
    """
    Responde uma pergunta com base nos documentos armazenados.
    
    Args:
        question: A pergunta do usuário
        top_k: Número máximo de resultados a usar (opcional, usa o padrão se None)
        
    Returns:
        Dicionário com a resposta e informações adicionais
    """
    # Validar a pergunta
    if not question or len(question.strip()) == 0:
        logger.warning("Pergunta vazia recebida")
        return {
            "question": question,
            "answer": "Por favor, faça uma pergunta válida.",
            "sources": [],
            "metadata": {
                "retrieved_documents": 0,
                "processing_time_ms": 0
            }
        }
    
    logger.info(f"Processando pergunta: '{question}'")
    start_time = time.time()
    
    try:
        # Recuperar documentos relevantes usando o retriever
        retrieved_docs = document_retriever.search(question)
        
        # Se não encontrou documentos relevantes
        if not retrieved_docs:
            logger.warning("Nenhum documento relevante encontrado para a pergunta")
            return {
                "question": question,
                "answer": "Não encontrei informações relevantes para responder a esta pergunta nos documentos carregados.",
                "sources": [],
                "metadata": {
                    "retrieved_documents": 0,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
        
        # Limitar o número de documentos se top_k for especificado
        if top_k is not None:
            retrieved_docs = retrieved_docs[:top_k]
        
        # Preparar os contextos para o prompt
        contexts = []
        sources = []
        
        for i, doc in enumerate(retrieved_docs):
            # Formatar o contexto
            context = f"[Documento {i+1}] {doc['content']}"
            contexts.append(context)
            
            # Coletar informações da fonte
            source_info = {
                "file_name": doc["file_name"],
                "source": doc["source"] if "source" in doc else f"Documento {i+1}"
            }
            sources.append(source_info)
        
        # Selecionar o template de prompt
        prompt_template = PROMPT_TEMPLATES.get(QA_PROMPT_TEMPLATE, PROMPT_TEMPLATES["padrao"])
        
        # Formatar o prompt com os contextos e a pergunta
        prompt = prompt_template.format(
            system_prompt=QA_SYSTEM_PROMPT,
            contexts="\n\n".join(contexts),
            question=question
        )
        
        # Gerar a resposta usando o LLM Manager
        answer = llm_manager.generate_response(
            prompt,
            temperature=QA_TEMPERATURE,
            max_tokens=QA_MAX_TOKENS
        )
        
        # Calcular tempo de processamento
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Obter informações sobre o modelo usado
        model_info = llm_manager.get_model_info()
        
        # Retornar o resultado
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "metadata": {
                "retrieved_documents": len(retrieved_docs),
                "processing_time_ms": processing_time_ms,
                "model_info": model_info
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao responder pergunta: {str(e)}")
        processing_time_ms = int((time.time() - start_time) * 1000)
        return {
            "question": question,
            "answer": f"Ocorreu um erro ao processar sua pergunta: {str(e)}",
            "sources": [],
            "metadata": {
                "error": str(e),
                "retrieved_documents": 0,
                "processing_time_ms": processing_time_ms
            }
        }

def list_available_documents() -> List[Dict[str, str]]:
    """
    Lista os documentos disponíveis para consulta.
    
    Returns:
        Lista de dicionários com informações sobre os documentos
    """
    from gesonelbot.core.document_processor import get_processed_documents_info
    
    try:
        documents = get_processed_documents_info()
        return documents
    except Exception as e:
        logger.error(f"Erro ao listar documentos disponíveis: {str(e)}")
        return []

def get_model_info() -> Dict[str, Any]:
    """
    Retorna informações sobre o modelo de linguagem atual.
    
    Returns:
        Dicionário com informações sobre o modelo
    """
    return llm_manager.get_model_info()

def list_available_models() -> List[Dict[str, Any]]:
    """
    Lista os modelos disponíveis no sistema.
    
    Returns:
        Lista de dicionários com informações sobre os modelos
    """
    return llm_manager.list_available_models()

# Funções a serem implementadas nas próximas etapas:
# - create_vectorstore_from_documents
# - retrieve_relevant_documents
# - format_answer_with_sources 