"""
Motor de perguntas e respostas

Este módulo é responsável por responder perguntas com base nos documentos processados,
utilizando o sistema de recuperação de informações e templates de prompts.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union

# Componentes do GesonelBot
from gesonelbot.core.retriever import document_retriever
from gesonelbot.config.settings import (
    QA_PROMPT_TEMPLATE,
    QA_TEMPERATURE,
    QA_MAX_TOKENS,
    MODEL_TYPE,
    OPENAI_MODEL,
    OPENAI_API_KEY
)

# Configurar logging
logger = logging.getLogger(__name__)

# Template de prompt padrão para QA
PROMPT_TEMPLATES = {
    "padrao": """
Você é um assistente de IA que responde perguntas com base nos documentos fornecidos.
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
Responda à pergunta de forma concisa usando apenas os contextos fornecidos.
Contextos: {contexts}
Pergunta: {question}
Resposta (cite as fontes):
"""
}

def generate_answer_with_openai(prompt: str) -> str:
    """
    Gera uma resposta usando a API da OpenAI.
    
    Args:
        prompt: O prompt formatado para enviar à API
        
    Returns:
        Resposta gerada
    """
    try:
        # Importação condicional para evitar dependência obrigatória
        from openai import OpenAI
        
        if not OPENAI_API_KEY:
            logger.error("Chave da API OpenAI não configurada")
            return "Erro: Chave da API OpenAI não configurada. Verifique seu arquivo .env."
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=QA_TEMPERATURE,
            max_tokens=QA_MAX_TOKENS
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro ao gerar resposta com OpenAI: {str(e)}")
        return f"Erro ao gerar resposta: {str(e)}"

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
                    "processing_time_ms": 0
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
            contexts="\n\n".join(contexts),
            question=question
        )
        
        # Gerar a resposta com base no modelo configurado
        if MODEL_TYPE == "openai":
            answer = generate_answer_with_openai(prompt)
        else:
            # Por enquanto, apenas um stub para o modelo local (será implementado na próxima fase)
            answer = f"[Modelo local não implementado] Pergunta: {question}\nContextos encontrados: {len(contexts)}"
        
        # Retornar o resultado
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "metadata": {
                "retrieved_documents": len(retrieved_docs),
                "processing_time_ms": 0  # Será implementado futuramente
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao responder pergunta: {str(e)}")
        return {
            "question": question,
            "answer": f"Ocorreu um erro ao processar sua pergunta: {str(e)}",
            "sources": [],
            "metadata": {
                "error": str(e),
                "retrieved_documents": 0
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

# Funções a serem implementadas nas próximas etapas:
# - create_vectorstore_from_documents
# - retrieve_relevant_documents
# - format_answer_with_sources 