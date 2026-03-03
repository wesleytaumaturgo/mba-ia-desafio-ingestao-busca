# 06 — Catalogo de Prompts

> Registro de todos os prompts prontos para uso com skills do Claude Code
> Atualizado a cada novo prompt gerado

---

## Indice

| # | Skill | Finalidade | Fase |
|---|---|---|---|
| 1 | `@verification-before-completion` | Checagem final playbook vs desafio | Pre-implementacao |
| 2 | `@comprehensive-review-full-review` | Revisao completa playbook vs desafio | Pre-implementacao |
| 3 | `@verification-before-completion` | Verificar gate da Fase 0 — Bootstrap | Fase 0 |
| 4 | `@verification-before-completion` | Verificar gate da Fase 2 — Ingestao | Fase 2 |
| 5 | `@verification-before-completion` | Verificar gate da Fase 3 — Busca + Chat | Fase 3 |
| 6 | `@verification-before-completion` | Verificar gate da Fase 4 — Polish e Entrega | Fase 4 |
| 7 | `@prompt-engineer` `@rag-engineer` | Revisao do prompt template e grounding | Fase 3 |
| 8 | `@requesting-code-review` | Code review dos arquivos Fase 2+3 antes do PR | Fase 3 |

### Registro de Execucoes

| Data | Prompt # | Resultado | Observacao |
|---|---|---|---|
| 2026-03-03 | #1 (`@verification-before-completion`) | 6/6 CONFORME | Zero divergencias criticas. 3 divergencias menores entre stubs e playbook (serao resolvidas nas Fases 2-3) |
| 2026-03-03 | #2 (`@comprehensive-review-full-review`) | 42/42 CONFORME, 0 DIVERGE, 18 EXTRA | Revisao completa prompt a prompt. Todas correcoes anteriores confirmadas por grep. Consistencia interna OK em 8 valores-chave. |
| 2026-03-03 | #7 (`@prompt-engineer` `@rag-engineer`) | 7/7 OK | Prompt template, grounding, exemplos, temperature, separador, embeddings — tudo conforme. Nenhuma melhoria necessaria para o escopo do desafio. |
| 2026-03-03 | #8 (`@requesting-code-review`) | BLOQUEADO | Arquivos no disco sao stubs. Implementacoes no IDE nao foram salvas. Salvar antes de executar. |

---

## Recomendacao de Skills por Contexto

```
+------------------------------------+-------------------------------------------+---------------------------+
| Contexto                           | Skill Recomendado                         | Quando Usar               |
+------------------------------------+-------------------------------------------+---------------------------+
| Revisar playbook vs desafio        | @verification-before-completion           | Antes de implementar      |
|                                    | @comprehensive-review-full-review         | Revisao profunda          |
+------------------------------------+-------------------------------------------+---------------------------+
| Implementar codigo Python          | @rag-engineer                             | Pipeline RAG completo     |
|                                    | @python-pro                               | Codigo Python geral       |
+------------------------------------+-------------------------------------------+---------------------------+
| Revisar codigo antes de PR         | @code-reviewer                            | Code review geral         |
|                                    | @code-review-checklist                    | Checklist estruturado     |
+------------------------------------+-------------------------------------------+---------------------------+
| Arquitetura e design               | @architecture-patterns                    | Padroes arquiteturais     |
|                                    | @ai-agents-architect                      | Design de agentes IA      |
+------------------------------------+-------------------------------------------+---------------------------+
| Prompt engineering                 | @prompt-engineer                          | Otimizar prompts LLM      |
|                                    | @prompt-engineering-patterns              | Padroes de prompts        |
+------------------------------------+-------------------------------------------+---------------------------+
| LangChain especifico               | @langchain-architecture                   | Arquitetura LangChain     |
|                                    | @rag-implementation                       | Implementacao RAG         |
+------------------------------------+-------------------------------------------+---------------------------+
| Banco de dados / pgVector          | @postgres-best-practices                  | PostgreSQL geral          |
|                                    | @vector-database-engineer                 | Banco vetorial            |
|                                    | @database-architect                       | Design de banco           |
+------------------------------------+-------------------------------------------+---------------------------+
| Docker e infra                     | @docker-expert                            | Docker/Compose            |
+------------------------------------+-------------------------------------------+---------------------------+
| README e documentacao              | @readme                                   | Gerar README              |
|                                    | @documentation                            | Documentacao geral        |
+------------------------------------+-------------------------------------------+---------------------------+
| Testes                             | @python-testing-patterns                  | Testes Python             |
|                                    | @test-driven-development                  | TDD                       |
+------------------------------------+-------------------------------------------+---------------------------+
| PR e Git                           | @create-pr                                | Criar pull request        |
|                                    | @commit                                   | Criar commit              |
+------------------------------------+-------------------------------------------+---------------------------+
```

