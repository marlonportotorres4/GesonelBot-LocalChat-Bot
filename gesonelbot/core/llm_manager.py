"""
Gerenciador de Modelos de Linguagem (LLM)

Este módulo gerencia o modelo de linguagem para geração de respostas,
utilizando o modelo TinyLlama localmente.
"""
import os
import logging
import json
from typing import Dict, Any, Optional, Union, List

# Importações necessárias para o modelo local
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

# Configurações
from gesonelbot.config.settings import (
    LOCAL_MODEL_NAME,
    QA_TEMPERATURE,
    QA_MAX_TOKENS,
    SYSTEM_TEMPLATE,
    MODEL_CACHE_DIR,
    USE_8BIT_QUANTIZATION,
    USE_4BIT_QUANTIZATION,
    USE_CPU_ONLY
)

# Configurar logging
logger = logging.getLogger(__name__)

class LLMManager:
    """
    Gerencia o modelo de linguagem para geração de texto.
    
    Esta classe oferece uma interface para modelos de linguagem locais
    usando a biblioteca Transformers do Hugging Face.
    
    O modelo é carregado sob demanda para economizar recursos.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de modelos."""
        self.model_type = "local"
        self.current_model = None
        self.tokenizer = None
        self.generator = None
        self.model_info = {}
        
        # Verificar configurações iniciais
        logger.info(f"Inicializando LLM Manager com modelo local: {LOCAL_MODEL_NAME}")
    
    def load_model(self) -> bool:
        """
        Carrega o modelo local.
        
        Returns:
            bool: True se o modelo foi carregado com sucesso
        """
        logger.info(f"Carregando modelo local: {LOCAL_MODEL_NAME}")
        try:
            # Configurar diretório de cache
            os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
            
            # Determinar configuração de quantização
            quantization_config = None
            device_map = "auto"
            
            if USE_CPU_ONLY:
                device_map = "cpu"
                logger.info("Usando apenas CPU para o modelo")
            
            if USE_8BIT_QUANTIZATION and not USE_CPU_ONLY:
                logger.info("Usando quantização de 8 bits")
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            elif USE_4BIT_QUANTIZATION and not USE_CPU_ONLY:
                logger.info("Usando quantização de 4 bits")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
            
            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                LOCAL_MODEL_NAME,
                cache_dir=MODEL_CACHE_DIR
            )
            
            # Carregar modelo com otimizações para CPU
            if USE_CPU_ONLY:
                # Usar configurações otimizadas para CPU
                self.current_model = AutoModelForCausalLM.from_pretrained(
                    LOCAL_MODEL_NAME,
                    device_map=device_map,
                    cache_dir=MODEL_CACHE_DIR,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
            else:
                # Configuração padrão para GPU
                self.current_model = AutoModelForCausalLM.from_pretrained(
                    LOCAL_MODEL_NAME,
                    device_map=device_map,
                    quantization_config=quantization_config,
                    cache_dir=MODEL_CACHE_DIR,
                    torch_dtype=torch.float16
                )
            
            # Criar pipeline de geração de texto com configurações otimizadas
            self.generator = pipeline(
                "text-generation",
                model=self.current_model,
                tokenizer=self.tokenizer
            )
            
            # Atualizar informações do modelo
            self.model_info = {
                "type": "local",
                "name": LOCAL_MODEL_NAME,
                "max_tokens": QA_MAX_TOKENS,
                "temperature": QA_TEMPERATURE,
                "modo": "local",
                "quantization": "8bit" if USE_8BIT_QUANTIZATION else ("4bit" if USE_4BIT_QUANTIZATION else "none"),
                "device": "cpu" if USE_CPU_ONLY else str(self.current_model.device)
            }
            
            logger.info(f"Modelo local carregado: {LOCAL_MODEL_NAME}")
            return True
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Erro ao carregar modelo local: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            return False
    
    def reload_settings(self):
        """
        Recarrega as configurações e atualiza o modelo se necessário.
        
        Esta função deve ser chamada quando as configurações forem alteradas
        para garantir que o modelo atual seja atualizado.
        """
        # Reimportar as configurações
        import importlib
        import gesonelbot.config.settings
        importlib.reload(gesonelbot.config.settings)
        
        # Atualizar variáveis locais
        from gesonelbot.config.settings import (
            LOCAL_MODEL_NAME
        )
        
        # Verificar se configurações importantes mudaram
        if self.current_model:
            # Recarregar modelo se o modelo mudou
            current_model_name = self.model_info.get("name")
            if current_model_name != LOCAL_MODEL_NAME:
                logger.info(f"Modelo local alterado de {current_model_name} para {LOCAL_MODEL_NAME}")
                self.current_model = None
                self.tokenizer = None
                self.generator = None
                self.load_model()
    
    def format_prompt_for_model(self, prompt: str, system_prompt: str) -> str:
        """
        Formata o prompt para o modelo TinyLlama no formato correto.
        
        Args:
            prompt: O prompt do usuário
            system_prompt: O prompt do sistema
        
        Returns:
            O prompt formatado para o modelo
        """
        # TinyLlama usa o formato:
        # <|system|>
        # system_prompt
        # <|user|>
        # user_prompt
        # <|assistant|>
        
        formatted_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>"
        return formatted_prompt
    
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
        if not self.current_model or not self.tokenizer or not self.generator:
            logger.info("Modelo não carregado. Carregando modelo...")
            success = self.load_model()
            
            if not success:
                return "Erro: Não foi possível carregar o modelo local. Verifique os logs para mais detalhes."
        
        # Gerar resposta
        try:
            # Parâmetros para a geração
            temperature = kwargs.get("temperature", QA_TEMPERATURE)
            max_tokens = kwargs.get("max_tokens", QA_MAX_TOKENS)
            
            # Usar o sistema prompt personalizado se fornecido, caso contrário usar o padrão
            system_prompt = kwargs.get("system_prompt", SYSTEM_TEMPLATE.format(app_name="GesonelBot"))
            
            # Formatar o prompt para o modelo
            formatted_prompt = self.format_prompt_for_model(prompt, system_prompt)
            
            logger.info(f"Enviando prompt para modelo local: {LOCAL_MODEL_NAME}")
            logger.info(f"Parâmetros da chamada: temperatura={temperature}, max_tokens={max_tokens}")
            logger.debug(f"Prompt completo: {formatted_prompt[:500]}...")
            
            # Gerar resposta com configurações otimizadas para evitar travamentos
            generation_config = {
                "max_new_tokens": min(max_tokens, 256),  # Limitar para evitar problemas
                "temperature": temperature,
                "top_p": 0.9,
                "do_sample": temperature > 0.0,
                "pad_token_id": self.tokenizer.eos_token_id,
                "num_return_sequences": 1,
                "repetition_penalty": 1.2,  # Evitar repetições
                "no_repeat_ngram_size": 3  # Evitar repetição de n-gramas
            }
            
            output = self.generator(
                formatted_prompt,
                **generation_config
            )
            
            # Extrair apenas a resposta gerada (sem repetir o prompt)
            generated_text = output[0]['generated_text']
            
            # Remover o prompt do início da resposta
            response = generated_text.split("<|assistant|>")[-1].strip()
            
            # Verificar se a resposta está vazia ou muito curta
            if not response or len(response) < 5:
                return "Desculpe, não consegui gerar uma resposta adequada. O modelo TinyLlama pode ter limitações para este tipo de consulta."
                
            return response
                
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
            return {"status": "não carregado", "type": self.model_type, "name": LOCAL_MODEL_NAME}
        
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
        
        # Informações sobre o modelo atual/configurado
        models.append({
            "name": LOCAL_MODEL_NAME,
            "type": "local",
            "status": "ativo" if self.current_model else "não carregado",
            "modo": "local",
            "quantization": "8bit" if USE_8BIT_QUANTIZATION else ("4bit" if USE_4BIT_QUANTIZATION else "none")
        })
        
        return models

# Instância global para uso em toda a aplicação
llm_manager = LLMManager() 