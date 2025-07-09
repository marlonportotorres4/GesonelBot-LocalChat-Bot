"""
Gerenciador de configurações para o GesonelBot.

Este módulo permite gerenciar as configurações do sistema, incluindo
modificações em tempo de execução e persistência das configurações.
"""
import os
import logging
import importlib
from typing import Dict, Any, Optional, Union

# Configurações
from gesonelbot.config.settings import (
    LOCAL_MODEL_NAME,
    USE_8BIT_QUANTIZATION,
    USE_4BIT_QUANTIZATION,
    USE_CPU_ONLY,
    QA_TEMPERATURE,
    QA_MAX_TOKENS
)

# Configurar logging
logger = logging.getLogger(__name__)

class SettingsManager:
    """
    Gerencia as configurações do GesonelBot.
    
    Permite atualizar configurações em tempo de execução e persistir
    as alterações no arquivo .env.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de configurações."""
        self.current_settings = {
            "LOCAL_MODEL_NAME": LOCAL_MODEL_NAME,
            "USE_8BIT_QUANTIZATION": USE_8BIT_QUANTIZATION,
            "USE_4BIT_QUANTIZATION": USE_4BIT_QUANTIZATION,
            "USE_CPU_ONLY": USE_CPU_ONLY,
            "QA_TEMPERATURE": QA_TEMPERATURE,
            "QA_MAX_TOKENS": QA_MAX_TOKENS
        }
    
    def update_model_name(self, model_name: str) -> bool:
        """
        Atualiza o nome do modelo local a ser utilizado.
        
        Args:
            model_name: Nome do modelo no formato Hugging Face
            
        Returns:
            bool: True se a atualização foi bem-sucedida
        """
        if not model_name or len(model_name) < 3:
            logger.error("Nome de modelo inválido ou muito curto.")
            return False
        
        try:
            # Atualizar configuração em memória
            self.current_settings['LOCAL_MODEL_NAME'] = model_name
            
            # Salvar no arquivo .env
            self._save_to_env("LOCAL_MODEL_NAME", model_name)
            
            # Atualizar variável global
            import gesonelbot.config.settings
            gesonelbot.config.settings.LOCAL_MODEL_NAME = model_name
            
            logger.info(f"Modelo configurado para: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração do modelo: {str(e)}")
            return False
    
    def update_quantization(self, use_8bit: bool, use_4bit: bool) -> bool:
        """
        Atualiza as configurações de quantização.
        
        Args:
            use_8bit: Se True, usa quantização de 8 bits
            use_4bit: Se True, usa quantização de 4 bits
            
        Returns:
            bool: True se a atualização foi bem-sucedida
        """
        try:
            # Não permitir ambas as opções habilitadas ao mesmo tempo
            if use_8bit and use_4bit:
                logger.warning("Não é possível habilitar quantização de 8 bits e 4 bits simultaneamente.")
                use_4bit = False
            
            # Atualizar configurações em memória
            self.current_settings['USE_8BIT_QUANTIZATION'] = use_8bit
            self.current_settings['USE_4BIT_QUANTIZATION'] = use_4bit
            
            # Salvar no arquivo .env
            self._save_to_env("USE_8BIT_QUANTIZATION", str(use_8bit))
            self._save_to_env("USE_4BIT_QUANTIZATION", str(use_4bit))
            
            # Atualizar variáveis globais
            import gesonelbot.config.settings
            gesonelbot.config.settings.USE_8BIT_QUANTIZATION = use_8bit
            gesonelbot.config.settings.USE_4BIT_QUANTIZATION = use_4bit
            
            logger.info(f"Configurações de quantização atualizadas: 8-bit={use_8bit}, 4-bit={use_4bit}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações de quantização: {str(e)}")
            return False
    
    def update_generation_params(self, temperature: float, max_tokens: int) -> bool:
        """
        Atualiza os parâmetros de geração de texto.
        
        Args:
            temperature: Temperatura para amostragem (0.0 a 1.0)
            max_tokens: Número máximo de tokens a gerar
            
        Returns:
            bool: True se a atualização foi bem-sucedida
        """
        try:
            # Validar parâmetros
            if temperature < 0.0 or temperature > 1.0:
                logger.warning(f"Temperatura inválida: {temperature}. Usando valor padrão de 0.7.")
                temperature = 0.7
            
            if max_tokens < 50 or max_tokens > 2000:
                logger.warning(f"Valor de max_tokens inválido: {max_tokens}. Usando valor padrão de 512.")
                max_tokens = 512
            
            # Atualizar configurações em memória
            self.current_settings['QA_TEMPERATURE'] = temperature
            self.current_settings['QA_MAX_TOKENS'] = max_tokens
            
            # Salvar no arquivo .env
            self._save_to_env("QA_TEMPERATURE", str(temperature))
            self._save_to_env("QA_MAX_TOKENS", str(max_tokens))
            
            # Atualizar variáveis globais
            import gesonelbot.config.settings
            gesonelbot.config.settings.QA_TEMPERATURE = temperature
            gesonelbot.config.settings.QA_MAX_TOKENS = max_tokens
            
            logger.info(f"Parâmetros de geração atualizados: temperatura={temperature}, max_tokens={max_tokens}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar parâmetros de geração: {str(e)}")
            return False
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Retorna as configurações atuais.
        
        Returns:
            Dict[str, Any]: Configurações atuais
        """
        # Atualizar configurações a partir dos valores mais recentes
        import gesonelbot.config.settings
        settings = {
            "LOCAL_MODEL_NAME": gesonelbot.config.settings.LOCAL_MODEL_NAME,
            "USE_8BIT_QUANTIZATION": gesonelbot.config.settings.USE_8BIT_QUANTIZATION,
            "USE_4BIT_QUANTIZATION": gesonelbot.config.settings.USE_4BIT_QUANTIZATION,
            "USE_CPU_ONLY": gesonelbot.config.settings.USE_CPU_ONLY,
            "QA_TEMPERATURE": gesonelbot.config.settings.QA_TEMPERATURE,
            "QA_MAX_TOKENS": gesonelbot.config.settings.QA_MAX_TOKENS
        }
        
        return settings
    
    def _save_to_env(self, key: str, value: str) -> bool:
        """
        Salva uma configuração no arquivo .env.
        
        Args:
            key: Nome da configuração
            value: Valor da configuração
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Ler o arquivo .env
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            
            if not os.path.exists(env_path):
                logger.warning(f"Arquivo .env não encontrado em {env_path}. Criando arquivo...")
                with open(env_path, 'w') as f:
                    f.write(f"{key}={value}\n")
                return True
            
            # Ler o conteúdo atual
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Verificar se a chave já existe
            key_exists = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    key_exists = True
                    break
            
            # Se a chave não existir, adicionar ao final
            if not key_exists:
                lines.append(f"{key}={value}\n")
            
            # Escrever de volta ao arquivo
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logger.info(f"Configuração '{key}' atualizada no arquivo .env")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração no arquivo .env: {str(e)}")
            return False

# Instância global para uso em toda a aplicação
settings_manager = SettingsManager() 