---

## Prompt #1 — Checagem Final (verification-before-completion)

**Skill:** `@verification-before-completion`
**Finalidade:** Verificar se o playbook.md esta 100% alinhado com o desafio.md antes de iniciar a implementacao
**Fase:** Pre-implementacao (entre Fase 1 e Fase 2)

```
@verification-before-completion

Verifique se o playbook.md esta 100% alinhado com o desafio.md antes de iniciar a implementacao.

## Arquivos para verificar:
- playbook.md (playbook de prompts — fonte das instrucoes de implementacao)
- desafio.md (especificacao oficial do desafio — fonte da verdade)
- src/ingest.py, src/search.py, src/chat.py (stubs atuais)

## Checklist de verificacao:

1. **Imports** — Cada import no playbook e identico ao desafio?
   - PyPDFLoader, RecursiveCharacterTextSplitter, OpenAIEmbeddings, PGVector, GoogleGenerativeAIEmbeddings

2. **Parametros** — chunk_size=1000, chunk_overlap=150, k=10, model="text-embedding-3-small", model="gpt-5-nano"

3. **Prompt template** — O template no playbook e identico ao do desafio (linhas 81-106)?
   - Placeholders devem ser {contexto} e {pergunta}

4. **Comandos de execucao** — O playbook usa os mesmos comandos do desafio?
   - docker compose up -d
   - python src/ingest.py
   - python src/chat.py (NAO python -m src.chat)

5. **Estrutura de arquivos** — O playbook segue a estrutura do desafio (linhas 114-123)?

6. **Import do chat.py** — Deve ser `from search import search_prompt` (NAO `from src.search import ...`)

Para cada item, responda: CONFORME / DIVERGE + localizacao exata (linha do playbook e linha do desafio).
```

---

## Prompt #2 — Revisao Completa (comprehensive-review-full-review)

**Skill:** `@comprehensive-review-full-review`
**Finalidade:** Revisao completa e profunda do playbook.md contra o desafio.md
**Fase:** Pre-implementacao (entre Fase 1 e Fase 2)

```
@comprehensive-review-full-review

Faca uma revisao completa do playbook.md contra o desafio.md.

## Contexto:
Este e um projeto de MBA onde o avaliador vai seguir o desafio.md ao pe da letra.
O playbook.md contem os prompts que serao usados no Cursor para gerar o codigo.
Qualquer divergencia entre playbook e desafio pode resultar em codigo que nao atende os requisitos.

## Escopo da revisao:
1. Compare CADA prompt do playbook com a secao correspondente do desafio
2. Verifique imports, parametros, nomes de variaveis, comandos de execucao
3. Identifique itens EXTRA (playbook adiciona algo que o desafio nao pede)
4. Identifique DIVERGENCIAS (playbook contradiz o desafio)
5. Classifique cada divergencia como CRITICA (quebra execucao) ou MENOR (nao afeta resultado)

## Arquivos:
- playbook.md
- desafio.md
- .docs/explicacao/05-auditoria-playbook-vs-desafio.md (auditoria anterior — verificar se as correcoes foram aplicadas)

## Output esperado:
Tabela com: Item | Playbook (linha) | Desafio (linha) | Status (CONFORME/DIVERGE/EXTRA)
```

---

## Prompt #3 — Gate Fase 0: Bootstrap (verification-before-completion)

**Skill:** `@verification-before-completion`
**Finalidade:** Verificar se a Fase 0 (Bootstrap do Ambiente) esta completa
**Fase:** Fase 0

