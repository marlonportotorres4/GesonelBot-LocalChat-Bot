"""
Processamento de documentos do GesonelBot

Este módulo é responsável por processar os documentos carregados pelos usuários,
extrair seu conteúdo e preparar os dados para indexação.
"""
import os
import mimetypes
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from gesonelbot.config.settings import UPLOAD_DIR, VECTORSTORE_DIR

# Configurar tipos MIME suportados
SUPPORTED_MIME_TYPES = {
    'text/plain': '.txt',
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
}

# Importações para processamento de documentos
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pypdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

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
    Extrai texto de um arquivo DOCX.
    
    Args:
        file_path: Caminho para o arquivo DOCX
        
    Returns:
        Texto extraído do arquivo ou mensagem de erro
    """
    if not DOCX_AVAILABLE:
        return f"[Biblioteca python-docx não instalada] Não foi possível extrair o texto de {os.path.basename(file_path)}"
    
    try:
        # Carregar o documento
        doc = docx.Document(file_path)
        
        # Extrair texto de todos os parágrafos
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
            
        # Extrair texto de tabelas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
        
        # Juntar todo o texto com quebras de linha
        return '\n'.join(full_text)
    except Exception as e:
        return f"[Erro ao processar DOCX: {str(e)}] Não foi possível extrair o texto de {os.path.basename(file_path)}"

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrai texto de um arquivo PDF.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Texto extraído do arquivo ou mensagem de erro
    """
    if not PDF_AVAILABLE:
        return f"[Biblioteca pypdf não instalada] Não foi possível extrair o texto de {os.path.basename(file_path)}"
    
    try:
        text = []
        # Abrir o PDF
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            
            # Extrair texto de cada página
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text.append(page.extract_text())
        
        # Juntar todo o texto com quebras de linha
        return '\n'.join(text)
    except Exception as e:
        return f"[Erro ao processar PDF: {str(e)}] Não foi possível extrair o texto de {os.path.basename(file_path)}"

def validate_file(file_path: str) -> Tuple[bool, str]:
    """
    Valida se o arquivo é suportado e está em bom estado.
    
    Args:
        file_path: Caminho para o arquivo
        
    Returns:
        Tupla (é_válido, mensagem)
    """
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        return False, "Arquivo não encontrado"
    
    # Verificar se é um arquivo
    if not os.path.isfile(file_path):
        return False, "O caminho especificado não é um arquivo"
    
    # Verificar tamanho do arquivo (máximo 20MB)
    if os.path.getsize(file_path) > 20 * 1024 * 1024:
        return False, "Arquivo muito grande (máximo 20MB)"
    
    # Verificar tipo MIME
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type not in SUPPORTED_MIME_TYPES:
        return False, f"Tipo de arquivo não suportado: {mime_type}"
    
    return True, "Arquivo válido"

def get_file_metadata(file_path: str) ->  Dict[str, str]:
    """
    Obtém metadados do arquivo.
    
    Args:
        file_path: Caminho para o arquivo
        
    Returns:
        Dicionário com metadados do arquivo
    """
    file_stat = os.stat(file_path)
    
    # Calcular hash do arquivo
    file_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_hash.update(chunk)
    
    return {
        "file_name": os.path.basename(file_path),
        "file_size": str(file_stat.st_size),
        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        "file_hash": file_hash.hexdigest(),
        "mime_type": mimetypes.guess_type(file_path)[0]
    }

def process_document(file_path: str) -> Dict[str, str]:
    """
    Processa um único documento e extrai seu texto.
    
    Args:
        file_path: Caminho para o arquivo a ser processado
        
    Returns:
        Dicionário com informações sobre o documento processado
    """
    # Validar arquivo
    is_valid, message = validate_file(file_path)
    if not is_valid:
        return {
            "status": "error",
            "file_name": os.path.basename(file_path),
            "message": message,
            "text": ""
        }
    
    # Obter metadados
    metadata = get_file_metadata(file_path)
    
    # Determinar o tipo de arquivo
    file_extension = os.path.splitext(file_path)[1].lower()
    
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
                "file_name": metadata["file_name"],
                "message": f"Formato não suportado: {file_extension}",
                "text": ""
            }
            
        # Retornar documento processado com sucesso
        return {
            "status": "success",
            "file_name": metadata["file_name"],
            "message": "Documento processado com sucesso",
            "text": text,
            "metadata": metadata
        }
        
    except Exception as e:
        # Retornar erro em caso de falha
        return {
            "status": "error",
            "file_name": metadata["file_name"],
            "message": f"Erro ao processar documento: {str(e)}",
            "text": "",
            "metadata": metadata
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
        print(f"Buscando documentos em: {UPLOAD_DIR}")
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # Obter informações básicas do arquivo
                file_size = os.path.getsize(file_path)
                file_extension = os.path.splitext(filename)[1].lower()
                
                print(f"Documento encontrado: {filename}, Tamanho: {file_size/1024/1024:.2f}MB")
                
                documents.append({
                    "file_name": filename,
                    "file_size": file_size,
                    "file_type": file_extension,
                    "file_path": file_path
                })
    else:
        print(f"Diretório de upload não existe: {UPLOAD_DIR}")
        
    print(f"Total de documentos encontrados: {len(documents)}")
    return documents

# Função para calcular o uso total da pasta uploaded_docs
def get_total_upload_usage() -> int:
    """
    Retorna o uso total em bytes da pasta de uploads.
    """
    total = 0
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                total += os.path.getsize(file_path)
    return total

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
    # Verificar diretório de upload
    if not os.path.exists(UPLOAD_DIR):
        print(f"Criando diretório de upload: {UPLOAD_DIR}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
    # Se nenhuma lista específica for fornecida, processar todos os arquivos no diretório
    if file_paths is None:
        print("Nenhum caminho específico fornecido, processando todos os documentos...")
        all_documents = get_processed_documents_info()
        file_paths = [doc["file_path"] for doc in all_documents]
    else:
        print(f"Processando {len(file_paths)} documentos específicos")
        for path in file_paths:
            print(f" - {os.path.basename(path)}: {os.path.getsize(path)/1024/1024:.2f}MB")
    
    # Processar documentos
    results = process_documents(file_paths)
    
    # Verificar o estado final
    docs_after = get_processed_documents_info()
    
    # Adicionar resumo ao resultado
    results["summary"] = f"Processados {results['success_count']} documentos com sucesso, {results['error_count']} erros."
    results["total_docs"] = len(docs_after)
    results["total_size"] = sum(doc["file_size"] for doc in docs_after)
    
    return results 