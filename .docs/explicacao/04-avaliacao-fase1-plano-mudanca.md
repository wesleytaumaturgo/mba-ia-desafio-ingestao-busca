# 04 — Avaliacao da Fase 1 + Plano de Mudanca

> Auditoria dos entregaveis da Fase 1 (Descoberta) contra o playbook.md
> Data: marco/2026

---

## Checklist do Gate — Fase 1

O playbook define 4 entregaveis no gate da Fase 1 (linhas 423-428):

### 1. Explicar o pipeline RAG em 3 frases sem consultar docs

| Status | Entregavel |
|---|---|
| FEITO | Relatorio `01-pipeline-rag.md` cobre os 8 passos do pipeline completo |

**Evidencia:** O documento explica ingestao (PyPDFLoader -> chunking -> embedding -> pgVector)
e busca (query embedding -> similarity search -> prompt template -> LLM) com diagramas e
justificativas para cada decisao.

**Teste do gate (3 frases):**
1. O PDF e carregado, dividido em chunks de 1000 chars e cada chunk e convertido em um vetor
   de 1536 dimensoes pelo text-embedding-3-small, armazenado no PostgreSQL com pgVector.
2. Quando o usuario faz uma pergunta, ela e convertida no mesmo tipo de vetor e os 10 chunks
   mais proximos por similaridade cosseno sao recuperados do banco.
3. Os chunks sao injetados como contexto num prompt com regras de grounding, e o gpt-5-nano
   (temperature=0) gera uma resposta baseada APENAS nesse contexto.

**Veredicto:** APROVADO

---

### 2. Decisoes de chunking documentadas

| Status | Entregavel |
|---|---|
| FEITO | Relatorio `02-decisoes-chunking.md` documenta todos os parametros |

**Cobertura verificada:**
- chunk_size=1000: justificado com tabela comparativa (300/500/1000/1500/2000)
- chunk_overlap=150: justificado como 15% do chunk_size, regra dos 10-20%
- RecursiveCharacterTextSplitter vs CharacterTextSplitter: cascata de separadores explicada
- Guia de ajuste por tipo de documento: presente
- Impacto no custo: calculado (<$0.001 para 34 paginas)

**Veredicto:** APROVADO

---

### 3. Prompt template projetado com 4 secoes

| Status | Entregavel |
|---|---|
| FEITO (parcial) | Template existe em `src/search.py` mas com ressalvas |

**Verificacao das 4 secoes obrigatorias (playbook linhas 374-393):**

| Secao | Playbook exige | src/search.py tem | Status |
|---|---|---|---|
| CONTEXTO: {context} | `{context}` | `{contexto}` | DIVERGENCIA no nome |
| REGRAS | 4 regras | 4 regras identicas | OK |
| EXEMPLOS | 3 exemplos (geral, ausente, opiniao) | 3 exemplos identicos | OK |
| PERGUNTA: {question} | `{question}` | `{pergunta}` | DIVERGENCIA no nome |

**Problema encontrado:** Os placeholders no template usam nomes em portugues
(`{contexto}`, `{pergunta}`) enquanto o playbook especifica nomes em ingles
(`{context}`, `{question}`). Isso importa porque o `chat.py` na Fase 3 vai
chamar `PROMPT_TEMPLATE.format(context=..., question=...)` — se os nomes nao
baterem, da KeyError em runtime.

**Veredicto:** APROVADO COM RESSALVA — funciona se o chat.py usar os nomes em
portugues. O relatorio `01-pipeline-rag.md` ja documenta o template com os
nomes corretos.

---

### 4. Pesquisa de referencias revisada (versoes e imports confirmados)

| Status | Entregavel |
|---|---|
| FEITO | Relatorio `03-referencias-atualizadas.md` cobre todos os 6 pontos |

**Cobertura verificada:**

