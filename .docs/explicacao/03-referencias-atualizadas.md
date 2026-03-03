# 03 — Referencias Atualizadas: LangChain + pgVector + Python

> Pesquisa realizada em marco/2026.
> Versoes alvo: LangChain 0.3+, langchain-postgres 0.0.15+, Python 3.12

---

## 1. LangChain 0.3+ — Mudancas de API relevantes

### PyPDFLoader

**Import correto (sem mudanca):**
```python
from langchain_community.document_loaders import PyPDFLoader
```

**Dependencias:**
```bash
pip install langchain-community pypdf
```

**Uso atualizado (LangChain 0.3):**
```python
loader = PyPDFLoader(
    file_path="./document.pdf",
    mode="page",          # "page" = 1 Document por pagina (padrao)
                          # "single" = 1 Document com tudo
)
documents = loader.load()
```

**O que mudou:** O parametro `mode` foi adicionado para controlar se o PDF
vira um Document unico ou um por pagina. O import permanece em
`langchain_community`.

**Fonte:** [PyPDFLoader — LangChain Reference](https://reference.langchain.com/v0.3/python/community/document_loaders/langchain_community.document_loaders.pdf.PyPDFLoader.html)

---

### PGVector — BREAKING CHANGE IMPORTANTE

**Linha do tempo de deprecacao:**

```
langchain_community.vectorstores.PGVector    (DEPRECATED — nao usar)
        |
        v
langchain_postgres.PGVector                  (DEPRECATED desde v0.0.14)
        |
        v
langchain_postgres.PGVectorStore             (ATUAL — usar este)
```

**Versao mais recente:** langchain-postgres **0.0.17** (fevereiro 2026)

O nosso `requirements.txt` usa `langchain-postgres==0.0.15`. Nesta versao,
`PGVector` ja esta deprecado. Devemos usar `PGVectorStore`.

**Fonte:** [langchain-postgres GitHub](https://github.com/langchain-ai/langchain-postgres) |
[Issue #31824](https://github.com/langchain-ai/langchain/issues/31824)

---

## 2. langchain-postgres vs langchain-community PGVector

### Comparacao Direta

| Criterio | langchain-community PGVector | langchain-postgres PGVector | langchain-postgres PGVectorStore |
|---|---|---|---|
| **Status** | Deprecado | Deprecado (v0.0.14+) | **Ativo — recomendado** |
| **Driver** | psycopg2 | psycopg3 | psycopg3 |
| **Schema** | 2 tabelas (collection + embedding) | 2 tabelas | **1 tabela por collection** |
| **Metadata** | JSON blob | JSON blob | **Colunas dedicadas** |
| **Performance** | Base | Melhor | **Melhor (single table)** |
| **from_documents()** | Sim | Sim | Nao — usa `add_documents()` |

### Import Correto (ATUAL)

```python
# NAO USAR (deprecado):
# from langchain_community.vectorstores import PGVector
# from langchain_postgres import PGVector

# USAR ESTE:
from langchain_postgres import PGEngine, PGVectorStore
```

### Inicializacao Correta (PGVectorStore)

```python
from langchain_postgres import PGEngine, PGVectorStore
from langchain_openai import OpenAIEmbeddings

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"

# 1. Criar engine (pool de conexoes)
engine = PGEngine.from_connection_string(url=CONNECTION_STRING)

# 2. Criar tabela com schema vetorial
engine.init_vectorstore_table(
    table_name="documents",
    vector_size=1536,  # text-embedding-3-small = 1536 dimensoes
)

# 3. Instanciar vector store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

store = PGVectorStore.create_sync(
    engine=engine,
    table_name="documents",
    embedding_service=embeddings,
)

# 4. Adicionar documentos
store.add_documents(documents)  # lista de Document do LangChain
```

### Diferenca Chave: from_documents() nao existe mais

**Antes (PGVector deprecado):**
```python
# Criava a tabela E inseria docs em uma chamada
store = PGVector.from_documents(
    documents=docs,
    embedding=embeddings,
    connection_string=CONNECTION_STRING,
    collection_name="documents",
)
```

**Agora (PGVectorStore):**
```python
# Passo 1: criar engine e tabela
engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
engine.init_vectorstore_table(table_name="documents", vector_size=1536)

# Passo 2: criar store
store = PGVectorStore.create_sync(
    engine=engine,
    table_name="documents",
    embedding_service=embeddings,
)

# Passo 3: adicionar documentos (separado)
store.add_documents(docs)
```

### Connection String — Mudanca de Driver

```python
# ANTES (psycopg2):
"postgresql+psycopg2://langchain:langchain@localhost:5432/langchain"

# AGORA (psycopg3):
"postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
#                  ^ sem o "2"
```

**ATENCAO:** `psycopg` (sem numero) e o psycopg3. O `langchain-postgres`
NAO funciona com `psycopg2`. O nosso `requirements.txt` ja tem `psycopg`
instalado, entao estamos corretos.

### Impacto no Projeto

O nosso `requirements.txt` tem `langchain-postgres==0.0.15`. Nesta versao:
- `PGVector` ainda funciona mas emite DeprecationWarning
- `PGVectorStore` e o recomendado
- Para evitar retrabalho futuro, devemos implementar ja com `PGVectorStore`

**Fontes:**
- [Migration Guide: PGVector to PGVectorStore](https://github.com/langchain-ai/langchain-postgres/blob/main/examples/migrate_pgvector_to_pgvectorstore.md)
- [PGVectorStore DeepWiki](https://deepwiki.com/langchain-ai/langchain-postgres/3.1-pgvectorstore-(current-implementation))
- [PGVectorStore Integration Docs](https://docs.langchain.com/oss/python/integrations/vectorstores/pgvectorstore)

---

## 3. pgVector com Docker (pgvector/pgvector:pg17)

### docker-compose.yml (nosso projeto — ja correto)

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: langchain
      POSTGRES_PASSWORD: langchain
      POSTGRES_DB: langchain
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### O que a imagem pgvector/pgvector:pg17 inclui

- PostgreSQL 17 com extensao `pgvector` pre-instalada
- Suporte a vetores de ate 16.000 dimensoes
- Indices HNSW e IVFFlat para busca aproximada
- Metricas: cosseno, euclidiana, produto interno

### Extensao e criada automaticamente?

**NAO.** A extensao precisa ser habilitada no banco. Porem, o
`PGVectorStore` do LangChain faz isso automaticamente via
`engine.init_vectorstore_table()`. Se precisar fazer manualmente:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Boas Praticas de Configuracao

```yaml
# Pinning de versao (recomendado para reproducibilidade):
image: pgvector/pgvector:0.8.0-pg17   # versao especifica
# vs
image: pgvector/pgvector:pg17          # latest do pg17 (nosso caso — ok para dev)
```

```yaml
# Se porta 5432 estiver ocupada:
ports:
  - "5433:5432"   # expor em porta alternativa
```

**Fontes:**
- [pgvector Docker Hub](https://hub.docker.com/r/pgvector/pgvector)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Setup guide (DEV Community)](https://dev.to/yukaty/setting-up-postgresql-with-pgvector-using-docker-hcl)

---

## 4. similarity_search_with_score vs similarity_search

### Comparacao

| Metodo | Retorno | Score | Quando usar |
|---|---|---|---|
| `similarity_search(query, k=10)` | `list[Document]` | Nao | Quando so precisa dos documentos |
| `similarity_search_with_score(query, k=10)` | `list[tuple[Document, float]]` | Sim (0-1) | **Quando precisa filtrar por relevancia** |
| `similarity_search_with_relevance_scores(query, k=10)` | `list[tuple[Document, float]]` | Sim (0-1, normalizado) | Alternativa com scores normalizados |

### Como o Score e Calculado (PGVectorStore)

A distancia bruta e transformada em score de relevancia entre 0 e 1:

| Estrategia | Formula | Score 1.0 = | Score 0.0 = |
|---|---|---|---|
| **COSINE** (padrao) | `1 - distancia` | Identico | Oposto |
| EUCLIDEAN | `1 / (1 + distancia)` | Mesmo ponto | Muito distante |
| INNER_PRODUCT | `1 - distancia` | Maximo alinhamento | Nenhum |

### ATENCAO — Gotcha Historico

Em versoes anteriores do `langchain-community`, o `similarity_search_with_score`
retornava **distancia** (menor = melhor), NAO similaridade. Isso causava confusao
porque score 0.1 era melhor que 0.9.

No `PGVectorStore` atual, os scores sao **normalizados para 0-1** onde
**maior = mais similar**. Comportamento correto.

### Recomendacao para o Projeto

```python
# USAR similarity_search_with_score para poder filtrar por qualidade
results = store.similarity_search_with_score(query, k=10)

# Filtrar chunks com baixa relevancia (opcional mas recomendado)
THRESHOLD = 0.3
filtered = [(doc, score) for doc, score in results if score >= THRESHOLD]
```

**Por que com score e nao sem:**
- Permite descartar chunks irrelevantes antes de montar o contexto
- Permite logging/debugging da qualidade da busca
- Permite ajustar k e threshold baseado em metricas reais

**Fontes:**
- [PGVector Scores Issue #13437](https://github.com/langchain-ai/langchain/issues/13437)
- [PGVectorStore Search API](https://deepwiki.com/langchain-ai/langchain-postgres/3.1-pgvectorstore-(current-implementation))

---

## 5. Boas Praticas para Prompt Grounding (Anti-alucinacao)

### Estrategias Aplicadas no Nosso Prompt

O `PROMPT_TEMPLATE` em `src/search.py` ja aplica varias boas praticas:

```
CONTEXTO:
{contexto}                          <-- (1) Contexto ANTES da pergunta

REGRAS:
- Responda somente com base no CONTEXTO.     <-- (2) Instrucao explicita
- Se a informacao nao estiver...
  "Nao tenho informacoes..."                  <-- (3) Fallback definido
- Nunca invente ou use conhecimento externo.  <-- (4) Restricao de fonte
- Nunca produza opinioes...                   <-- (5) Restricao de interpretacao

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:       <-- (6) Few-shot negativo
Pergunta: "Qual e a capital da Franca?"
Resposta: "Nao tenho informacoes..."
```

### Checklist de Grounding (melhores praticas 2025)

| Tecnica | Status no Projeto | Descricao |
|---|---|---|
| Contexto antes da pergunta | Aplicado | LLM processa contexto primeiro, reduz vies |
| Instrucao explicita de fonte | Aplicado | "Responda somente com base no CONTEXTO" |
| Fallback padrao definido | Aplicado | Frase exata para quando nao sabe |
| Few-shot negativo | Aplicado | Exemplos de perguntas fora do escopo |
| Temperature = 0 | Planejado (Fase 3) | Elimina variabilidade, maximiza fidelidade |
| Restricao de opiniao | Aplicado | "Nunca produza opinioes" |
| Citacao de fonte | Nao aplicado | Pedir ao LLM para citar pagina/secao |
| Score threshold | Nao aplicado | Filtrar chunks irrelevantes antes do prompt |

### Tecnicas Adicionais Recomendadas (para evolucao futura)

**1. Citacao de fonte no prompt:**
```
REGRAS ADICIONAIS:
- Sempre cite a pagina de onde veio a informacao.
  Exemplo: "Segundo a pagina 12, microsservicos sao..."
```

**2. Chain-of-thought com verificacao:**
```
Antes de responder, verifique:
1. A informacao esta EXPLICITAMENTE no contexto?
2. Voce esta parafraseando ou inventando?
Se inventando, responda com a frase padrao.
```

**3. Score threshold no retrieval:**
```python
# Descartar chunks com score < 0.3 ANTES de montar o prompt
results = store.similarity_search_with_score(query, k=10)
filtered = [(doc, score) for doc, score in results if score >= 0.3]
if not filtered:
    return "Nao tenho informacoes necessarias para responder sua pergunta."
```

### O que Pesquisas de 2025 Dizem

- Stanford (2025): mesmo pipelines RAG bem curados podem fabricar citacoes.
  Temperature=0 e few-shot negativo sao mitigacoes essenciais.
- MetaQA (ACM 2025): mutacoes de prompt podem detectar tendencia a alucinacao
  em modelos fechados.
- NAACL 2025: treinamento com exemplos sinteticos de "dificil alucinar" reduziu
  alucinacoes em 90-96% sem perder qualidade.

**Fontes:**
- [Mitigating Hallucinations in RAG — 2025 Review (OpenAI Community)](https://community.openai.com/t/mitigating-hallucinations-in-rag-a-2025-review/1362063)
- [How to Prevent LLM Hallucinations (Promptfoo)](https://www.promptfoo.dev/docs/guides/prevent-llm-hallucinations/)
- [LLM Hallucinations Guide (Lakera)](https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models)
- [Best Practices — Microsoft](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/best-practices-for-mitigating-hallucinations-in-large-language-models-llms/4403129)

---

## 6. text-embedding-3-small vs text-embedding-ada-002

### Comparacao Completa

| Criterio | text-embedding-ada-002 | text-embedding-3-small | text-embedding-3-large |
|---|---|---|---|
| **Geracao** | 2a geracao (2022) | **3a geracao (2024)** | 3a geracao (2024) |
| **Dimensoes** | 1536 (fixo) | 1536 (reduzivel) | 3072 (reduzivel) |
| **MTEB Score** | 61.0% | **62.3%** | 64.6% |
| **MIRACL (multilingual)** | 31.4% | **44.0%** | 54.9% |
| **Custo (por 1M tokens)** | $0.10 | **$0.02** | $0.13 |
| **Paginas por dolar** | ~12.500 | **~62.500** | ~9.615 |
| **Max input** | 8.192 tokens | 8.192 tokens | 8.192 tokens |
| **Dimensoes reduziveis** | Nao | **Sim (ate 256)** | Sim (ate 256) |
| **Status** | Legacy (nao deprecado) | **Recomendado** | Premium |

### Por que text-embedding-3-small e a escolha correta

1. **5x mais barato** que ada-002 com qualidade superior
2. **+40% melhor em multilingual** (MIRACL: 31.4% vs 44.0%) — relevante
   porque nosso PDF e em portugues
3. **Dimensoes reduziveis**: se precisar economizar storage, pode reduzir de
   1536 para 512 ou 256 sem retreinar
4. **ada-002 nao esta deprecado**, mas a OpenAI recomenda os modelos v3
   para novos projetos

### Dimensoes Reduziveis — Feature Exclusiva da v3

```python
# Padrao: 1536 dimensoes
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Reduzido: 512 dimensoes (menor storage, busca mais rapida)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,
)

# Dado importante: text-embedding-3-large com 256 dimensoes
# AINDA supera ada-002 com 1536 dimensoes no MTEB
```

### Recomendacao Final

```
Para o nosso projeto:
  Modelo: text-embedding-3-small
  Dimensoes: 1536 (padrao — nao ha necessidade de reduzir)
  Custo estimado para 34 paginas: < $0.001

Para projetos futuros de alta escala:
  Considerar text-embedding-3-small com dimensions=512
  (70% menos storage com perda minima de qualidade)
```

**Fontes:**
- [New Embedding Models — OpenAI Blog](https://openai.com/index/new-embedding-models-and-api-updates/)
- [Embeddings Guide — OpenAI API](https://developers.openai.com/api/docs/guides/embeddings/)
- [Performance Analysis — PingCAP](https://www.pingcap.com/article/analyzing-performance-gains-in-openais-text-embedding-3-small/)
- [Model Comparison — Helicone](https://www.helicone.ai/comparison/text-embedding-3-small-on-openai-vs-text-embedding-ada-002-v2-on-openai)

---

## Resumo de Impacto no Projeto

### O que PRECISA mudar no codigo

| Arquivo | Mudanca | Prioridade |
|---|---|---|
| `src/ingest.py` | Usar `PGVectorStore` em vez de `PGVector.from_documents()` | **Alta** |
| `src/ingest.py` | Connection string com `psycopg` (nao `psycopg2`) | **Alta** |
| `src/search.py` | Usar `similarity_search_with_score` com threshold | Media |
| `requirements.txt` | Considerar atualizar para `langchain-postgres>=0.0.17` | Baixa |

### O que ja esta correto

| Item | Status |
|---|---|
| PyPDFLoader import path | OK — `langchain_community` |
| docker-compose.yml (pgvector:pg17) | OK |
| Prompt template com grounding | OK — boas praticas aplicadas |
| text-embedding-3-small como escolha | OK — melhor custo-beneficio |
| psycopg (v3) no requirements.txt | OK |

### Codigo de Referencia Atualizado para Ingestao

```python
# src/ingest.py — esqueleto atualizado
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"

def ingest_pdf():
    # 1. Carregar PDF
    loader = PyPDFLoader(file_path=PDF_PATH)
    documents = loader.load()

    # 2. Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)

    # 3. Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 4. Armazenar no PostgreSQL (API nova — PGVectorStore)
    engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
    engine.init_vectorstore_table(
        table_name="documents",
        vector_size=1536,
    )
    store = PGVectorStore.create_sync(
        engine=engine,
        table_name="documents",
        embedding_service=embeddings,
    )
    store.add_documents(chunks)

    print(f"Ingeridos {len(chunks)} chunks de {PDF_PATH}")

if __name__ == "__main__":
    ingest_pdf()
```
