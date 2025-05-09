"""
GesonelBot - Aplicativo para responder perguntas com base em documentos locais

Este módulo implementa a interface do usuário usando Gradio, permitindo
o upload de documentos e a interação com perguntas e respostas.
"""
import os
import gradio as gr
from ingestion import ingest_documents

# Configurações de pastas
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_docs")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")

# Configurações do aplicativo
MAX_FILE_SIZE_MB = 20  # Tamanho máximo de arquivo em MB
MAX_FILES = 10          # Número máximo de arquivos permitidos

# Garantir que as pastas existam
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

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
    if len(files) > MAX_FILES:
        return f"⚠️ Número máximo de arquivos excedido. Limite: {MAX_FILES} arquivos."
    
    # Informações de debug
    print(f"Recebido {len(files)} arquivo(s) para processamento")
    for i, file in enumerate(files):
        print(f"Arquivo {i+1}: Tipo = {type(file).__name__}")
    
    # Lista para armazenar caminhos dos arquivos salvos
    file_paths = []
    
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
                
                # Verificar tamanho do arquivo
                if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                    return f"⚠️ Arquivo {file_name} excede o limite de {MAX_FILE_SIZE_MB}MB"
                
                with open(file_path, 'wb') as dest_file:
                    dest_file.write(content)
                    
            elif isinstance(file, str) and os.path.exists(file):
                # Para caminhos de arquivos (comum no Gradio)
                # Verificar tamanho do arquivo
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
        message = f"✅ {len(files)} arquivo(s) salvo(s) e processado(s) com sucesso!\n\n"
        message += f"📊 {results['success_count']} processados, {results['error_count']} erros.\n"
        
        # Adicionar detalhes se houver erros
        if results['error_count'] > 0:
            message += "\nErros encontrados:\n"
            for error in results['errors']:
                message += f"- {error['file_name']}: {error['message']}\n"
                
        return message
    except Exception as e:
        # Arquivo foi salvo mas houve erro no processamento
        return f"✅ {len(files)} arquivo(s) salvo(s), mas houve erro no processamento: {str(e)}"

def answer_question(question):
    """
    Função temporária para responder perguntas (será substituída pela implementação real).
    
    Parâmetros:
        question (str): A pergunta do usuário
        
    Retorna:
        str: Uma resposta simulada
    """
    if not question:
        return "Por favor, faça uma pergunta."
    
    # Resposta temporária
    return f"Sua pergunta foi: '{question}'\n\nA funcionalidade de resposta inteligente será implementada em breve."

# Interface principal do Gradio
with gr.Blocks(title="GesonelBot - Seu chat bot local") as demo:
    # Cabeçalho
    gr.Markdown("# 📚 GesonelBot")
    gr.Markdown("### Faça upload de documentos e pergunte sobre eles")
    
    # Aba de Upload de Documentos
    with gr.Tab("Upload de Documentos"):
        with gr.Column():
            # Componente para upload de arquivos
            files_input = gr.File(
                file_count="multiple",  # Permitir múltiplos arquivos
                label="Carregar documentos (PDF, DOCX, TXT)",
                file_types=["pdf", "docx", "txt", ".pdf", ".docx", ".txt"]  # Tentar diferentes formatos de especificação
            )
            
            # Explicação sobre formatos suportados
            gr.Markdown("""
            **Formatos suportados:**
            - PDF (`.pdf`) - Documentos, artigos, manuais
            - Word (`.docx`) - Documentos do Microsoft Word
            - Texto (`.txt`) - Arquivos de texto simples
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
    
    # Aba de Perguntas e Respostas
    with gr.Tab("Fazer Perguntas"):
        with gr.Column():
            # Campo para inserir pergunta
            question_input = gr.Textbox(
                label="Sua pergunta sobre os documentos",
                placeholder="Ex: O que é mencionado sobre..."
            )
            
            # Botão para enviar pergunta
            answer_button = gr.Button("Perguntar", variant="primary")
            
            # Área para exibir resposta
            answer_output = gr.Textbox(
                label="Resposta",
                placeholder="A resposta aparecerá aqui..."
            )
            
            # Conectar botão à função de resposta
            answer_button.click(answer_question, inputs=[question_input], outputs=[answer_output])
    
    # Explicação sobre como funciona
    with gr.Accordion("Como usar o GesonelBot", open=False):
        gr.Markdown("""
        ### Instruções de uso:
        
        1. **Upload de Documentos**:
           - Na primeira aba, faça upload de arquivos PDF, DOCX ou TXT
           - Clique no botão "Processar Documentos"
           - Aguarde o processamento (isto pode levar alguns segundos)
        
        2. **Fazer Perguntas**:
           - Vá para a segunda aba
           - Digite sua pergunta sobre o conteúdo dos documentos
           - Clique em "Perguntar"
           - O sistema buscará informações relevantes e responderá
        
        **Nota:** Esta é a versão inicial do GesonelBot. Funcionalidades adicionais serão implementadas em breve.
        """)

# Iniciar a aplicação quando o script é executado diretamente
if __name__ == "__main__":
    demo.launch(share=False) 