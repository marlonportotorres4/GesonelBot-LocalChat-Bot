"""
GesonelBot - Aplicativo para responder perguntas com base em documentos locais

Este módulo implementa a interface do usuário usando Gradio, permitindo
o upload de documentos e a interação com perguntas e respostas.
"""
import os
import sys

# Patch para contornar o erro de pyaudioop no Python 3.13+
import sys
import importlib.util

# Verificar se o módulo audioop está disponível
if importlib.util.find_spec("audioop") is None:
    # Se não estiver disponível, criar um módulo falso
    import types
    audioop_module = types.ModuleType("audioop")
    sys.modules["audioop"] = audioop_module
    
    # Adicionar funções básicas ao módulo falso
    def dummy_func(*args, **kwargs):
        return 0
    
    # Adicionar as funções mais comumente usadas
    audioop_module.avg = dummy_func
    audioop_module.avgpp = dummy_func
    audioop_module.bias = dummy_func
    audioop_module.cross = dummy_func
    audioop_module.findfactor = dummy_func
    audioop_module.findfit = dummy_func
    audioop_module.findmax = dummy_func
    audioop_module.getsample = dummy_func
    audioop_module.lin2lin = dummy_func
    audioop_module.lin2ulaw = dummy_func
    audioop_module.minmax = dummy_func
    audioop_module.mul = dummy_func
    audioop_module.ratecv = dummy_func
    audioop_module.reverse = dummy_func
    audioop_module.rms = dummy_func
    audioop_module.tomono = dummy_func
    audioop_module.tostereo = dummy_func
    audioop_module.ulaw2lin = dummy_func

import gradio as gr
from gesonelbot.core.document_processor import ingest_documents, get_total_upload_usage
from gesonelbot.core.qa_engine import answer_question as qa_answer
from gesonelbot.core.qa_engine import get_model_info, list_available_models
from gesonelbot.core.settings_manager import settings_manager
from gesonelbot.core.llm_manager import llm_manager

# Importação explícita das configurações
from gesonelbot.config.settings import DOCS_DIR as SETTINGS_UPLOAD_DIR
from gesonelbot.config.settings import VECTORSTORE_DIR
from gesonelbot.config.settings import LOCAL_MODEL_NAME

# Definir configurações de limites de upload que não estão presentes no settings.py
MAX_FILE_SIZE_MB = 20  # Tamanho máximo de arquivo em MB
MAX_FILES = 10         # Número máximo de arquivos permitidos

# Fixar o diretório de upload como caminho absoluto
UPLOAD_DIR = os.path.abspath(SETTINGS_UPLOAD_DIR)

# Função para atualizar informações de armazenamento (movida para o início do arquivo)
def update_storage_info():
    current_size, current_files = get_directory_size()
    return f"### Estado atual do sistema\n📊 **Uso de armazenamento:** {current_size:.2f}MB de {MAX_FILE_SIZE_MB}MB\n📁 **Arquivos:** {current_files} de {MAX_FILES}"

# Garantir que as pastas existam
print(f"Diretório de upload configurado: {UPLOAD_DIR}")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Escrever um arquivo de teste para verificar permissões
try:
    test_file_path = os.path.join(UPLOAD_DIR, "test_write.txt")
    with open(test_file_path, 'w') as f:
        f.write("Teste de escrita")
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"Teste de escrita no diretório {UPLOAD_DIR} bem-sucedido")
    else:
        print(f"Falha no teste de escrita - arquivo não foi criado em {UPLOAD_DIR}")
except Exception as e:
    print(f"Erro ao testar escrita no diretório {UPLOAD_DIR}: {str(e)}")