| Topico pesquisado | Coberto? | Achado critico |
|---|---|---|
| LangChain API changes | Sim | PyPDFLoader sem mudanca |
| langchain-postgres vs community | Sim | PGVector DEPRECADO desde v0.0.14 |
| pgVector Docker config | Sim | docker-compose.yml correto |
| similarity_search_with_score | Sim | Scores normalizados 0-1 no PGVectorStore |
| Prompt grounding | Sim | 6 de 8 boas praticas aplicadas |
| text-embedding-3-small vs ada-002 | Sim | 3-small e 5x mais barato e melhor |

**Veredicto:** APROVADO

---

## Avaliacao Geral da Fase 1

```
+--------------------------------------------------+----------+
| Entregavel                                       | Status   |
+--------------------------------------------------+----------+
| Pipeline RAG explicado                           | APROVADO |
| Decisoes de chunking documentadas                | APROVADO |
| Prompt template projetado                        | APROVADO*|
| Pesquisa de referencias revisada                 | APROVADO |
+--------------------------------------------------+----------+
| GATE FASE 1                                      | APROVADO |
+--------------------------------------------------+----------+

* Com ressalva: placeholders em portugues vs ingles (ver plano de mudanca)
```

---

## Problemas Encontrados na Pesquisa (Relatorio 03)

A pesquisa de referencias revelou **divergencias criticas** entre o que o
playbook especifica e o que deveria ser usado nas Fases 2 e 3.

### PROBLEMA 1 — PGVector deprecado (CRITICO)

**O que o playbook diz (linhas 486-494):**
```python
from langchain_postgres import PGVector
vector_store = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
    pre_delete_collection=True,
)
```

**O que deveria ser usado (langchain-postgres 0.0.15+):**
```python
from langchain_postgres import PGEngine, PGVectorStore

engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
engine.init_vectorstore_table(table_name="documents", vector_size=1536)

store = PGVectorStore.create_sync(
    engine=engine,
    table_name="documents",
    embedding_service=embeddings,
)
store.add_documents(chunks)
```

**Impacto:** `PGVector` emite DeprecationWarning. Funciona hoje mas pode
quebrar em versoes futuras. API `from_documents()` nao existe no PGVectorStore.

**Severidade:** ALTA — afeta `ingest.py` (Fase 2) e `search.py` (Fase 3)

---

### PROBLEMA 2 — search.py instanciacao do vector store (MEDIO)

**O que o playbook diz (linhas 596-602):**
```python
from langchain_postgres import PGVector
vector_store = PGVector(
    embeddings=embeddings,
    connection=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
)
```

**O que deveria ser usado:**
```python
from langchain_postgres import PGEngine, PGVectorStore

engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
store = PGVectorStore.create_sync(
    engine=engine,
    table_name="documents",
    embedding_service=embeddings,
)
```

---

### PROBLEMA 3 — Score interpretation (BAIXO)

**O que o playbook diz (linha 611):**
```
Score: menor = mais relevante (distancia coseno)
```

**O que a pesquisa revelou:**
No `PGVectorStore`, scores sao normalizados 0-1 onde **maior = mais similar**.
A interpretacao no playbook esta invertida (era verdade no antigo
langchain-community, mas mudou).

---

### PROBLEMA 4 — Placeholders do prompt template (BAIXO)

**O que o playbook diz (linhas 656-673):**
```
{context} e {question}
```

**O que src/search.py tem:**
```
{contexto} e {pergunta}
```

Nao e erro se o chat.py usar os mesmos nomes. Mas o playbook original do
Cursor usa ingles, e misturar pode causar confusao.

---

## Plano de Mudanca para Fases 2 e 3

Baseado nos problemas encontrados, aqui esta o plano de ajuste para
implementar as proximas fases com as APIs corretas.

### Mudanca 1 — ingest.py: usar PGVectorStore (Fase 2)

**Arquivo:** `src/ingest.py`
**Prioridade:** ALTA
**Motivo:** PGVector.from_documents() esta deprecado

