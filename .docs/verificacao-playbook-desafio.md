# Verificação: playbook.md vs desafio.md

**Data:** 2026-03-03  
**Objetivo:** Garantir alinhamento 100% antes da implementação.

---

## Resultado por Item

| # | Item | Status | Localização |
|---|------|--------|-------------|
| 1 | Imports | ✅ CONFORME | — |
| 2 | Parâmetros | ✅ CONFORME | — |
| 3 | Prompt template | ✅ CONFORME | — |
| 4 | Comandos de execução | ✅ CONFORME | Corrigido em create-pr.sh L42 |
| 5 | Estrutura de arquivos | ✅ CONFORME | — |
| 6 | Import do chat.py | ✅ CONFORME | — |

---

## 1. Imports

**Status: CONFORME**

| Import | desafio.md | playbook.md |
|--------|------------|-------------|
| PyPDFLoader | L45 `langchain_community.document_loaders` | L417 `langchain_community.document_loaders` |
| RecursiveCharacterTextSplitter | L42 `langchain_text_splitters` | L383 `langchain_text_splitters` |
| OpenAIEmbeddings | L43 `langchain_openai` | L398, L471 `langchain_openai` |
| PGVector | L45 `langchain_postgres` | L422, L475 `langchain_postgres` |
| GoogleGenerativeAIEmbeddings | L44 `langchain_google_genai` | L400, L473 (comentado) |

---

## 2. Parâmetros

**Status: CONFORME**

| Parâmetro | desafio.md | playbook.md |
|-----------|------------|-------------|
| chunk_size | L68: 1000 | L383: 1000 |
| chunk_overlap | L68: 150 | L384: 150 |
| k | L77: 10 | L485, L545: 10 |
| embeddings model | L53: text-embedding-3-small | L398, L471: text-embedding-3-small |
| LLM model | L54: gpt-5-nano | L538: gpt-5-nano |

---

## 3. Prompt Template

**Status: CONFORME**

- **desafio.md L81-106:** Template com CONTEXTO, REGRAS, EXEMPLOS, PERGUNTA DO USUÁRIO
- **playbook.md L507-527:** Especifica o mesmo template, placeholders `{contexto}` e `{pergunta}`
- **src/search.py (stub):** Já possui PROMPT_TEMPLATE com `{contexto}` e `{pergunta}` — alinhado

O desafio usa descrições nos placeholders (`{resultados concatenados...}`, `{pergunta do usuário}`). O playbook usa nomes de variáveis Python (`{contexto}`, `{pergunta}`) — equivalente e correto para `.format()`.

---

## 4. Comandos de Execução

**Status: CONFORME** (correção aplicada)

| Comando | desafio.md | playbook.md | create-pr.sh |
|---------|------------|-------------|--------------|
| docker compose up -d | L147 | L116, L664 | — |
| python src/ingest.py | L155 | L190, L437, L665 | L40 ✅ |
| python src/chat.py | L167 | L193, L545, L667, L728 | L42 ✅ |

**Correção aplicada:** `scripts/create-pr.sh` L42 — alterado de `python -m src.chat` para `python src/chat.py`.

---

## 5. Estrutura de Arquivos

**Status: CONFORME**

**desafio.md L114-123:**
```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   ├── chat.py
├── document.pdf
└── README.md
```

**playbook.md L47-58:** Mesma estrutura + `__init__.py` e `.gitignore` (extensões aceitáveis).

---

## 6. Import do chat.py

**Status: CONFORME**

- **playbook L503, L589:** `from search import search` (função `search` em search.py)
- **Padrão:** Import relativo dentro de `src/`, sem prefixo `src.` — correto para `python src/chat.py`
- **Nota:** O stub atual usa `search_prompt`; a implementação seguirá o playbook com `search()`.

---

## Conclusão

O playbook está **100% alinhado** com o desafio.md. A única divergência (comando do chat no create-pr.sh) foi corrigida. Pode iniciar a implementação.
