"""
GesonelBot - Aplicativo para responder perguntas com base em documentos locais

Este módulo implementa a interface do usuário usando Gradio, permitindo
o upload de documentos e a interação com perguntas e respostas.
"""
import os
import gradio as gr
from gesonelbot.core.document_processor import ingest_documents
from gesonelbot.core.qa_engine import answer_question as qa_answer
from gesonelbot.config.settings import UPLOAD_DIR, VECTORSTORE_DIR, MAX_FILE_SIZE_MB, MAX_FILES

# Garantir que as pastas existam
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

def get_directory_size():
    """
    Calcula o tamanho total dos arquivos no diretório de upload.
    
    Retorna:
        tuple: (tamanho em MB, número de arquivos)
    """
    total_size = 0
    file_count = 0
    
    for dirpath, _, filenames in os.walk(UPLOAD_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
            file_count += 1
    
    return total_size / (1024 * 1024), file_count  # Converter para MB

def save_file(files):
    """
    Salva os arquivos enviados pelo usuário no diretório de upload e inicia o processamento.
    
    Parâmetros:
        files (list): Lista de objetos de arquivo do Gradio
        
    Retorna:
        str: Mensagem de status da operação
    """
    # Verificação de input
    if not files:
        return "⚠️ Nenhum arquivo selecionado. Por favor, escolha arquivos para upload."
    
    # Verificar limite de arquivos
    current_size, current_files = get_directory_size()
    new_files_count = len(files)
    
    if current_files + new_files_count > MAX_FILES:
        return f"⚠️ Número máximo de arquivos excedido. Limite: {MAX_FILES} arquivos (atualmente: {current_files})"
    
    # Lista para armazenar caminhos dos arquivos salvos
    file_paths = []
    total_new_size = 0
    
    # Primeiro, calcular o tamanho total dos novos arquivos
    for file in files:
        try:
            if hasattr(file, 'read'):
                content = file.read()
                total_new_size += len(content)
                file.seek(0)  # Resetar o ponteiro do arquivo
            elif isinstance(file, str) and os.path.exists(file):
                total_new_size += os.path.getsize(file)
        except Exception as e:
            return f"❌ Erro ao verificar tamanho do arquivo: {str(e)}"
    
    # Verificar se o tamanho total excede o limite
    if current_size + (total_new_size / (1024 * 1024)) > MAX_FILE_SIZE_MB:
        return f"⚠️ Capacidade total excedida. Limite: {MAX_FILE_SIZE_MB}MB (atualmente: {current_size:.2f}MB)"
    
    # Iterar sobre cada arquivo e salvá-lo
    for file in files:
        try:
            # Determinar o nome do arquivo
            if hasattr(file, 'name'):
                file_name = os.path.basename(file.name)
            elif isinstance(file, str):
                file_name = os.path.basename(file)
            else:
                file_name = f"arquivo_{len(file_paths) + 1}.txt"
                
            # Criar caminho completo para o arquivo de destino
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            # Técnica 1: Método de leitura e escrita para qualquer tipo de arquivo
            if hasattr(file, 'read'):
                # Para objetos tipo arquivo
                content = file.read()
                
                # Verificar tamanho do arquivo individual
                if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                    return f"⚠️ Arquivo {file_name} excede o limite de {MAX_FILE_SIZE_MB}MB"
                
                with open(file_path, 'wb') as dest_file:
                    dest_file.write(content)
                    
            elif isinstance(file, str) and os.path.exists(file):
                # Para caminhos de arquivos (comum no Gradio)
                # Verificar tamanho do arquivo individual
                if os.path.getsize(file) > MAX_FILE_SIZE_MB * 1024 * 1024:
                    return f"⚠️ Arquivo {file_name} excede o limite de {MAX_FILE_SIZE_MB}MB"
                
                # Usar leitura/escrita manual em vez de shutil.copy2
                with open(file, 'rb') as src_file:
                    content = src_file.read()
                with open(file_path, 'wb') as dest_file:
                    dest_file.write(content)
            else:
                return f"❌ Formato de arquivo não suportado: {type(file).__name__}"
                
            # Adicionar caminho à lista de arquivos processados
            file_paths.append(file_path)
            
        except Exception as e:
            # Retornar mensagem de erro detalhada para depuração
            import traceback
            error_details = traceback.format_exc()
            return f"❌ Erro ao salvar o arquivo: {str(e)}\n\nDetalhes: {error_details}"
    
    # Verificação básica de tipos de arquivo 
    unsupported_files = []
    for path in file_paths:
        # Extrair a extensão do arquivo e converter para minúsculas
        ext = os.path.splitext(path)[1].lower()
        
        # Verificar se a extensão está na lista de formatos suportados
        if ext not in ['.pdf', '.docx', '.txt']:
            # Adicionar à lista de arquivos não suportados
            unsupported_files.append(os.path.basename(path))
    
    # Informar sobre arquivos não suportados, se houver
    if unsupported_files:
        return f"⚠️ {len(files)} arquivo(s) salvo(s), mas alguns formatos não são suportados: {', '.join(unsupported_files)}. Por favor, envie apenas arquivos PDF, DOCX ou TXT."
    
    # Processar os documentos
    try:
        results = ingest_documents(file_paths)
        current_size, current_files = get_directory_size()
        
        message = f"✅ {len(files)} arquivo(s) salvo(s) e processado(s) com sucesso!\n\n"
        message += f"📊 {results['success_count']} processados, {results['error_count']} erros.\n"
        message += f"💾 Uso atual: {current_size:.2f}MB de {MAX_FILE_SIZE_MB}MB ({current_files} de {MAX_FILES} arquivos)\n"
        
        # Adicionar detalhes se houver erros
        if results['error_count'] > 0:
            message += "\nErros encontrados:\n"
            for error in results['errors']:
                message += f"- {error['file_name']}: {error['message']}\n"
                
        return message
    except Exception as e:
        # Arquivo foi salvo mas houve erro no processamento
        return f"✅ {len(files)} arquivo(s) salvo(s), mas houve erro no processamento: {str(e)}"

def answer_question(question, chat_history):
    """
    Função para responder perguntas utilizando o motor de QA.
    
    Parâmetros:
        question (str): A pergunta do usuário
        chat_history (list): Histórico de conversas anteriores
        
    Retorna:
        tuple: (histórico atualizado, '')
    """
    if not question:
        return chat_history, ""
    
    # Utilizando o motor de QA para responder à pergunta
    result = qa_answer(question)
    
    # Adicionar a pergunta e resposta ao histórico
    chat_history = chat_history + [(question, result["answer"])]
    
    return chat_history, ""

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
            with gr.Column():
                # Componente para upload de arquivos
                files_input = gr.File(
                    file_count="multiple",  # Permitir múltiplos arquivos
                    label=f"Carregar documentos (PDF, DOCX, TXT) - Limite: {MAX_FILES} arquivos, {MAX_FILE_SIZE_MB}MB total",
                    file_types=["pdf", "docx", "txt", ".pdf", ".docx", ".txt"]  # Tentar diferentes formatos de especificação
                )
                
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
                
                # Botão para iniciar o processamento
                upload_button = gr.Button("Processar Documentos", variant="primary")
                
                # Área para exibição de status
                upload_output = gr.Textbox(
                    label="Status",
                    placeholder="Os resultados do processamento aparecerão aqui...",
                    interactive=False
                )
                
                # Conectar o botão à função de processamento
                upload_button.click(save_file, inputs=[files_input], outputs=[upload_output])
        
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
            
            **Nota:** Esta é a versão inicial do GesonelBot. Funcionalidades adicionais serão implementadas em breve.
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