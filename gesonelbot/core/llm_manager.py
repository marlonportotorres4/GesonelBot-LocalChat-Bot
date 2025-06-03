"""
Gerenciador de Modelos de Linguagem (LLM)

Este módulo gerencia o modelo de linguagem para geração de respostas,
utilizando a API da Together.ai com o modelo lgai/exaone-3-5-32b-instruct.
"""
import os
import logging
import json
from typing import Dict, Any, Optional, Union, List

# Configurações
from gesonelbot.config.settings import (
    TOGETHER_API_KEY,
    TOGETHER_MODEL,
    QA_TEMPERATURE,
    QA_MAX_TOKENS,
    SYSTEM_TEMPLATE
)

# Configurar logging
logger = logging.getLogger(__name__)

class LLMManager:
    """
    Gerencia o modelo de linguagem para geração de texto.
    
    Esta classe oferece uma interface para modelos de linguagem
    através da API da Together.ai.
    
    O modelo é carregado sob demanda para economizar recursos.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de modelos."""
        self.model_type = "together"
        self.current_model = None
        self.model_info = {}
        
        # Verificar configurações iniciais
        logger.info(f"Inicializando LLM Manager com Together.ai - modelo: {TOGETHER_MODEL}")
    
    def _load_together_model(self) -> bool:
        """
        Configura o acesso ao modelo da Together.ai.
        
        Returns:
            bool: True se a configuração foi bem-sucedida
        """
        try:
            if not TOGETHER_API_KEY:
                logger.error("Chave API da Together.ai não configurada. Verifique seu arquivo .env")
                return False
            
            # Importar a biblioteca Together
            try:
                from together import Together
                logger.info("Biblioteca Together importada com sucesso")
            except ImportError:
                logger.error("Biblioteca Together não instalada. Execute 'pip install together'")
                return False
            
            # Inicializar o cliente Together
            self.current_model = Together(api_key=TOGETHER_API_KEY)
            
            # Atualizar informações do modelo
            self.model_info = {
                "type": "together",
                "name": TOGETHER_MODEL,
                "max_tokens": QA_MAX_TOKENS,
                "temperature": QA_TEMPERATURE,
                "modo": "online"
            }
            
            logger.info(f"API Together.ai configurada para modelo: {TOGETHER_MODEL}")
            return True
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Erro ao configurar API Together.ai: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
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
            TOGETHER_API_KEY, TOGETHER_MODEL
        )
        
        # Verificar se configurações importantes mudaram
        if self.current_model:
            # Recarregar modelo se o modelo mudou
            current_model_name = self.model_info.get("name")
            if current_model_name != TOGETHER_MODEL:
                logger.info(f"Modelo Together.ai alterado de {current_model_name} para {TOGETHER_MODEL}")
                self.current_model = None
                self.load_model()
    
    def load_model(self) -> bool:
        """
        Carrega o modelo Together.ai.
        
        Returns:
            bool: True se o modelo foi carregado com sucesso
        """
        logger.info(f"Carregando modelo Together.ai: {TOGETHER_MODEL}")
        return self._load_together_model()
    
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
            
            if not success:
                return "Erro: Não foi possível carregar o modelo. Verifique se a API key da Together.ai está configurada."
        
        # Gerar resposta
        try:
            # Parâmetros para a API
            temperature = kwargs.get("temperature", QA_TEMPERATURE)
            max_tokens = kwargs.get("max_tokens", QA_MAX_TOKENS)
            
            # Usar o sistema prompt personalizado se fornecido, caso contrário usar o padrão
            system_prompt = kwargs.get("system_prompt", SYSTEM_TEMPLATE.format(app_name="GesonelBot"))
            
            # Melhorar o formato do prompt
            formatted_prompt = f"""
Por favor, analise os documentos fornecidos e responda à pergunta com base apenas nas informações contidas neles.

{prompt}
"""
            
            # Criar mensagens no formato adequado para o modelo
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ]
            
            logger.info(f"Enviando prompt para modelo Together.ai: {TOGETHER_MODEL}")
            logger.info(f"Parâmetros da chamada: temperatura={temperature}, max_tokens={max_tokens}")
            logger.debug(f"Prompt completo: {formatted_prompt[:500]}...")
            
            try:
                # Chamar a API da Together.ai
                response = self.current_model.chat.completions.create(
                    model=TOGETHER_MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=0.9
                )
                
                logger.info("Resposta recebida do modelo Together.ai")
                
                # Extrair a resposta
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                        return response.choices[0].message.content
                
                # Fallback se a estrutura não for a esperada
                logger.warning("Formato de resposta inesperado, tentando extrair conteúdo")
                return str(response)
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Erro na chamada da API Together.ai: {str(e)}")
                logger.error(f"Traceback: {error_traceback}")
                return f"Erro ao gerar resposta: {str(e)}"
                
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            return f"Erro ao gerar resposta: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual.
        
        Returns:
            Dict[str, Any]: Informações sobre o modelo
        """
        if not self.current_model:
            return {"status": "não carregado", "type": self.model_type, "name": TOGETHER_MODEL}
        
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
        
        # Verificar modelo Together.ai
        if TOGETHER_API_KEY:
            models.append({
                "name": TOGETHER_MODEL,
                "type": "together",
                "api_key_configured": True,
                "modo": "online",
                "status": "ativo"
            })
        else:
            models.append({
                "name": TOGETHER_MODEL,
                "type": "together",
                "api_key_configured": False,
                "status": "indisponível - API key não configurada",
                "modo": "online"
            })
        
        return models

# Instância global para uso em toda a aplicação
llm_manager = LLMManager() 