```python
# ANTES (playbook original):
from langchain_postgres import PGVector
vector_store = PGVector.from_documents(...)

# DEPOIS (API atualizada):
from langchain_postgres import PGEngine, PGVectorStore

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"

engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
engine.init_vectorstore_table(
    table_name="documents",
    vector_size=1536,
    overwrite_existing=True,  # equivale ao pre_delete_collection=True
)

store = PGVectorStore.create_sync(
    engine=engine,
    table_name="documents",
    embedding_service=embeddings,
)
store.add_documents(chunks)
```

**Validacao:** mesmas queries SQL do playbook funcionam, mas tabela muda de
`langchain_pg_embedding` para `documents` (nome customizado).

---

### Mudanca 2 — search.py: usar PGVectorStore (Fase 3)

**Arquivo:** `src/search.py`
**Prioridade:** ALTA
**Motivo:** Consistencia com ingest.py

```python
# ANTES (playbook original):
from langchain_postgres import PGVector
vector_store = PGVector(embeddings=..., connection=..., collection_name=...)

# DEPOIS (API atualizada):
from langchain_postgres import PGEngine, PGVectorStore

engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
store = PGVectorStore.create_sync(
    engine=engine,
    table_name="documents",
    embedding_service=embeddings,
)

def search(query: str, k: int = 10):
    results = store.similarity_search_with_score(query, k=k)
    return results
    # NOTA: score agora e 0-1 onde MAIOR = mais similar
```

---

### Mudanca 3 — Prompt template: padronizar placeholders (Fase 3)

**Arquivo:** `src/search.py` (template) e futuro `src/chat.py`
**Prioridade:** BAIXA
**Motivo:** Evitar confusao entre portugues/ingles nos placeholders

**Decisao:** Manter em portugues (`{contexto}`, `{pergunta}`) ja que o projeto
inteiro e em portugues. O chat.py devera usar:
```python
prompt = PROMPT_TEMPLATE.format(contexto=context_text, pergunta=question)
```

Nao mudar o template que ja existe — ele esta correto e consistente.

---

### Mudanca 4 — Queries de validacao SQL (Fase 2)

**Prioridade:** MEDIA
**Motivo:** O PGVectorStore usa tabela com nome customizado em vez de
`langchain_pg_embedding`

```sql
-- ANTES (playbook):
SELECT count(*) FROM langchain_pg_embedding;

-- DEPOIS (PGVectorStore com table_name="documents"):
SELECT count(*) FROM documents;
```

---

### Mudanca 5 — Connection string driver (ja correto)

**Prioridade:** NENHUMA — ja esta correto
```python
# O playbook ja usa psycopg (v3), nao psycopg2:
CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
```

---

## Resumo do Plano

```
+-----+-------------------------------+-----------+------------+----------+
| #   | Mudanca                       | Arquivo   | Prioridade | Fase     |
+-----+-------------------------------+-----------+------------+----------+
| 1   | PGVector -> PGVectorStore     | ingest.py | ALTA       | Fase 2   |
| 2   | PGVector -> PGVectorStore     | search.py | ALTA       | Fase 3   |
| 3   | Padronizar placeholders       | search.py | BAIXA      | Fase 3   |
| 4   | Ajustar queries SQL validacao | validacao | MEDIA      | Fase 2   |
| 5   | Connection string driver      | nenhum    | JA CORRETO | -        |
+-----+-------------------------------+-----------+------------+----------+
```

## Proximos Passos

1. Abrir PR da Fase 1 (`bash scripts/create-pr.sh 1`) com os 3 relatorios + este
2. Na Fase 2, implementar `ingest.py` ja com `PGVectorStore` (Mudanca 1)
3. Na Fase 3, implementar `search.py` ja com `PGVectorStore` (Mudanca 2)
4. Documentar desvios do playbook no PR de cada fase