```
@verification-before-completion

Verifique se a FASE 0 — Bootstrap do Ambiente esta completa.

## Gate (playbook L19):
- docker compose ps mostra PostgreSQL rodando
- python -c "import langchain" passa

## Entregaveis a verificar:

1. **Estrutura de diretorios** — src/ com ingest.py, search.py, chat.py existem?
   Desafio linhas 114-123.

2. **docker-compose.yml** — Existe? Imagem pgvector? Porta 5432? Credenciais langchain/langchain?
   Executar: docker compose ps

3. **requirements.txt** — Existe? Contem langchain, langchain-openai, langchain-community,
   langchain-postgres, langchain-text-splitters, langchain-google-genai, pypdf, python-dotenv?
   Executar: pip list | grep langchain

4. **.env.example** — Existe? Contem OPENAI_API_KEY?
   Desafio linha 117.

5. **.env** — Existe (local, nao commitado)? Tem API key configurada?
   Verificar: .env esta no .gitignore?

6. **.gitignore** — Protege venv/, .env, __pycache__/?

7. **document.pdf** — Existe na raiz do projeto?

8. **venv** — Ativo? which python aponta para venv/bin/python?

## Comandos de verificacao (executar todos):
- docker compose ps
- python -c "import langchain; print(langchain.__version__)"
- ls src/ingest.py src/search.py src/chat.py
- cat .env.example
- grep ".env" .gitignore
- ls document.pdf
- which python

Para cada item: PASS (com evidencia do comando) ou FAIL (com erro exato).
```

---

## Prompt #4 — Gate Fase 2: Ingestao (verification-before-completion)

**Skill:** `@verification-before-completion`
**Finalidade:** Verificar se a Fase 2 (Ingestao do PDF) esta completa
**Fase:** Fase 2

```
@verification-before-completion

Verifique se a FASE 2 — Ingestao do PDF esta completa.

## Gate (playbook L437):
- python src/ingest.py executa sem erros
- Vetores estao no banco

## Entregaveis a verificar:

1. **src/ingest.py funcional** — Executar: python src/ingest.py
   Esperado: 3 prints (paginas carregadas, chunks gerados, ingestao concluida)

2. **Imports corretos** — Verificar no codigo:
   - from langchain_community.document_loaders import PyPDFLoader (desafio L42)
   - from langchain_text_splitters import RecursiveCharacterTextSplitter (desafio L39)
   - from langchain_openai import OpenAIEmbeddings (desafio L40)
   - from langchain_postgres import PGVector (desafio L43)

3. **Parametros corretos**:
   - chunk_size=1000, chunk_overlap=150 (desafio L66)
   - model="text-embedding-3-small" (desafio L51)

4. **Chunks no banco** — Executar:
   docker compose exec postgres psql -U langchain -d langchain -c \
     "SELECT count(*) FROM langchain_pg_embedding;"
   Esperado: mesmo numero que o print "Chunks gerados: X"

5. **Dimensao dos vetores** — Executar:
   docker compose exec postgres psql -U langchain -d langchain -c \
     "SELECT vector_dims(embedding) FROM langchain_pg_embedding LIMIT 1;"
   Esperado: 1536

Para cada item: PASS (com evidencia) ou FAIL (com erro exato).
```

---

## Prompt #5 — Gate Fase 3: Busca + Chat (verification-before-completion)

**Skill:** `@verification-before-completion`
**Finalidade:** Verificar se a Fase 3 (Busca Semantica + Chat CLI) esta completa
**Fase:** Fase 3

```
@verification-before-completion

Verifique se a FASE 3 — Busca Semantica + Chat CLI esta completa.

## Gate (playbook L565):
- CLI responde perguntas no contexto
- CLI rejeita perguntas fora do contexto

## Entregaveis a verificar:

1. **src/search.py** — Verificar:
   - Mesmo modelo de embeddings do ingest.py (text-embedding-3-small)
   - Mesma CONNECTION_STRING e COLLECTION_NAME do ingest.py
   - similarity_search_with_score(query, k=k) (desafio L44)
   - Executar standalone: python src/search.py (testar com query)

2. **src/chat.py** — Verificar:
   - Import: from search import search (NAO from src.search)
   - Prompt template identico ao desafio (linhas 81-106)
   - Placeholders: {contexto} e {pergunta}
   - LLM: ChatOpenAI(model="gpt-5-nano", temperature=0) (desafio L52)
   - Funcao ask() chama search(question, k=10)
   - Output: PERGUNTA: / RESPOSTA: (desafio L15-16)

3. **Teste no contexto** — Executar: python src/chat.py
   Fazer pergunta sobre o conteudo do PDF
   Esperado: resposta correta baseada no PDF

4. **Teste fora do contexto** — Perguntar: "Qual e a capital da Franca?"
   Esperado: "Nao tenho informacoes necessarias para responder sua pergunta."

5. **Teste de saida** — Digitar: sair
   Esperado: "Ate logo!" e encerrar

6. **Consistencia** — CONNECTION_STRING e COLLECTION_NAME identicos em ingest.py e search.py?

Para cada item: PASS (com evidencia) ou FAIL (com erro exato).
```

