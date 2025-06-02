"""
Gerenciador de Embeddings

Este módulo gerencia a geração e armazenamento de embeddings para os documentos processados.
Suporta diferentes modelos de embeddings e se integra com o banco de dados vetorial.
"""
import os
from typing import List, Dict, Any, Optional, Union
import logging

from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

from gesonelbot.config.settings import (
    VECTORSTORE_DIR, 
    EMBEDDINGS_MODEL,
    MODEL_TYPE
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingsManager:
    """Gerencia a criação e utilização de embeddings para documentos."""
    
    def __init__(self):
        """Inicializa o gerenciador de embeddings."""
        self.embedding_model = None
        self.vector_store = None
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self) -> None:
        """
        Inicializa o modelo de embeddings com base nas configurações.
        Suporta modelos locais (HuggingFace) e OpenAI.
        """
        logger.info(f"Inicializando modelo de embeddings: {EMBEDDINGS_MODEL}")
        
        try:
            if EMBEDDINGS_MODEL == "openai" and MODEL_TYPE == "openai":
                # Usando embeddings da OpenAI (requer API key)
                self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
                logger.info("Modelo de embeddings OpenAI inicializado")
            else:
                # Modelo padrão local (melhor equilíbrio entre qualidade e velocidade)
                model_name = "all-MiniLM-L6-v2"
                # Se um modelo específico foi configurado, usá-lo
                if EMBEDDINGS_MODEL != "local" and EMBEDDINGS_MODEL != "openai":
                    model_name = EMBEDDINGS_MODEL
                
                logger.info(f"Usando modelo de embeddings local: {model_name}")
                self.embedding_model = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info("Modelo de embeddings local inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo de embeddings: {str(e)}")
            # Fallback para modelo simples local em caso de erro
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.warning("Usando modelo de embeddings de fallback devido a erro")
    
    def get_embedding_model(self) -> Embeddings:
        """
        Retorna o modelo de embeddings atual.
        
        Returns:
            Embeddings: O modelo de embeddings inicializado
        """
        if not self.embedding_model:
            self._initialize_embedding_model()
        return self.embedding_model
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Cria ou atualiza um banco de dados vetorial com os documentos fornecidos.
        
        Args:
            documents: Lista de documentos a serem adicionados ao banco de dados
            
        Returns:
            Chroma: O banco de dados vetorial
        """
        if not documents:
            logger.warning("Nenhum documento fornecido para criar o vector store")
            return None
        
        logger.info(f"Criando vector store com {len(documents)} documentos")
        
        try:
            # Criar ou atualizar o banco de dados vetorial
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.get_embedding_model(),
                persist_directory=VECTORSTORE_DIR
            )
            
            # Persistir o banco de dados
            vector_store.persist()
            
            logger.info(f"Vector store criado e persistido em {VECTORSTORE_DIR}")
            self.vector_store = vector_store
            return vector_store
        except Exception as e:
            logger.error(f"Erro ao criar vector store: {str(e)}")
            return None
    
    def load_vector_store(self) -> Optional[Chroma]:
        """
        Carrega um banco de dados vetorial existente.
        
        Returns:
            Optional[Chroma]: O banco de dados vetorial ou None se não existir
        """
        if not os.path.exists(VECTORSTORE_DIR) or not os.listdir(VECTORSTORE_DIR):
            logger.warning(f"Diretório do vector store vazio ou não existente: {VECTORSTORE_DIR}")
            return None
        
        try:
            logger.info(f"Carregando vector store de {VECTORSTORE_DIR}")
            vector_store = Chroma(
                persist_directory=VECTORSTORE_DIR,
                embedding_function=self.get_embedding_model()
            )
            self.vector_store = vector_store
            return vector_store
        except Exception as e:
            logger.error(f"Erro ao carregar vector store: {str(e)}")
            return None
    
    def get_vector_store(self) -> Optional[Chroma]:
        """
        Retorna o banco de dados vetorial atual ou carrega se existir.
        
        Returns:
            Optional[Chroma]: O banco de dados vetorial ou None se não existir
        """
        if self.vector_store:
            return self.vector_store
        
        return self.load_vector_store()
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Adiciona documentos ao banco de dados vetorial existente.
        
        Args:
            documents: Lista de documentos a serem adicionados
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        if not documents:
            logger.warning("Nenhum documento fornecido para adicionar ao vector store")
            return False
        
        vector_store = self.get_vector_store()
        
        try:
            if vector_store:
                logger.info(f"Adicionando {len(documents)} documentos ao vector store existente")
                vector_store.add_documents(documents)
                vector_store.persist()
                return True
            else:
                logger.info("Vector store não existe, criando novo")
                return self.create_vector_store(documents) is not None
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos ao vector store: {str(e)}")
            return False

# Instância global para uso em toda a aplicação
embeddings_manager = EmbeddingsManager() 