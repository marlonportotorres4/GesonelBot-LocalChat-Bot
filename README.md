# GesonelBot - Seu chat bot local 🤖

Um chatbot com IA para responder perguntas com base em documentos locais, sem necessidade de conexão constante com a internet para o funcionamento principal.

## Visão Geral 📝

Este projeto tem como objetivo criar um chatbot simples que permite:
- Upload de documentos (PDF, DOCX, TXT)
- Processamento de documentos localmente
- Fazer perguntas sobre o conteúdo desses documentos
- Receber respostas geradas por IA com base no conteúdo

## Tecnologias Planejadas 🧩

- **LangChain:** Framework para orquestração do fluxo de QA
- **ChromaDB:** Banco de dados vetorial local
- **Embeddings:** OpenAI ou modelo local via Hugging Face
- **Gradio:** Interface web simples

## Estrutura de Pastas Planejada 📁

```
./
├── app.py                # Código principal com interface
├── qa_engine.py          # Motor de perguntas e respostas
├── ingestion.py          # Processamento de documentos
├── uploaded_docs/        # Armazenamento de documentos
├── vectorstore/          # Banco vetorial local
└── requirements.txt      # Dependências
```

## Status do Projeto ⏱️

🚧 **Em desenvolvimento** 🚧

Este projeto está em estágio inicial de desenvolvimento. Atualizações serão feitas incrementalmente.

## Próximos Passos 🛣️

1. Configurar ambiente básico e dependências
2. Implementar interface inicial com Gradio
3. Desenvolver processamento de documentos
4. Implementar armazenamento vetorial
5. Criar motor de QA
6. Integrar todos os componentes

---

Desenvolvido como projeto pessoal para estudos de IA e processamento de linguagem natural.