---

## Prompt #6 — Gate Fase 4: Polish e Entrega (verification-before-completion)

**Skill:** `@verification-before-completion`
**Finalidade:** Verificar se a Fase 4 (Polish e Entrega) esta completa — checklist final
**Fase:** Fase 4

```
@verification-before-completion

Verifique se a FASE 4 — Polish e Entrega esta completa. Este e o checklist FINAL.

## Gate (playbook L809):
- Repositorio publico no GitHub, pronto para avaliacao

## Checklist final (desafio L173-175):

1. **README.md** — Existe? Tem instrucoes claras de execucao?
   Verificar que contem os 3 comandos: docker compose up -d, python src/ingest.py, python src/chat.py

2. **Validacao E2E do zero** — Executar na sequencia:
   a) docker compose down -v
   b) docker compose up -d (esperar subir)
   c) docker compose ps (postgres running?)
   d) python src/ingest.py (3 prints sem erro?)
   e) SELECT count(*) FROM langchain_pg_embedding (chunks no banco?)
   f) python src/chat.py → pergunta no contexto (resposta correta?)
   g) python src/chat.py → "Qual e a capital da Franca?" (rejeita?)
   h) python src/chat.py → "sair" (encerra?)

3. **Seguranca** — git status: .env NAO aparece? .env.example aparece?

4. **Estrutura** — Todos os arquivos do desafio (L114-123) existem?
   docker-compose.yml, requirements.txt, .env.example, src/ingest.py,
   src/search.py, src/chat.py, document.pdf, README.md

5. **Codigo limpo** — Sem prints de debug? Sem imports nao utilizados?

6. **Repositorio publico** — gh repo view mostra visibility: public?

Para cada item: PASS (com evidencia do comando) ou FAIL (com erro exato).
Se todos PASS: projeto pronto para entrega.
```

---

## Prompt #7 — Revisao Prompt Template e Grounding (prompt-engineer + rag-engineer)

**Skill:** `@prompt-engineer` `@rag-engineer`
**Finalidade:** Revisar o prompt template e regras de grounding do chat.py
**Fase:** Fase 3 (apos implementacao, antes do PR)

```
@prompt-engineer @rag-engineer

Revise o prompt template e as regras de grounding implementadas no chat.py.

Cole o conteudo completo de src/chat.py abaixo:
{{COLE_AQUI_O_CONTEUDO_DE_CHAT_PY}}

Verifique cada ponto:

1. O prompt template tem as 4 secoes obrigatorias?
   (CONTEXTO, REGRAS, EXEMPLOS, PERGUNTA)

2. As regras de grounding sao suficientes para evitar alucinacao?
   - "Responda somente com base no CONTEXTO" esta presente?
   - "Nunca invente" esta presente?

3. Os exemplos de rejeicao cobrem os 3 casos?
   - Conhecimento geral (ex: capital da Franca)
   - Dados nao presentes no PDF (ex: clientes 2024)
   - Opiniao (ex: voce acha bom?)

4. temperature=0 esta configurado na LLM?

5. O contexto e montado ANTES de chamar a LLM?
   (nao pode chamar a LLM sem contexto)

6. A concatenacao dos chunks usa separador claro ("\n\n---\n\n")?

7. O modelo de embeddings no search.py e identico ao do ingest.py?

Sugestoes de melhoria:
- Algum padrao de prompt injection que deveria ser tratado?
- O prompt poderia ser mais conciso sem perder eficacia?
- Algum edge case nao coberto pelos exemplos?

Para cada ponto: OK ou MELHORIA + sugestao concreta.
```

---
