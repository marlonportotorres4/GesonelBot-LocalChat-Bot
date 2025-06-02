"""
Módulo de recuperação de informações (Retriever)

Este módulo é responsável por recuperar informações relevantes
do banco de dados vetorial com base em consultas do usuário.
"""
import logging
from typing import List, Dict, Any, Optional, Union

from langchain.docstore.document import Document
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Importar componentes do GesonelBot
from gesonelbot.core.embeddings_manager import embeddings_manager
from gesonelbot.config.settings import (
    RETRIEVER_K,
    RETRIEVER_SEARCH_TYPE,
    RETRIEVER_THRESHOLD,
    MODEL_TYPE
)

# Configurar logging
logger = logging.getLogger(__name__)

class DocumentRetriever:
    """
    Classe para recuperação de documentos relevantes com base em consultas.
    
    Esta classe implementa vários métodos de recuperação para buscar os 
    documentos mais relevantes para uma consulta:
    
    1. Busca semântica: Busca por similaridade de embeddings
    2. Busca híbrida: Combinação de busca por keywords e semântica
    3. Busca contextual: Refina os resultados usando compressão contextual
    """
    
    def __init__(self):
        """Inicializa o retriever."""
        self.embeddings_manager = embeddings_manager
        self.vector_store = None
        self.retriever = None
        self._initialize_retriever()
    
    def _initialize_retriever(self) -> None:
        """
        Inicializa o retriever com base no banco de dados vetorial.
        """
        # Carregar o vector store
        self.vector_store = self.embeddings_manager.get_vector_store()
        
        if not self.vector_store:
            logger.warning("Banco de dados vetorial não encontrado. Não será possível realizar buscas.")
            return
        
        # Configurar o retriever básico
        # O tipo de busca pode ser 'similarity', 'mmr', ou 'similarity_score_threshold'
        if RETRIEVER_SEARCH_TYPE == "mmr":
            # MMR (Maximum Marginal Relevance) busca documentos relevantes mas diversos
            self.retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": RETRIEVER_K,
                    "fetch_k": RETRIEVER_K * 2,  # Buscar mais para ter diversidade
                    "lambda_mult": 0.7  # Equilíbrio entre relevância e diversidade
                }
            )
            logger.info("Retriever inicializado com busca MMR")
        elif RETRIEVER_SEARCH_TYPE == "similarity_score_threshold":
            # Busca por similaridade com limite de score
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": RETRIEVER_K,
                    "score_threshold": RETRIEVER_THRESHOLD
                }
            )
            logger.info(f"Retriever inicializado com threshold de similaridade: {RETRIEVER_THRESHOLD}")
        else:
            # Busca por similaridade padrão
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": RETRIEVER_K}
            )
            logger.info(f"Retriever inicializado com busca de similaridade padrão (top {RETRIEVER_K})")
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Recupera documentos relevantes para a consulta.
        
        Args:
            query: Texto da consulta do usuário
            
        Returns:
            Lista de documentos relevantes
        """
        if not self.retriever:
            logger.warning("Retriever não inicializado. Tentando inicializar novamente.")
            self._initialize_retriever()
            
            if not self.retriever:
                logger.error("Não foi possível inicializar o retriever. Retornando lista vazia.")
                return []
        
        try:
            logger.info(f"Buscando documentos relevantes para: '{query}'")
            documents = self.retriever.get_relevant_documents(query)
            logger.info(f"Encontrados {len(documents)} documentos relevantes")
            return documents
        except Exception as e:
            logger.error(f"Erro ao buscar documentos: {str(e)}")
            return []
    
    def format_retrieved_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Formata os documentos recuperados para apresentação.
        
        Args:
            documents: Lista de documentos recuperados
            
        Returns:
            Lista de documentos formatados com metadados
        """
        formatted_docs = []
        
        for i, doc in enumerate(documents):
            try:
                # Extrair informações dos metadados
                source = doc.metadata.get("source", "Desconhecido")
                file_name = doc.metadata.get("file_name", "Desconhecido")
                
                # Formatar para exibição
                formatted_docs.append({
                    "id": i,
                    "content": doc.page_content,
                    "source": source,
                    "file_name": file_name,
                    "metadata": doc.metadata
                })
            except Exception as e:
                logger.error(f"Erro ao formatar documento {i}: {str(e)}")
        
        return formatted_docs
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Realiza uma busca completa e retorna documentos formatados.
        
        Args:
            query: Texto da consulta do usuário
            
        Returns:
            Lista de documentos formatados
        """
        # Recuperar documentos relevantes
        documents = self.get_relevant_documents(query)
        
        # Se não encontrar documentos, retornar lista vazia
        if not documents:
            logger.warning(f"Nenhum documento encontrado para a consulta: '{query}'")
            return []
        
        # Formatar documentos para apresentação
        return self.format_retrieved_documents(documents)

# Instância global para uso em toda a aplicação
document_retriever = DocumentRetriever() 