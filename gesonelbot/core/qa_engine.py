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
    QA_MAX_TOKENS
)

# Configurar logging
logger = logging.getLogger(__name__)

# Sistema prompt personalizado para o chatbot
SYSTEM_PROMPT = """
Você é um assistente de IA especializado em responder perguntas com base em documentos.

INSTRUÇÕES IMPORTANTES:
1. Use APENAS as informações contidas nos documentos fornecidos para responder às perguntas.
2. Se a informação não estiver presente nos documentos, diga uma resposta simples e direta, por exemplo se um usuário perguntar se você sabe conjurar magia, responda: "Não sei conjurar magia, Estou aqui para responder perguntas sobre os documentos fornecidos" ou se perguntar "olá tudo bem com você?" responda: "Estou bem! E você? Estou aqui para responder perguntas sobre os documentos fornecidos".
3. NÃO invente informações ou use seu conhecimento geral quando os documentos não contêm a resposta.
4. Cite as fontes específicas dos documentos de onde extraiu as informações, somente dos DOCUMENTOS QUE VOCÊ EXTRAIU AS INFORMAÇÕES, não cite fontes de outros documentos caso não tenha extraído informações de outros documentos.
5. Forneça respostas Objetivas e precisas quando os documentos contiverem as informações solicitadas.
6. Analise cuidadosamente todo o conteúdo dos documentos antes de responder.
"""

# Template de prompt padrão para QA
PROMPT_TEMPLATES = {
    "padrao": """
Use apenas as informações fornecidas nos documentos abaixo para responder à pergunta.
Se a informação não estiver presente nos documentos, diga que não tem informações suficientes para responder.
Não invente ou suponha informações que não estejam explicitamente nos documentos.
Cite as fontes dos documentos de onde você extraiu as informações.

Documentos:
{contexts}

Pergunta: {question}
""",
    "conciso": """
Responda à pergunta de forma concisa usando apenas os documentos fornecidos.
Documentos: {contexts}
Pergunta: {question}
""",
    "academico": """
Você é um assistente acadêmico respondendo a uma pergunta com base em documentos fornecidos.
Use um tom formal e estruturado, citando apropriadamente as fontes.
Organize sua resposta em parágrafos lógicos e inclua uma conclusão.

Documentos disponíveis:
{contexts}

Pergunta: {question}
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
            # Extrair informações do documento
            file_name = doc.get("file_name", f"Documento {i+1}")
            source = doc.get("source", f"Fonte {i+1}")
            content = doc.get("content", "").strip()
            
            # Formatar o conteúdo do documento de forma clara
            formatted_content = f"""DOCUMENTO {i+1}: {file_name}
{content}
"""
            contexts.append(formatted_content)
            
            # Coletar informações da fonte
            source_info = {
                "file_name": file_name,
                "source": source
            }
            sources.append(source_info)
        
        # Juntar todos os contextos com separadores claros
        all_contexts = "\n\n" + "\n\n".join(contexts)
        
        # Selecionar o template de prompt
        prompt_template = PROMPT_TEMPLATES.get(QA_PROMPT_TEMPLATE, PROMPT_TEMPLATES["padrao"])
        
        # Formatar o prompt com os contextos e a pergunta
        prompt = prompt_template.format(
            contexts=all_contexts,
            question=question
        )
        
        # Log do prompt para debug
        logger.debug(f"Prompt completo: {prompt[:500]}...")
        
        # Gerar a resposta usando o LLM Manager com o sistema prompt personalizado
        answer = llm_manager.generate_response(
            prompt,
            temperature=QA_TEMPERATURE,
            max_tokens=QA_MAX_TOKENS,
            system_prompt=SYSTEM_PROMPT
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
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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