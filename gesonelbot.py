#!/usr/bin/env python
"""
GesonelBot - Ponto de entrada principal

Este script inicia a aplicação GesonelBot.
"""
from gesonelbot.ui.app import launch_app
from gesonelbot.config.settings import verify_config

if __name__ == "__main__":
    # Verificar configurações antes de iniciar
    config_ok = verify_config()
    if not config_ok:
        print("AVISO: Algumas configurações não estão corretas. A aplicação pode não funcionar corretamente.")
    
    # Iniciar a aplicação
    print("Iniciando GesonelBot...")
    launch_app(share=False) 