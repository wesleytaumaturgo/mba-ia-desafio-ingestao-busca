# Ingestão e Busca Semântica com LangChain e Postgres

Pipeline RAG que ingere um PDF, armazena embeddings no PostgreSQL com pgVector
e responde perguntas com base exclusiva no conteúdo do documento.

## Tecnologias

- Python 3.9+
- LangChain + langchain-postgres (PGVector)
- PostgreSQL 17 + pgVector
- Google Gemini (`gemini-embedding-001` + `gemini-2.5-flash-lite`)
- OpenAI (`text-embedding-3-small` + `gpt-4o-mini`) — alternativa
- Docker

## Pré-requisitos

- Docker instalado e rodando
- Python 3.9+
- Chave de API do Google Gemini **ou** OpenAI

## Configuração

### 1. Variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha obrigatoriamente:

```env
GOOGLE_API_KEY=sua_chave_aqui          # para usar Gemini (padrão)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PDF_PATH=/caminho/absoluto/para/document.pdf
```

> Para usar OpenAI em vez de Gemini, defina `EMBEDDING_PROVIDER=openai` e `OPENAI_API_KEY=sua_chave`.

### 2. Dependências

```bash
pip install -r requirements.txt
```

### 3. Banco de dados

```bash
docker run -d \
  --name postgres_rag \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=rag \
  -p 5432:5432 \
  pgvector/pgvector:pg17
```

Aguarde o banco subir e habilite a extensão:

```bash
docker exec postgres_rag psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

> Se preferir usar `docker compose up -d`, o `docker-compose.yml` já inclui o bootstrap da extensão.

## Execução

```bash
# 1. Ingestão do PDF (chunk_size=1000, chunk_overlap=150)
PYTHONPATH=. python src/ingest.py

# 2. Chat interativo
PYTHONPATH=. python src/chat.py
```

## Exemplo de uso

```
Chat RAG iniciado. Digite 'sair' para encerrar.

Pergunta: Qual empresa tem o maior faturamento?
Resposta: Tríade Dados LTDA R$ 3.037.258.594,22 1961

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
    ├── ingest.py   # carrega PDF, chunka e salva embeddings no pgVector
    ├── search.py   # busca semântica com score e formatação do prompt
    └── chat.py     # loop de chat RAG interativo
```

## Parâmetros do desafio

| Parâmetro | Valor |
|---|---|
| `chunk_size` | 1000 |
| `chunk_overlap` | 150 |
| `k` (similarity search) | 10 |
| Embedding (Gemini) | `gemini-embedding-001` |
| LLM | `gemini-2.5-flash-lite` |
