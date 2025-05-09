"""
Módulo de processamento e ingestão de documentos

Este módulo é responsável por processar os documentos carregados pelos usuários,
extrair seu conteúdo e preparar os dados para indexação.
"""
import os
from typing import List, Dict, Optional

# Configurações
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_docs")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")

def extract_text_from_txt(file_path: str) -> str:
    """
    Extrai texto de um arquivo TXT.
    
    Args:
        file_path: Caminho para o arquivo TXT
        
    Returns:
        Texto extraído do arquivo
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Tentar com codificação alternativa se UTF-8 falhar
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

def extract_text_from_docx(file_path: str) -> str:
    """
    Extrai texto de um arquivo DOCX. (Stub - será implementado na próxima fase)
    
    Args:
        file_path: Caminho para o arquivo DOCX
        
    Returns:
        Texto extraído do arquivo ou mensagem de erro
    """
    # Placeholder - será implementado com python-docx
    return f"[Texto simulado de {os.path.basename(file_path)}] A extração real será implementada na próxima fase."

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrai texto de um arquivo PDF. (Stub - será implementado na próxima fase)
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Texto extraído do arquivo ou mensagem de erro
    """
    # Placeholder - será implementado com PyPDF
    return f"[Texto simulado de {os.path.basename(file_path)}] A extração real será implementada na próxima fase."

def process_document(file_path: str) -> Dict[str, str]:
    """
    Processa um único documento e extrai seu texto.
    
    Args:
        file_path: Caminho para o arquivo a ser processado
        
    Returns:
        Dicionário com informações sobre o documento processado
    """
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "file_name": os.path.basename(file_path),
            "message": f"Arquivo não encontrado: {file_path}",
            "text": ""
        }
    
    # Determinar o tipo de arquivo
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    
    # Extrair texto com base no tipo de arquivo
    try:
        if file_extension == '.txt':
            text = extract_text_from_txt(file_path)
        elif file_extension == '.docx':
            text = extract_text_from_docx(file_path)
        elif file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        else:
            return {
                "status": "error",
                "file_name": file_name,
                "message": f"Formato não suportado: {file_extension}",
                "text": ""
            }
            
        # Retornar documento processado com sucesso
        return {
            "status": "success",
            "file_name": file_name,
            "message": "Documento processado com sucesso",
            "text": text
        }
        
    except Exception as e:
        # Retornar erro em caso de falha
        return {
            "status": "error",
            "file_name": file_name,
            "message": f"Erro ao processar documento: {str(e)}",
            "text": ""
        }

def process_documents(file_paths: List[str]) -> Dict[str, object]:
    """
    Processa uma lista de documentos e prepara para indexação.
    
    Args:
        file_paths: Lista de caminhos para os arquivos a serem processados
        
    Returns:
        Dicionário com informações sobre o processamento
    """
    results = {
        "success_count": 0,
        "error_count": 0,
        "processed_files": [],
        "errors": []
    }
    
    # Processar cada arquivo
    for file_path in file_paths:
        result = process_document(file_path)
        
        # Registrar resultado
        if result["status"] == "success":
            results["success_count"] += 1
            results["processed_files"].append({
                "file_name": result["file_name"],
                "char_count": len(result["text"])
            })
        else:
            results["error_count"] += 1
            results["errors"].append({
                "file_name": result["file_name"],
                "message": result["message"]
            })
    
    return results

def get_processed_documents_info() -> List[Dict[str, str]]:
    """
    Obtém informações sobre os documentos já processados.
    
    Returns:
        Lista de dicionários com informações sobre os documentos
    """
    documents = []
    
    # Listar arquivos no diretório de uploads
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # Obter informações básicas do arquivo
                file_size = os.path.getsize(file_path)
                file_extension = os.path.splitext(filename)[1].lower()
                
                documents.append({
                    "file_name": filename,
                    "file_size": file_size,
                    "file_type": file_extension,
                    "file_path": file_path
                })
    
    return documents

# Função principal que será chamada pelo app.py
def ingest_documents(file_paths: Optional[List[str]] = None) -> Dict[str, object]:
    """
    Função principal que inicia o processo de ingestão de documentos.
    
    Args:
        file_paths: Lista opcional de caminhos para arquivos. Se None, processa todos os arquivos
                   no diretório de uploads.
        
    Returns:
        Resultado do processamento
    """
    # Se nenhuma lista específica for fornecida, processar todos os arquivos no diretório
    if file_paths is None:
        all_documents = get_processed_documents_info()
        file_paths = [doc["file_path"] for doc in all_documents]
    
    # Processar documentos
    results = process_documents(file_paths)
    
    # Adicionar resumo ao resultado
    results["summary"] = f"Processados {results['success_count']} documentos com sucesso, {results['error_count']} erros."
    
    return results 