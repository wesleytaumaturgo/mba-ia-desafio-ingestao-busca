# Ingestão e Busca Semântica com LangChain e Postgres

Pipeline RAG que ingere um PDF, armazena embeddings no PostgreSQL com pgVector
e responde perguntas com base exclusiva no conteúdo do documento.

## Tecnologias

- Python 3.9+
- LangChain
- PostgreSQL + pgVector
- Google Gemini (gemini-2.5-flash-lite + gemini-embedding-001)
- Docker & Docker Compose

## Pré-requisitos

- Docker instalado
- Python 3.9+
- Chave de API do Google Gemini

## Configuração

```bash
cp .env.example .env
```

Preencha as variáveis no `.env`:

```
GOOGLE_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documents
PDF_PATH=/caminho/para/document.pdf
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Ordem de execução

```bash
# 1. Subir o banco
docker compose up -d

# 2. Ingestão do PDF
python src/ingest.py

# 3. Chat interativo
python src/chat.py
```

## Exemplo de uso

```
Chat RAG iniciado. Digite 'sair' para encerrar.

Pergunta: Qual empresa tem o maior faturamento?
Resposta: Solar IA Serviços R$ 3.790.111.387,30 1980

Pergunta: Qual é a capital da França?
Resposta: Não tenho informações necessárias para responder sua pergunta.

Pergunta: sair
Chat encerrado.
```

## Estrutura do projeto

```
.
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── document.pdf
└── src/
    ├── ingest.py   # carrega PDF, chuna e salva embeddings no pgVector
    ├── search.py   # busca semântica e formatação do prompt
    └── chat.py     # loop de chat RAG
```
