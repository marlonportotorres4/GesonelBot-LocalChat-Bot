# GesonelBot - Seu chat bot local 🤖

Um chatbot com IA para responder perguntas com base em documentos locais, sem necessidade de conexão constante com a internet para o funcionamento principal.

## Visão Geral 📝

Este projeto tem como objetivo criar um chatbot simples que permite:
- Upload de documentos (PDF, DOCX, TXT)
- Processamento de documentos localmente
- Fazer perguntas sobre o conteúdo desses documentos
- Receber respostas geradas por IA com base no conteúdo

## Tecnologias Utilizadas 🧩

- **LangChain:** Framework para orquestração do fluxo de QA
- **ChromaDB:** Banco de dados vetorial local
- **Gradio:** Interface web simples
- **Python-docx/PyPDF:** Processamento de documentos

## Estrutura do Projeto 📁

```
./
├── gesonelbot/           # Pacote principal
│   ├── __init__.py       # Inicialização do pacote
│   ├── core/             # Funcionalidades centrais
│   │   ├── __init__.py
│   │   ├── document_processor.py  # Processamento de documentos
│   │   └── qa_engine.py         # Motor de perguntas e respostas
│   ├── data/             # Gerenciamento de dados
│   │   ├── __init__.py
│   │   ├── uploaded_docs/  # Documentos carregados
│   │   └── vectorstore/    # Banco de dados vetorial
│   ├── utils/            # Utilitários
│   │   └── __init__.py
│   ├── config/           # Configurações
│   │   ├── __init__.py
│   │   └── settings.py   # Configurações centralizadas
│   ├── api/              # APIs (para futuras extensões)
│   │   └── __init__.py
│   └── ui/               # Interface do usuário
│       ├── __init__.py
│       └── app.py        # Interface Gradio
├── scripts/              # Scripts utilitários
│   ├── setup.bat         # Script de instalação
│   └── executar.bat      # Script para execução rápida
├── tests/                # Testes automatizados
├── docs/                 # Documentação
├── models/               # Modelos locais (quando aplicável)
├── gesonelbot.py         # Ponto de entrada principal
├── requirements.txt      # Dependências
├── env.example           # Modelo para arquivo .env
├── LICENSE               # Licenciamento do projeto
└── README.md             # Este arquivo
```

## Instalação 🛠️

### Requisitos
- Python 3.8 ou superior
- Windows, Linux ou macOS

### Passos para instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seuusuario/GesonelBot-LocalChat-Bot.git
   cd GesonelBot-LocalChat-Bot
   ```

2. Execute o script de instalação:
   - No Windows: `scripts\setup.bat`
   - No Linux/macOS: `bash scripts/setup.sh`


> **Nota:** Os diretórios para armazenamento de documentos (`uploaded_docs`) e banco de dados vetorial (`vectorstore`) são criados automaticamente na primeira execução. Você não precisa criá-los manualmente.

## Execução 🚀

- No Windows: Execute o arquivo `scripts\executar.bat`
- No Linux/macOS: Execute `python gesonelbot.py`

## Uso 📋

1. **Upload de Documentos**:
   - Na primeira aba, faça upload de arquivos PDF, DOCX ou TXT
   - Clique no botão "Processar Documentos"
   - Aguarde o processamento

2. **Fazer Perguntas**:
   - Vá para a segunda aba
   - Digite sua pergunta sobre o conteúdo dos documentos
   - Clique em "Perguntar"
   - Receba a resposta

## Status do Projeto ⏱️

🚧 **Em desenvolvimento** 🚧

Este projeto está em desenvolvimento ativo. Novas funcionalidades serão adicionadas regularmente.

## Próximos Passos 🛣️

- Implementação completa do banco de dados vetorial
- Adição de suporte para modelos locais
- Aprimoramento do motor de QA
- Interface de usuário melhorada

---

Desenvolvido como projeto pessoal para estudos de IA e processamento de linguagem natural.