def get_directory_size():
    """
    Calcula o tamanho total dos arquivos no diretório de upload.
    
    Retorna:
        tuple: (tamanho em MB, número de arquivos)
    """
    # Checar se o diretório existe
    if not os.path.exists(UPLOAD_DIR):
        print(f"Diretório de upload não existe: {UPLOAD_DIR}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        return 0.0, 0
    
    total_size = 0
    file_count = 0
    
    # Listar explicitamente arquivos no diretório (apenas nível principal)
    print(f"Verificando arquivos em: {UPLOAD_DIR}")
    try:
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size
                file_count += 1
                print(f"Arquivo encontrado: {filename}, Tamanho: {file_size/1024/1024:.2f}MB")
    except Exception as e:
        print(f"Erro ao listar arquivos: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # Mostrar resultado final
    print(f"Total: {total_size/1024/1024:.2f}MB, {file_count} arquivo(s)")
    return total_size / (1024 * 1024), file_count

def save_file(files):
    """
    Salva os arquivos enviados pelo usuário no diretório de upload e inicia o processamento.
    
    Parâmetros:
        files (list): Lista de objetos de arquivo do Gradio
        
    Retorna:
        tuple: (mensagem de status, atualização de armazenamento)
    """
    # DEBUG - Imprimir o UPLOAD_DIR para verificar seu valor real
    print(f"====> UPLOAD_DIR em save_file: {repr(UPLOAD_DIR)}")
    print(f"====> Este é um caminho absoluto? {os.path.isabs(UPLOAD_DIR)}")
    
    # Verificação de input
    if not files:
        return "⚠️ Nenhum arquivo selecionado. Por favor, escolha arquivos para upload.", update_storage_info()
    
    # Lista para armazenar caminhos dos arquivos salvos
    file_paths = []
    
    # Verificar limite de arquivos
    current_size, current_files = get_directory_size()
    new_files_count = len(files)
    
    print(f"Estado atual: {current_files} arquivos, {current_size:.2f}MB usados")
    print(f"Diretório de upload: {UPLOAD_DIR}")
    
    if current_files + new_files_count > MAX_FILES:
        return f"⚠️ Número máximo de arquivos excedido. Limite: {MAX_FILES} arquivos (atualmente: {current_files})", update_storage_info()
    
    # Importar o módulo de cópia de arquivos
    import shutil
    
    # Processar cada arquivo na lista
    for file_obj in files:
        try:
            # No Gradio 3.50.2, os arquivos são objetos especiais
            # Vamos extrair o caminho de origem e nome do arquivo
            if hasattr(file_obj, 'name') and hasattr(file_obj, 'orig_name'):
                # Este é o formato típico da versão 3.50.2
                source_path = file_obj.name  # Caminho temporário do Gradio
                file_name = file_obj.orig_name  # Nome original do arquivo
            elif isinstance(file_obj, tuple) and len(file_obj) == 2:
                # Algumas versões do Gradio retornam tuplas (caminho, nome)
                source_path, file_name = file_obj
            elif isinstance(file_obj, str) and os.path.exists(file_obj):
                # Pode ser simplesmente um caminho de arquivo
                source_path = file_obj
                file_name = os.path.basename(file_obj)
            elif hasattr(file_obj, 'name'):
                # Tentativa para objetos file-like (Gradio mais recente)
                file_name = os.path.basename(str(file_obj.name))
                source_path = str(file_obj.name) if os.path.exists(str(file_obj.name)) else None
            else:
                # Para objetos temporários
                try:
                    source_path = file_obj.name
                    file_name = os.path.basename(source_path)
                except:
                    return f"❌ Não foi possível identificar o arquivo. Formato desconhecido: {type(file_obj)}", update_storage_info()
            
            # Garantir que temos apenas o nome do arquivo, não o caminho completo
            file_name = os.path.basename(file_name)
            
            # Log detalhado para depuração
            print(f"Processando arquivo: {file_name}")
            print(f"Caminho de origem (temporário): {source_path}")
            print(f"Tipo do objeto: {type(file_obj)}")
            
            # Verificar se o caminho de origem existe e tem conteúdo
            if not source_path or not os.path.exists(source_path):
                return f"❌ Caminho temporário do arquivo {file_name} não encontrado.", update_storage_info()
                
            if os.path.getsize(source_path) == 0:
                return f"❌ Arquivo de origem {file_name} está vazio.", update_storage_info()
            
            # Verificar formato do arquivo
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in ['.pdf', '.docx', '.txt']:
                return f"⚠️ Formato de arquivo não suportado: {ext}. Use PDF, DOCX ou TXT.", update_storage_info()
                
            # Garantir que o diretório de destino exista
            if not os.path.exists(UPLOAD_DIR):
                print(f"Recriando diretório de upload: {UPLOAD_DIR}")
                os.makedirs(UPLOAD_DIR, exist_ok=True)
            
            # CORRETO: Definir o caminho final no UPLOAD_DIR usando apenas o nome do arquivo
            # Importante: Não usar os.path.join com qualquer parte do caminho temporário!
            final_path = UPLOAD_DIR + os.sep + file_name  # Forçar a concatenação direta
            
            print(f"Tentando salvar arquivo em: {final_path}")
            print(f"Este caminho usa UPLOAD_DIR? {final_path.startswith(UPLOAD_DIR)}")
            
            # Método seguro para salvar o arquivo no destino correto
            try:
                # Abrir o arquivo de origem e ler todo o conteúdo
                with open(source_path, 'rb') as src_file:
                    content = src_file.read()
                    
                # Verificar se leu corretamente
                if not content:
                    return f"❌ Não foi possível ler o conteúdo do arquivo {file_name}", update_storage_info()
                    
                # Escrever o conteúdo no arquivo de destino diretamente
                with open(final_path, 'wb') as dest_file:
                    dest_file.write(content)
                    
                print(f"Arquivo salvo diretamente em: {final_path}")
            except Exception as e:
                print(f"Erro salvando diretamente: {str(e)}")
                # Tentar outro método se o primeiro falhar
                try:
                    shutil.copyfile(source_path, final_path)  # Usar copyfile em vez de copy2
                    print(f"Arquivo copiado via shutil para: {final_path}")
                except Exception as e2:
                    return f"❌ Falha ao copiar o arquivo. Erros: {str(e)} e {str(e2)}", update_storage_info()
            
            # Verificar se o arquivo realmente foi salvo no diretório correto
            if not os.path.exists(final_path):
                return f"❌ Arquivo não existe após tentativa de cópia: {final_path}", update_storage_info()
                
            if os.path.getsize(final_path) == 0:
                return f"❌ Arquivo salvo mas está vazio: {final_path}", update_storage_info()
            
            # Verificar se o arquivo realmente está no diretório UPLOAD_DIR (debug)
            expected_dir = os.path.dirname(final_path)
            is_in_upload_dir = os.path.samefile(expected_dir, UPLOAD_DIR) if os.path.exists(expected_dir) and os.path.exists(UPLOAD_DIR) else False
            print(f"Arquivo está no diretório UPLOAD_DIR? {is_in_upload_dir}")
            
            # Listar arquivos no diretório 
            print(f"Arquivos no UPLOAD_DIR após salvamento:")
            for f in os.listdir(UPLOAD_DIR):
                f_path = os.path.join(UPLOAD_DIR, f)
                print(f" - {f}: {os.path.getsize(f_path)} bytes")
                
            print(f"Arquivo salvo com sucesso: {final_path}, Tamanho: {os.path.getsize(final_path)/1024/1024:.2f}MB")
            
            # Verificar tamanho do arquivo
            if os.path.getsize(final_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
                os.remove(final_path)  # Remover arquivo muito grande
                return f"⚠️ Arquivo {file_name} excede o limite de {MAX_FILE_SIZE_MB}MB", update_storage_info()
            
            # Adicionar à lista de arquivos salvos
            file_paths.append(final_path)
            
        except Exception as e:
            # Capturar erros detalhados
            import traceback
            error_details = traceback.format_exc()
            return f"❌ Erro ao processar {file_name if 'file_name' in locals() else 'arquivo'}: {str(e)}\n\nDetalhes: {error_details}", update_storage_info()
    
    # Se chegou aqui, todos os arquivos foram salvos
    try:
        # Garantir que os caminhos para ingest_documents sejam os definitivos
        results = ingest_documents(file_paths)
        
        # Verificar novamente os arquivos após processamento
        current_size, current_files = get_directory_size()
        print(f"Estado após processamento: {current_files} arquivos, {current_size:.2f}MB usados")
        
        # Listar explicitamente todos os arquivos na pasta
        print("Arquivos encontrados em UPLOAD_DIR após processamento:")
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            print(f" - {filename}: {os.path.getsize(file_path)/1024/1024:.2f}MB")
        
        message = f"✅ {len(files)} arquivo(s) salvo(s) e processado(s) com sucesso!\n\n"
        message += f"📊 {results['success_count']} processados, {results['error_count']} erros.\n"
        message += f"💾 Uso atual: {current_size:.2f}MB de {MAX_FILE_SIZE_MB}MB ({current_files} de {MAX_FILES} arquivos)\n"
        
        # Adicionar detalhes se houver erros
        if results['error_count'] > 0:
            message += "\nErros encontrados:\n"
            for error in results['errors']:
                message += f"- {error['file_name']}: {error['message']}\n"
                
        return message, update_storage_info()
    except Exception as e:
        # Arquivo foi salvo mas houve erro no processamento
        import traceback
        error_details = traceback.format_exc()
        return f"✅ {len(files)} arquivo(s) salvo(s), mas houve erro no processamento: {str(e)}\n\nDetalhes: {error_details}", update_storage_info()

def answer_question(question, chat_history):
    """
    Processa uma pergunta do usuário e adiciona a resposta ao histórico de chat.
    
    Args:
        question: Pergunta do usuário
        chat_history: Histórico atual do chat
    
    Returns:
        Histórico de chat atualizado e campo de mensagem limpo
    """
    if not question or question.strip() == "":
        return chat_history, ""
    
    # Adicionar a pergunta do usuário ao histórico
    chat_history = chat_history + [(question, None)]
    
    try:
        # Obter resposta do motor de QA
        result = qa_answer(question)
        
        # Extrair a resposta
        response = result.get("answer", "Desculpe, não consegui processar sua pergunta.")
        
        # Atualizar o histórico com a resposta
        chat_history[-1] = (question, response)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao processar pergunta: {str(e)}\n{error_details}")
        
        # Em caso de erro, adicionar mensagem de erro ao histórico
        error_message = f"Ocorreu um erro ao processar sua pergunta: {str(e)}"
        chat_history[-1] = (question, error_message)
    
    # Retornar o histórico atualizado e limpar o campo de pergunta
    return chat_history, ""

def get_model_status():
    """
    Obtém o status atual do modelo de linguagem.
    
    Returns:
        str: Status formatado em Markdown
    """
    from gesonelbot.core.llm_manager import llm_manager
    
    model_info = llm_manager.get_model_info()
    
    status = "### Status do Modelo\n"
    
    # Verificar se o modelo está carregado
    if model_info.get("status") == "carregado":
        status += "✅ **Estado**: Modelo carregado e pronto para uso\n\n"
        status += f"**Nome do modelo**: {model_info.get('name', 'Desconhecido')}\n"
        status += f"**Tipo**: Modelo local\n"
        status += f"**Quantização**: {model_info.get('quantization', 'Nenhuma')}\n"
        status += f"**Dispositivo**: {model_info.get('device', 'CPU')}\n"
        status += f"**Temperatura**: {model_info.get('temperature', 0.7)}\n"
        status += f"**Tokens máximos**: {model_info.get('max_tokens', 512)}\n"
    else:
        status += "⚠️ **Estado**: Modelo não carregado\n\n"
        status += "O modelo será carregado automaticamente quando você fizer a primeira pergunta.\n"
        status += f"**Nome do modelo configurado**: {model_info.get('name', 'Desconhecido')}\n"
        status += "Isso pode levar alguns minutos na primeira execução."
    
    status += "\n"
    
    return status

# Interface principal do Gradio
def create_interface():
    """
    Cria a interface Gradio para a aplicação.
    
    Returns:
        Interface Gradio
    """
    with gr.Blocks(title="GesonelBot - Seu chat bot local", theme=gr.themes.Soft()) as demo:
        # Cabeçalho
        gr.Markdown("# 📚 GesonelBot")
        gr.Markdown("### Seu assistente de documentos com chat integrado")
        
        # Aba de Upload de Documentos
        with gr.Tab("Upload de Documentos"):
            # Estado atual de uso de armazenamento
            current_size, current_files = get_directory_size()
            
            with gr.Row():
                storage_info = gr.Markdown(
                    f"### Estado atual do sistema\n"
                    f"📊 **Uso de armazenamento:** {current_size:.2f}MB de {MAX_FILE_SIZE_MB}MB\n"
                    f"📁 **Arquivos:** {current_files} de {MAX_FILES}"
                )
                refresh_btn = gr.Button("🔄 Atualizar", variant="secondary")
            
            with gr.Column():
                # Componente para upload de arquivos
                files_input = gr.File(
                    file_count="multiple",  # Permitir múltiplos arquivos
                    label=f"Carregar documentos (PDF, DOCX, TXT) - Limite: {MAX_FILES} arquivos, {MAX_FILE_SIZE_MB}MB total",
                    file_types=["pdf", "docx", "txt", ".pdf", ".docx", ".txt"]  # Tentar diferentes formatos de especificação
                )
                
                # Nota sobre gerenciamento de arquivos
                gr.Markdown("""
                **Nota:** Para remover arquivos específicos da seleção, use o botão X 
                no canto superior direito de cada arquivo na lista ou clique no botão X acima 
                da lista para remover todos.
                """)
                
                # Botão para processamento
                upload_button = gr.Button("📤 Processar Documentos", variant="primary")
                
                # Explicação sobre formatos suportados
                gr.Markdown(f"""
                **Formatos suportados:**
                - PDF (`.pdf`) - Documentos, artigos, manuais
                - Word (`.docx`) - Documentos do Microsoft Word
                - Texto (`.txt`) - Arquivos de texto simples
                
                **Limites:**
                - Máximo de arquivos: {MAX_FILES}
                - Tamanho total máximo: {MAX_FILE_SIZE_MB}MB
                - Tamanho máximo por arquivo: {MAX_FILE_SIZE_MB}MB
                """)
                
                # Área para exibição de status
                upload_output = gr.Textbox(
                    label="Status",
                    placeholder="Os resultados do processamento aparecerão aqui...",
                    interactive=False
                )
                
                # Conectar o botão à função de processamento (agora com dois outputs)
                upload_button.click(
                    save_file, 
                    inputs=[files_input], 
                    outputs=[upload_output, storage_info]
                )
                
                # Conectar o botão de atualização para mostrar estatísticas atualizadas
                refresh_btn.click(update_storage_info, inputs=[], outputs=[storage_info])
        
        # Aba de Chat
        with gr.Tab("Chat"):
            # Componente de chat para exibir histórico e mensagens
            chatbot = gr.Chatbot(
                label="Conversa",
                height=500,
                bubble=True,
                avatar_images=("👤", "🤖")
            )
            
            # Interface para mensagens do usuário
            with gr.Row():
                user_message = gr.Textbox(
                    placeholder="Digite sua pergunta sobre os documentos...", 
                    scale=8,
                    show_label=False,
                    container=False
                )
                submit_btn = gr.Button("Enviar", variant="primary", scale=1)
            
            # Botões de ação
            with gr.Row():
                clear_btn = gr.Button("Limpar Conversa", variant="secondary")
                example_btn = gr.Button("Pergunta Exemplo", variant="secondary")
            
            # Exemplos de perguntas
            examples = [
                "O que é mencionado sobre...?",
                "Quais são os principais tópicos abordados?",
                "Poderia resumir o documento?",
                "Qual é a conclusão do texto sobre...?",
                "Existe alguma menção a...?"
            ]
            
            # Ações dos botões
            submit_btn.click(
                answer_question, 
                [user_message, chatbot], 
                [chatbot, user_message]
            )
            
            # Também permitir enviar com Enter
            user_message.submit(
                answer_question, 
                [user_message, chatbot], 
                [chatbot, user_message]
            )
            
            # Limpar conversa
            clear_btn.click(lambda: [], None, chatbot)
            
            # Inserir exemplo
            def load_example():
                import random
                return random.choice(examples)
            
            example_btn.click(load_example, None, user_message)
            
            # Informações sobre o chat
            gr.Markdown("""
            ### Dicas de Uso do Chat
            
            - Seja específico em suas perguntas para obter melhores respostas
            - O assistente tem conhecimento apenas sobre os documentos que você carregou
            - Use a aba "Upload de Documentos" para adicionar mais conteúdo
            - Você pode limpar a conversa a qualquer momento
            """)
        
        # Nova aba de Configurações
        with gr.Tab("Configurações"):
            # Exibir status atual do modelo
            model_status = gr.Markdown(get_model_status())
            refresh_model_btn = gr.Button("🔄 Atualizar Status", variant="secondary")
            
            gr.Markdown("### Informações do Modelo")
            
            # Informações sobre os modelos
            gr.Markdown("""
            ### Modelo utilizado: TinyLlama - Modelo Local

            **TinyLlama**
            - Modelo de linguagem compacto executado localmente
            - Projetado para funcionar em hardware comum
            - Processamento de documentos e respostas sem necessidade de conexão constante com internet
            - Todas as operações ocorrem no seu próprio computador
            
            **Observação:** O primeiro carregamento do modelo pode levar alguns minutos.
            O desempenho depende das capacidades do seu hardware.
            """)
            
            # Atualizar status do modelo
            refresh_model_btn.click(
                get_model_status,
                inputs=[],
                outputs=[model_status]
            )
        
        # Explicação sobre como funciona
        with gr.Accordion("Como usar o GesonelBot", open=False):
            gr.Markdown("""
            ### Instruções de uso:
            
            1. **Upload de Documentos**:
               - Na primeira aba, faça upload de arquivos PDF, DOCX ou TXT
               - Clique no botão "Processar Documentos"
               - Aguarde o processamento (isto pode levar alguns segundos)
            
            2. **Chat com o Assistente**:
               - Vá para a segunda aba "Chat"
               - Digite sua pergunta e pressione Enter ou clique em "Enviar"
               - O sistema buscará informações relevantes nos documentos e responderá
               - Seu histórico de conversas ficará visível e organizado
               - Use "Limpar Conversa" para reiniciar o chat
               
            3. **Configurações**:
               - Na terceira aba, você pode ver as configurações do sistema
               - O sistema usa um modelo de IA local para respostas rápidas sem dependência de serviços externos
            
            **Nota:** Esta é a versão local do GesonelBot, otimizada para funcionar completamente em seu computador.
            """)
    
    return demo

# Função para iniciar a aplicação
def launch_app(share=False):
    """
    Inicia a aplicação Gradio.
    
    Args:
        share (bool): Se True, compartilha a interface publicamente
    """
    demo = create_interface()
    demo.launch(share=share) 