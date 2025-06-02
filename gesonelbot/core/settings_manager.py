"""
Gerenciador de configurações em tempo de execução

Este módulo permite alterar configurações do sistema sem reiniciar a aplicação,
como alternar entre modos de modelo e atualizar chaves de API.
"""
import os
import logging
import dotenv
from pathlib import Path
from typing import Dict, Any, Optional

# Importar configurações atuais
from gesonelbot.config.settings import (
    MODEL_TYPE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LOCAL_MODEL_PATH,
    LOCAL_MODEL_TYPE
)

# Configurar logging
logger = logging.getLogger(__name__)

class SettingsManager:
    """
    Gerencia alterações nas configurações em tempo de execução.
    
    Esta classe permite modificar configurações do sistema sem reiniciar
    a aplicação, atualizando tanto as variáveis em memória quanto o arquivo .env.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de configurações."""
        # Caminho para o arquivo .env
        self.env_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / '.env'
        if not self.env_path.exists():
            logger.warning(f"Arquivo .env não encontrado em {self.env_path}. Será criado ao salvar configurações.")
        
        # Configurações atuais
        self.current_settings = {
            "MODEL_TYPE": MODEL_TYPE,
            "OPENAI_API_KEY": OPENAI_API_KEY,
            "OPENAI_MODEL": OPENAI_MODEL,
            "LOCAL_MODEL_PATH": LOCAL_MODEL_PATH,
            "LOCAL_MODEL_TYPE": LOCAL_MODEL_TYPE
        }
    
    def update_model_type(self, model_type: str) -> bool:
        """
        Altera o tipo de modelo utilizado (local ou openai).
        
        Args:
            model_type: Tipo de modelo ('local' ou 'openai')
            
        Returns:
            bool: True se a alteração foi bem-sucedida
        """
        if model_type not in ['local', 'openai']:
            logger.error(f"Tipo de modelo inválido: {model_type}. Use 'local' ou 'openai'.")
            return False
        
        # Verificar se tem API key configurada quando alterando para OpenAI
        if model_type == 'openai' and not self.current_settings['OPENAI_API_KEY']:
            logger.warning("Alterando para modelo OpenAI sem API key configurada. Configure a API key primeiro.")
        
        # Atualizar configuração
        self.current_settings['MODEL_TYPE'] = model_type
        
        # Salvar no arquivo .env
        self._save_to_env("MODEL_TYPE", model_type)
        
        # Atualizar valor global (usado pelo sistema)
        import gesonelbot.config.settings
        gesonelbot.config.settings.MODEL_TYPE = model_type
        
        logger.info(f"Tipo de modelo alterado para: {model_type}")
        return True
    
    def update_openai_api_key(self, api_key: str) -> bool:
        """
        Atualiza a chave de API da OpenAI.
        
        Args:
            api_key: Nova chave de API
            
        Returns:
            bool: True se a alteração foi bem-sucedida
        """
        if not api_key or len(api_key.strip()) < 10:
            logger.error("Chave de API OpenAI inválida ou muito curta.")
            return False
        
        # Atualizar configuração
        self.current_settings['OPENAI_API_KEY'] = api_key
        
        # Salvar no arquivo .env
        self._save_to_env("OPENAI_API_KEY", api_key)
        
        # Atualizar valor global (usado pelo sistema)
        import gesonelbot.config.settings
        gesonelbot.config.settings.OPENAI_API_KEY = api_key
        
        logger.info("Chave de API OpenAI atualizada com sucesso.")
        return True
    
    def update_openai_model(self, model_name: str) -> bool:
        """
        Atualiza o modelo da OpenAI utilizado.
        
        Args:
            model_name: Nome do modelo OpenAI
            
        Returns:
            bool: True se a alteração foi bem-sucedida
        """
        if not model_name:
            logger.error("Nome de modelo inválido.")
            return False
        
        # Atualizar configuração
        self.current_settings['OPENAI_MODEL'] = model_name
        
        # Salvar no arquivo .env
        self._save_to_env("OPENAI_MODEL", model_name)
        
        # Atualizar valor global (usado pelo sistema)
        import gesonelbot.config.settings
        gesonelbot.config.settings.OPENAI_MODEL = model_name
        
        logger.info(f"Modelo OpenAI alterado para: {model_name}")
        return True
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Retorna as configurações atuais.
        
        Returns:
            Dict[str, Any]: Configurações atuais
        """
        # Atualizar com os valores mais recentes
        import gesonelbot.config.settings
        self.current_settings = {
            "MODEL_TYPE": gesonelbot.config.settings.MODEL_TYPE,
            "OPENAI_API_KEY": gesonelbot.config.settings.OPENAI_API_KEY,
            "OPENAI_MODEL": gesonelbot.config.settings.OPENAI_MODEL,
            "LOCAL_MODEL_PATH": gesonelbot.config.settings.LOCAL_MODEL_PATH,
            "LOCAL_MODEL_TYPE": gesonelbot.config.settings.LOCAL_MODEL_TYPE
        }
        
        # Mascarar a API key por segurança
        display_settings = self.current_settings.copy()
        if display_settings['OPENAI_API_KEY']:
            display_settings['OPENAI_API_KEY'] = f"{display_settings['OPENAI_API_KEY'][:5]}...{display_settings['OPENAI_API_KEY'][-4:]}"
        
        return display_settings
    
    def _save_to_env(self, key: str, value: str) -> bool:
        """
        Salva uma configuração no arquivo .env.
        
        Args:
            key: Chave da configuração
            value: Valor da configuração
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Garantir que o diretório existe
            self.env_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Atualizar o arquivo .env
            dotenv.set_key(self.env_path, key, value)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração no arquivo .env: {str(e)}")
            return False

# Instância global para uso em toda a aplicação
settings_manager = SettingsManager() 