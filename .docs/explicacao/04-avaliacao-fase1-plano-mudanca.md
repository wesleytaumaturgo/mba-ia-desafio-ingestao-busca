# 04 — Avaliacao da Fase 1 + Plano de Mudanca

> Auditoria dos entregaveis da Fase 1 (Descoberta) contra o playbook.md e desafio.md
> Data: marco/2026

---

## Decisao Estrategica: Seguir o Desafio ao Pe da Letra

Apos revisar o `desafio.md`, a decisao e **seguir exatamente o que o desafio
especifica**, mesmo onde a pesquisa de referencias (relatorio 03) identificou
APIs mais recentes.

**Motivo:** O avaliador do MBA espera ver os imports e APIs listados no desafio.
Usar APIs diferentes (mesmo que melhores) pode causar estranhamento ou ser
interpretado como nao ter seguido as instrucoes.

**Consequencia:** Os problemas 1 e 2 identificados abaixo sao ACEITOS como
limitacoes conhecidas, nao serao corrigidos.

```
+-------------------------------------------+------------------+
| Item do desafio                           | Decisao          |
+-------------------------------------------+------------------+
| from langchain_postgres import PGVector   | SEGUIR (linha 43)|
| PGVector.from_documents()                 | SEGUIR           |
| similarity_search_with_score(query, k=10) | SEGUIR (linha 44)|
| Prompt template identico ao desafio       | SEGUIR (linha 81)|
| Estrutura de arquivos do desafio          | SEGUIR (linha110)|
+-------------------------------------------+------------------+
```

---

## Checklist do Gate — Fase 1

O playbook define 4 entregaveis no gate da Fase 1 (linhas 423-428):

### 1. Explicar o pipeline RAG em 3 frases sem consultar docs

| Status | Entregavel |
|---|---|
| FEITO | Relatorio `01-pipeline-rag.md` cobre os 8 passos do pipeline completo |

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
- chunk_size=1000: requisito do desafio (linha 66)
- chunk_overlap=150: requisito do desafio (linha 66)
- RecursiveCharacterTextSplitter: requisito do desafio (linha 39)

**Nota:** Esses valores sao requisitos fixos do desafio, nao decisoes do projeto.
A documentacao em `02-decisoes-chunking.md` serve como material de estudo pessoal.

**Veredicto:** APROVADO

---

### 3. Prompt template projetado com 4 secoes

| Status | Entregavel |
|---|---|
| FEITO | Template em `src/search.py` segue o desafio |

**Verificacao contra o prompt do desafio (linhas 81-106):**

| Secao | Desafio exige | src/search.py tem | Status |
|---|---|---|---|
| CONTEXTO | `{resultados concatenados do banco de dados}` | `{contexto}` | OK |
| REGRAS | 4 regras | 4 regras identicas | OK |
| EXEMPLOS | 3 exemplos | 3 exemplos identicos | OK |
| PERGUNTA DO USUARIO | `{pergunta do usuario}` | `{pergunta}` | OK |

O template em `src/search.py` ja esta **identico ao do desafio**.
Os placeholders usam portugues (`{contexto}`, `{pergunta}`) — consistente
com o desafio que esta inteiro em portugues.

**Veredicto:** APROVADO

---

### 4. Pesquisa de referencias revisada

| Status | Entregavel |
|---|---|
| FEITO | Relatorio `03-referencias-atualizadas.md` cobre os 6 pontos |

A pesquisa identificou que `PGVector` esta deprecado, mas a decisao e
seguir o desafio mesmo assim. A pesquisa serve como conhecimento adicional.

**Veredicto:** APROVADO

---

## Avaliacao Geral da Fase 1

```
+--------------------------------------------------+----------+
| Entregavel                                       | Status   |
+--------------------------------------------------+----------+
| Pipeline RAG explicado                           | APROVADO |
| Decisoes de chunking documentadas                | APROVADO |
| Prompt template projetado                        | APROVADO |
| Pesquisa de referencias revisada                 | APROVADO |
+--------------------------------------------------+----------+
| GATE FASE 1                                      | APROVADO |
+--------------------------------------------------+----------+
```

---

## Divergencias Conhecidas (pesquisa vs desafio)

A pesquisa (relatorio 03) encontrou divergencias. Todas sao ACEITAS porque
o desafio tem prioridade sobre boas praticas de versao.

### DIVERGENCIA 1 — PGVector deprecado (ACEITA)

**O que a pesquisa diz:** PGVector deprecado desde v0.0.14, usar PGVectorStore.
**O que o desafio pede (linha 43):** `from langchain_postgres import PGVector`
**Decisao:** Usar PGVector como o desafio pede. Funciona na v0.0.15.

### DIVERGENCIA 2 — Score interpretation (ACEITA)

**O que a pesquisa diz:** No PGVectorStore, scores sao 0-1 (maior=melhor).
**O que o desafio usa:** PGVector com similarity_search_with_score
(retorna distancia — menor=melhor).
**Decisao:** Seguir o comportamento do PGVector. Testar na implementacao.

### DIVERGENCIA 3 — Placeholders do prompt (NAO EXISTE)

O desafio usa portugues no prompt. O `src/search.py` usa portugues.
Nao ha divergencia — o playbook que sugeria ingles nao e o desafio.

---

## Plano para Fases 2 e 3 — Seguindo o Desafio

### Fase 2 — ingest.py (seguir desafio linhas 64-68)

```python
# Imports exatos do desafio:
from langchain_community.document_loaders import PyPDFLoader          # linha 42
from langchain_text_splitters import RecursiveCharacterTextSplitter    # linha 39
from langchain_openai import OpenAIEmbeddings                         # linha 40
from langchain_postgres import PGVector                                # linha 43

# Parametros exatos do desafio:
chunk_size=1000, chunk_overlap=150                                     # linha 66
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")          # linha 51
PGVector.from_documents(...)                                           # linha 43
```

### Fase 3 — search.py + chat.py (seguir desafio linhas 72-106)

```python
# Busca exata do desafio:
similarity_search_with_score(query, k=10)                              # linha 44

# LLM exata do desafio:
ChatOpenAI(model="gpt-5-nano", temperature=0)                         # linha 52

# Prompt identico ao desafio (linhas 81-106):
# CONTEXTO → REGRAS → EXEMPLOS → PERGUNTA DO USUARIO
```

### Fase 4 — README.md (seguir desafio linha 173)

Entregavel: README com instrucoes claras de execucao.
Ordem de execucao do desafio (linhas 146-168):
1. `docker compose up -d`
2. `python src/ingest.py`
3. `python src/chat.py`

---

## Resumo

```
+----------------------------------+---------------------------+
| Decisao                          | Justificativa             |
+----------------------------------+---------------------------+
| Usar PGVector (nao PGVectorStore)| Desafio pede (linha 43)   |
| Usar from_documents()            | Padrao do desafio         |
| chunk_size=1000, overlap=150     | Requisito fixo (linha 66) |
| Prompt identico ao desafio       | Requisito fixo (linha 81) |
| gpt-5-nano, temperature=0       | Requisito fixo (linha 52) |
| text-embedding-3-small           | Requisito fixo (linha 51) |
| README com instrucoes            | Entregavel (linha 173)    |
+----------------------------------+---------------------------+
```
