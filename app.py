import os
import gradio as gr

# Configurações de pastas
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_docs")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")

# Garantir que as pastas existam
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Funções mockadas para serem implementadas posteriormente
def save_file(files):
    """Função placeholder para salvar arquivos"""
    return "Funcionalidade de upload será implementada em breve."

def answer_question(question):
    """Função placeholder para responder perguntas"""
    return "Funcionalidade de resposta será implementada em breve."

# Interface Gradio básica
with gr.Blocks(title="GesonelBot - Seu chat bot local") as demo:
    gr.Markdown("# 📚 GesonelBot")
    gr.Markdown("### Faça upload de documentos e pergunte sobre eles")
    
    with gr.Tab("Upload de Documentos"):
        with gr.Column():
            files_input = gr.File(
                file_count="multiple",
                label="Carregar documentos (PDF, DOCX, TXT)"
            )
            upload_button = gr.Button("Processar Documentos")
            upload_output = gr.Textbox(label="Status")
            upload_button.click(save_file, inputs=[files_input], outputs=[upload_output])
    
    with gr.Tab("Fazer Perguntas"):
        with gr.Column():
            question_input = gr.Textbox(
                label="Sua pergunta sobre os documentos",
                placeholder="Ex: O que é mencionado sobre..."
            )
            answer_button = gr.Button("Perguntar")
            answer_output = gr.Textbox(label="Resposta")
            answer_button.click(answer_question, inputs=[question_input], outputs=[answer_output])

if __name__ == "__main__":
    demo.launch(share=False) 