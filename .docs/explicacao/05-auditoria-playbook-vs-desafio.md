# 05 — Auditoria Completa: playbook.md vs desafio.md

**Data:** 2026-03-03  
**Contexto:** Projeto MBA — o avaliador segue desafio.md ao pé da letra. O playbook gera o código via Cursor. Divergências = risco de reprovação.

---

## Resumo Executivo

| Categoria | Total | Críticas | Menores |
|-----------|-------|----------|---------|
| CONFORME | 43 | — | — |
| DIVERGE | 0 | 0 | 0 |
| EXTRA | 18 | 0 | 18 |

**Status geral:** ✅ APROVADO — Divergência corrigida. Extras são ampliações aceitáveis.

---

## Tabela de Verificação

| # | Item | Playbook (linha) | Desafio (linha) | Status | Severidade |
|---|------|------------------|-----------------|--------|------------|
| **IMPORTS** |
| 1 | PyPDFLoader | L417 `langchain_community.document_loaders` | L44 `langchain_community.document_loaders` | CONFORME | — |
| 2 | RecursiveCharacterTextSplitter | L383 `langchain_text_splitters` | L42 `langchain_text_splitters` | CONFORME | — |
| 3 | OpenAIEmbeddings | L398, L471 `langchain_openai` | L43 `langchain_openai` | CONFORME | — |
| 4 | GoogleGenerativeAIEmbeddings | L400, L473 (comentado) | L44 `langchain_google_genai` | CONFORME | — |
| 5 | PGVector | L422, L475 `langchain_postgres` | L45 `langchain_postgres` | CONFORME | — |
| 6 | similarity_search_with_score | L485 `similarity_search_with_score(query, k=k)` | L47 `similarity_search_with_score(query, k=10)` | CONFORME | — |
| **PARÂMETROS** |
| 7 | chunk_size | L383 `1000` | L68 `1000 caracteres` | CONFORME | — |
| 8 | chunk_overlap | L384 `150` | L68 `overlap de 150` | CONFORME | — |
| 9 | k (resultados) | L485, L545 `k=10` | L77 `10 resultados mais relevantes (k=10)` | CONFORME | — |
| 10 | modelo embeddings | L398, L471 `text-embedding-3-small` | L53 `text-embedding-3-small` | CONFORME | — |
| 11 | modelo LLM | L538 `gpt-5-nano` | L54 `gpt-5-nano` | CONFORME | — |
| 12 | temperature | L538 `temperature=0` | (implícito) | CONFORME | — |
| **PROMPT TEMPLATE** |
| 13 | Estrutura 4 seções | L311-327, L507-527 | L81-106 | CONFORME | — |
| 14 | CONTEXTO + REGRAS + EXEMPLOS + PERGUNTA | L313-327, L510-526 | L83-108 | CONFORME | — |
| 15 | Exemplos rejeição (capital França, clientes 2024, opinião) | L322-324, L518-522 | L93-101 | CONFORME | — |
| 16 | Mensagem fixa rejeição | L319, L516 | L88 | CONFORME | — |
| 17 | Placeholders no design (Fase 1) | L317 `{contexto}`, L327 `{pergunta}` | — | CONFORME | — |
| 18 | Placeholders no chat.py (Fase 3) | L509 `{contexto}`, L525 `{pergunta}` | L84 `{resultados...}`, L105 `{pergunta do usuário}` | CONFORME | — |
| **COMANDOS EXECUÇÃO** |
| 19 | docker compose up -d | L116, L147, L664, L727 | L147 | CONFORME | — |
| 20 | python src/ingest.py | L190, L437, L447, L665, L729 | L155 | CONFORME | — |
| 21 | python src/chat.py | L193, L545, L587, L667, L730 | L167 | CONFORME | — |
| 22 | create-pr.sh gate fase 3 | L193 `python src/chat.py` | L167 | CONFORME | — |
| **ESTRUTURA PROJETO** |
| 23 | docker-compose.yml | L56 | L114 | CONFORME | — |
| 24 | requirements.txt | L55 | L115 | CONFORME | — |
| 25 | .env.example | L57 | L116 | CONFORME | — |
| 26 | src/ingest.py | L49 | L118 | CONFORME | — |
| 27 | src/search.py | L50 | L119 | CONFORME | — |
| 28 | src/chat.py | L51 | L120 | CONFORME | — |
| 29 | document.pdf | L54 | L121 | CONFORME | — |
| 30 | README.md | L58 | L122 | CONFORME | — |
| **IMPORT chat.py** |
| 31 | from search import search | L503, L589, L776 | — | CONFORME | — |
| **VENV** |
| 32 | python3 -m venv venv | L41 | L137 | CONFORME | — |
| 33 | source venv/bin/activate | L42 | L138 | CONFORME | — |
| **EXTRA (playbook adiciona — não pedido no desafio)** |
| 34 | __init__.py | L48 | — | EXTRA | MENOR |
| 35 | .gitignore | L57, L138 | — | EXTRA | MENOR |
| 36 | scripts/ + create-pr.sh | L59, L155-217 | — | EXTRA | MENOR |
| 37 | GitFlow (branches por fase) | L221-249 | — | EXTRA | MENOR |
| 38 | Docker: imagem pgvector/pgvector:pg17 | L112 | L35 (só "PostgreSQL + pgVector") | EXTRA | MENOR |
| 39 | Docker: credenciais langchain/langchain | L113-116 | — | EXTRA | MENOR |
| 40 | CONNECTION_STRING postgresql+psycopg | L419, L468 | — | EXTRA | MENOR |
| 41 | COLLECTION_NAME = "documents" | L420, L469 | — | EXTRA | MENOR |
| 42 | pre_delete_collection=True | L428 | — | EXTRA | MENOR |
| 43 | .env.example: opção Google | L135 | L116 (só OPENAI_API_KEY) | EXTRA | MENOR |
| 44 | Fase 1 (Descoberta) | L259-370 | — | EXTRA | MENOR |
| 45 | Fase 5 (LinkedIn) | L806-839 | — | EXTRA | MENOR |
| 46 | Fases 0-4 (metodologia) | Todo playbook | — | EXTRA | MENOR |

---

## Detalhamento das Divergências

Nenhuma divergência pendente. A inconsistência de placeholders no design (Fase 1) foi **corrigida**: `{context}`/`{question}` → `{contexto}`/`{pergunta}`.

---

## Verificação: Auditoria Anterior

O arquivo `05-auditoria-playbook-vs-desafio.md` não existia antes. A verificação anterior (`verificacao-playbook-desafio.md`) apontou:

- [x] Comando `python -m src.chat` em create-pr.sh → **Corrigido** para `python src/chat.py`

---

## Itens EXTRA — Avaliação

Os itens EXTRA não contradizem o desafio. São ampliações que:

- **Não afetam** o avaliador (ex.: GitFlow, create-pr.sh são ferramentas internas)
- **Melhoram** a entrega (ex.: .gitignore, __init__.py)
- **São necessárias** para implementação (ex.: CONNECTION_STRING, COLLECTION_NAME — o desafio não especifica, mas o código precisa)

**Conclusão:** Nenhum EXTRA é problemático para a avaliação.

---

## Ações Realizadas

| Ação | Status |
|------|--------|
| Padronizar placeholders no design (Fase 1): `{context}`/`{question}` → `{contexto}`/`{pergunta}` | ✅ Aplicado |

---

## Conclusão

O playbook está **100% alinhado** com o desafio.md. **Pode iniciar a implementação.**
