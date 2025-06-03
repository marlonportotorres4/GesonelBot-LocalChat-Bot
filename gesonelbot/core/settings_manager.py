"""
Gerenciador de configurações em tempo de execução

Este módulo permite alterar configurações do sistema sem reiniciar a aplicação,
como atualizar as chaves de API e configurações dos provedores.
"""
import os
import logging
import dotenv
from pathlib import Path
from typing import Dict, Any, Optional

# Importar configurações atuais
from gesonelbot.config.settings import (
    API_PROVIDER,
    TOGETHER_API_KEY,
    TOGETHER_MODEL
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
            "API_PROVIDER": API_PROVIDER,
            "TOGETHER_API_KEY": TOGETHER_API_KEY,
            "TOGETHER_MODEL": TOGETHER_MODEL
        }
    
    def update_api_provider(self, provider: str) -> bool:
        """
        Atualiza o provedor de API utilizado.
        
        Args:
            provider: Provedor de API (apenas 'together' é suportado)
            
        Returns:
            bool: True se a alteração foi bem-sucedida
        """
        if provider != 'together':
            logger.error(f"Provedor de API inválido: {provider}. Opção válida: 'together'")
            return False
        
        # Verificar se tem API key configurada para o provedor selecionado
        if not self.current_settings['TOGETHER_API_KEY']:
            logger.warning("A chave API da Together.ai não está configurada. Configure a chave primeiro.")
        
        # Atualizar configuração
        self.current_settings['API_PROVIDER'] = provider
        
        # Salvar no arquivo .env
        self._save_to_env("API_PROVIDER", provider)
        
        # Atualizar valor global (usado pelo sistema)
        import gesonelbot.config.settings
        gesonelbot.config.settings.API_PROVIDER = provider
        
        logger.info(f"Provedor de API atualizado para: {provider}")
        return True
    
    def update_together_api_key(self, api_key: str) -> bool:
        """
        Atualiza a chave de API da Together.ai.
        
        Args:
            api_key: Nova chave de API
            
        Returns:
            bool: True se a alteração foi bem-sucedida
        """
        if not api_key or len(api_key.strip()) < 10:
            logger.error("Chave de API Together.ai inválida ou muito curta.")
            return False
        
        # Atualizar configuração
        self.current_settings['TOGETHER_API_KEY'] = api_key
        
        # Salvar no arquivo .env
        self._save_to_env("TOGETHER_API_KEY", api_key)
        
        # Atualizar valor global (usado pelo sistema)
        import gesonelbot.config.settings
        gesonelbot.config.settings.TOGETHER_API_KEY = api_key
        
        logger.info("Chave de API Together.ai atualizada com sucesso.")
        return True
    
    def update_together_model(self, model_name: str) -> bool:
        """
        Atualiza o modelo da Together.ai utilizado.
        
        Args:
            model_name: Nome do modelo Together.ai
            
        Returns:
            bool: True se a alteração foi bem-sucedida
        """
        if not model_name:
            logger.error("Nome do modelo não pode estar vazio.")
            return False
        
        # Atualizar configuração
        self.current_settings['TOGETHER_MODEL'] = model_name
        
        # Salvar no arquivo .env
        self._save_to_env("TOGETHER_MODEL", model_name)
        
        # Atualizar valor global (usado pelo sistema)
        import gesonelbot.config.settings
        gesonelbot.config.settings.TOGETHER_MODEL = model_name
        
        logger.info(f"Modelo Together.ai configurado para: {model_name}")
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
            "API_PROVIDER": gesonelbot.config.settings.API_PROVIDER,
            "TOGETHER_API_KEY": gesonelbot.config.settings.TOGETHER_API_KEY,
            "TOGETHER_MODEL": gesonelbot.config.settings.TOGETHER_MODEL
        }
        
        # Mascarar as API keys por segurança
        display_settings = self.current_settings.copy()
        if display_settings['TOGETHER_API_KEY']:
            display_settings['TOGETHER_API_KEY'] = f"{display_settings['TOGETHER_API_KEY'][:5]}...{display_settings['TOGETHER_API_KEY'][-4:] if len(display_settings['TOGETHER_API_KEY']) > 8 else ''}"
        
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
            
            # Remover aspas simples ou duplas do valor se existirem
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Atualizar o arquivo .env manualmente para garantir formato correto
            if not os.path.exists(self.env_path):
                with open(self.env_path, 'w') as f:
                    f.write(f"{key}={value}\n")
            else:
                # Ler o arquivo .env
                with open(self.env_path, 'r') as f:
                    lines = f.readlines()
                
                # Procurar e substituir a linha
                key_found = False
                for i, line in enumerate(lines):
                    if line.strip().startswith(f"{key}=") or line.strip().startswith(f"{key} ="):
                        lines[i] = f"{key}={value}\n"
                        key_found = True
                        break
                
                # Se a chave não foi encontrada, adicionar ao final
                if not key_found:
                    lines.append(f"{key}={value}\n")
                
                # Escrever de volta ao arquivo
                with open(self.env_path, 'w') as f:
                    f.writelines(lines)
            
            logger.info(f"Configuração {key} atualizada para {value}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração no arquivo .env: {str(e)}")
            return False

# Instância global para uso em toda a aplicação
settings_manager = SettingsManager() 