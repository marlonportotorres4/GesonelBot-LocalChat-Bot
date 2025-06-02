"""
Gerenciador de Modelos de Linguagem (LLM)

Este módulo gerencia diferentes modelos de linguagem para geração de respostas,
suportando modelo local (offline) ou API da OpenAI (online).
"""
import os
import logging
from typing import Dict, Any, Optional, Union, List

# Importações condicionais para evitar dependências obrigatórias
# Serão importadas apenas quando o modelo específico for solicitado
llm_imports_successful = {
    "openai": False,
    "ctransformers": False
}

# Configurações
from gesonelbot.config.settings import (
    MODEL_TYPE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LOCAL_MODEL_PATH,
    LOCAL_MODEL_TYPE,
    QA_TEMPERATURE,
    QA_MAX_TOKENS
)

# Configurar logging
logger = logging.getLogger(__name__)

class LLMManager:
    """
    Gerencia modelos de linguagem para geração de texto.
    
    Esta classe oferece uma interface unificada para dois tipos de modelos:
    - Modelo local (usando CTransformers) para uso offline
    - Modelo da OpenAI (via API) para melhor qualidade quando online
    
    O modelo é carregado sob demanda para economizar recursos.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de modelos."""
        self.model_type = MODEL_TYPE  # 'local' ou 'openai'
        self.current_model = None
        self.model_info = {}
        
        # Verificar configurações iniciais
        logger.info(f"Inicializando LLM Manager com tipo de modelo: {self.model_type}")
        
        # Verificar se as pastas necessárias existem
        if self.model_type == "local" and not os.path.exists(LOCAL_MODEL_PATH):
            logger.warning(f"Caminho do modelo local não encontrado: {LOCAL_MODEL_PATH}")
            if os.path.dirname(LOCAL_MODEL_PATH):
                os.makedirs(os.path.dirname(LOCAL_MODEL_PATH), exist_ok=True)
                logger.info(f"Diretório para modelos locais criado: {os.path.dirname(LOCAL_MODEL_PATH)}")
    
    def _load_openai_model(self) -> bool:
        """
        Carrega o modelo da OpenAI.
        
        Returns:
            bool: True se o modelo foi carregado com sucesso
        """
        try:
            # Importar apenas quando necessário
            from openai import OpenAI
            llm_imports_successful["openai"] = True
            
            if not OPENAI_API_KEY:
                logger.error("Chave da API OpenAI não configurada. Verifique seu arquivo .env")
                return False
            
            # Criar cliente OpenAI
            self.current_model = OpenAI(api_key=OPENAI_API_KEY)
            self.model_info = {
                "type": "openai",
                "name": OPENAI_MODEL,
                "max_tokens": QA_MAX_TOKENS,
                "temperature": QA_TEMPERATURE,
                "modo": "online"
            }
            
            logger.info(f"Modelo OpenAI inicializado: {OPENAI_MODEL}")
            return True
        except ImportError:
            logger.error("Biblioteca OpenAI não instalada. Execute 'pip install openai'")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo OpenAI: {str(e)}")
            return False
    
    def _load_local_model(self) -> bool:
        """
        Carrega um modelo local usando CTransformers (para modelos GGUF).
        
        Returns:
            bool: True se o modelo foi carregado com sucesso
        """
        try:
            # Importar apenas quando necessário
            from ctransformers import AutoModelForCausalLM
            llm_imports_successful["ctransformers"] = True
            
            if not os.path.exists(LOCAL_MODEL_PATH):
                logger.error(f"Arquivo de modelo não encontrado: {LOCAL_MODEL_PATH}")
                logger.error("Execute o setup.bat para baixar o modelo.")
                return False
            
            # Carregar o modelo
            self.current_model = AutoModelForCausalLM.from_pretrained(
                LOCAL_MODEL_PATH,
                model_type=LOCAL_MODEL_TYPE or "llama",  # llama é o padrão para TinyLlama
                max_new_tokens=QA_MAX_TOKENS,
                temperature=QA_TEMPERATURE
            )
            
            self.model_info = {
                "type": "local",
                "name": os.path.basename(LOCAL_MODEL_PATH),
                "max_tokens": QA_MAX_TOKENS,
                "temperature": QA_TEMPERATURE,
                "modo": "offline"
            }
            
            logger.info(f"Modelo local inicializado: {os.path.basename(LOCAL_MODEL_PATH)}")
            return True
        except ImportError:
            logger.error("Biblioteca CTransformers não instalada. Execute 'pip install ctransformers'")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo local: {str(e)}")
            return False
    
    def reload_settings(self):
        """
        Recarrega as configurações e atualiza o modelo se necessário.
        
        Esta função deve ser chamada quando as configurações forem alteradas
        pelo settings_manager para garantir que o modelo atual seja atualizado.
        """
        # Reimportar as configurações
        import importlib
        import gesonelbot.config.settings
        importlib.reload(gesonelbot.config.settings)
        
        # Atualizar variáveis locais
        from gesonelbot.config.settings import (
            MODEL_TYPE, OPENAI_API_KEY, OPENAI_MODEL, 
            LOCAL_MODEL_PATH, LOCAL_MODEL_TYPE
        )
        
        # Verificar se o tipo de modelo mudou
        if MODEL_TYPE != self.model_type:
            logger.info(f"Tipo de modelo alterado de {self.model_type} para {MODEL_TYPE}")
            self.model_type = MODEL_TYPE
            
            # Descarregar o modelo atual
            self.current_model = None
            self.model_info = {}
            
            # Carregar o novo modelo
            self.load_model()
        
        # Verificar se outras configurações importantes mudaram
        if self.current_model and self.model_info.get("type") == "openai":
            # Recarregar modelo OpenAI se a API key ou o modelo mudou
            current_model_name = self.model_info.get("name")
            if current_model_name != OPENAI_MODEL:
                logger.info(f"Modelo OpenAI alterado de {current_model_name} para {OPENAI_MODEL}")
                self.current_model = None
                self.load_model()
    
    def load_model(self, model_type: Optional[str] = None) -> bool:
        """
        Carrega o modelo especificado.
        
        Args:
            model_type: Tipo de modelo a carregar ('openai' ou 'local')
                        Se None, usa o tipo configurado em settings.py
        
        Returns:
            bool: True se o modelo foi carregado com sucesso
        """
        # Se model_type não for especificado, usar o configurado
        model_type = model_type or self.model_type
        
        logger.info(f"Carregando modelo do tipo: {model_type}")
        
        # Carregar o modelo apropriado
        if model_type == "openai":
            return self._load_openai_model()
        elif model_type == "local":
            return self._load_local_model()
        else:
            logger.error(f"Tipo de modelo não suportado: {model_type}")
            logger.info("Tentando usar modelo local como fallback...")
            return self._load_local_model()
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Gera uma resposta usando o modelo carregado.
        
        Args:
            prompt: O prompt para o modelo
            **kwargs: Parâmetros adicionais para a geração (temperatura, max_tokens, etc.)
        
        Returns:
            str: A resposta gerada pelo modelo
        """
        # Verificar se o modelo está carregado
        if not self.current_model:
            logger.info("Modelo não carregado. Carregando modelo...")
            success = self.load_model()
            
            # Tentar usar modelo alternativo se o primeiro falhar
            if not success and self.model_type == "openai":
                logger.info("Modelo OpenAI falhou. Tentando modelo local como fallback...")
                success = self.load_model("local")
            
            if not success:
                return "Erro: Não foi possível carregar nenhum modelo. Verifique se o modelo local está baixado ou se a API da OpenAI está configurada."
        
        # Gerar resposta com base no tipo de modelo
        try:
            model_type = self.model_info.get("type", "unknown")
            
            if model_type == "openai":
                # Parâmetros para a API da OpenAI
                temperature = kwargs.get("temperature", QA_TEMPERATURE)
                max_tokens = kwargs.get("max_tokens", QA_MAX_TOKENS)
                
                response = self.current_model.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
                
            elif model_type == "local":
                # Parâmetros para o modelo local
                temperature = kwargs.get("temperature", QA_TEMPERATURE)
                max_tokens = kwargs.get("max_tokens", QA_MAX_TOKENS)
                
                return self.current_model(
                    prompt,
                    temperature=temperature,
                    max_new_tokens=max_tokens
                )
                
            else:
                logger.error(f"Tipo de modelo não suportado para geração: {model_type}")
                return f"Erro: Tipo de modelo não suportado: {model_type}"
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return f"Erro ao gerar resposta: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual.
        
        Returns:
            Dict[str, Any]: Informações sobre o modelo
        """
        if not self.current_model:
            return {"status": "não carregado", "type": self.model_type}
        
        return {
            "status": "carregado",
            **self.model_info
        }
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Lista os modelos disponíveis no sistema.
        
        Returns:
            List[Dict[str, Any]]: Lista de modelos disponíveis
        """
        models = []
        
        # Verificar modelo local
        if os.path.exists(LOCAL_MODEL_PATH):
            models.append({
                "name": os.path.basename(LOCAL_MODEL_PATH),
                "path": LOCAL_MODEL_PATH,
                "type": "local",
                "size_mb": round(os.path.getsize(LOCAL_MODEL_PATH) / (1024 * 1024), 1),
                "modo": "offline"
            })
        else:
            models.append({
                "name": "Modelo local não encontrado",
                "type": "local",
                "status": "indisponível - arquivo não encontrado",
                "modo": "offline"
            })
        
        # Verificar modelo OpenAI
        if OPENAI_API_KEY:
            models.append({
                "name": OPENAI_MODEL,
                "type": "openai",
                "api_key_configured": True,
                "modo": "online"
            })
        else:
            models.append({
                "name": OPENAI_MODEL,
                "type": "openai",
                "api_key_configured": False,
                "status": "indisponível - API key não configurada",
                "modo": "online"
            })
        
        return models

# Instância global para uso em toda a aplicação
llm_manager = LLMManager() 