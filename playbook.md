# Prompt Playbook — Ingestao e Busca Semantica com LangChain e Postgres
**Projeto:** CLI Python para ingestao de PDFs e busca semantica via embeddings
**Stack:** Python 3.12 · LangChain · PostgreSQL/pgVector · Docker Compose · OpenAI API
**Metodologia:** Design First, Code Second — 5 fases (0-4), nenhuma pode ser pulada
**Ferramentas:** Claude (arquitetura) · Gemini (pesquisa) · Cursor (codigo)
**Contexto:** Desafio tecnico MBA IA — Full Cycle

---

> **Como usar este documento**
> Siga as fases em ordem. Cada fase tem um **gate de conclusao** — so avance quando ele passar.
> Os placeholders `{{EM_MAIUSCULAS}}` sao os unicos trechos que voce edita antes de colar.
> Icones: 🧠 Claude · 🔍 Gemini · 🖥️ Cursor
> O projeto nao usa DDD nem framework web — e um CLI Python puro com LangChain.

---

## FASE 0 — Bootstrap do Ambiente
**Gate:** `docker compose ps` mostra PostgreSQL rodando e `python -c "import langchain"` passa.
**Entregaveis:** Repositorio forkado · venv ativo · Docker rodando · dependencias instaladas · .env configurado

---

### 🖥️ Cursor — Fork e estrutura inicial do projeto

```
@bash-scripting

Prepare o ambiente do projeto de ingestao e busca semantica com LangChain e pgVector.

Passos:

1. O repositorio ja foi forkado e clonado de:
   https://github.com/devfullcycle/mba-ia-desafio-ingestao-busca/
   Diretorio atual: {{DIRETORIO_DO_PROJETO}}

2. Crie o ambiente virtual Python:
   python3 -m venv venv
   source venv/bin/activate

3. Confirme que o venv esta ativo:
   which python → deve apontar para venv/bin/python

4. Verifique a estrutura do projeto. Se nao existir, crie:

{{DIRETORIO_DO_PROJETO}}/
├── src/
│   ├── __init__.py          → arquivo vazio (necessario para imports entre modulos)
│   ├── ingest.py            → sera criado na Fase 2
│   ├── search.py            → sera criado na Fase 3
│   └── chat.py              → sera criado na Fase 3
├── document.pdf             → PDF que sera ingerido (colocar manualmente)
├── docker-compose.yml       → sera criado a seguir
├── requirements.txt         → sera criado a seguir
├── .env.example             → sera criado a seguir
├── .gitignore               → sera criado a seguir
└── README.md                → sera criado na Fase 4

Crie apenas os diretorios e o src/__init__.py vazio por enquanto.
Os demais arquivos serao criados nos proximos prompts.

Criterio de sucesso: diretorio src/ existe com __init__.py vazio.
```

---

### 🖥️ Cursor — requirements.txt

```
@bash-scripting

Crie o arquivo requirements.txt com todas as dependencias do projeto.

O projeto usa LangChain para orquestracao, OpenAI para embeddings e LLM,
PostgreSQL com pgVector para armazenamento vetorial.

Dependencias necessarias (com versoes minimas):

langchain>=0.3.0                    → framework de orquestracao LLM
langchain-openai>=0.3.0             → integracao LangChain + OpenAI
langchain-google-genai>=2.0.0       → integracao LangChain + Google (alternativa)
langchain-community>=0.3.0          → loaders (PyPDFLoader)
langchain-postgres>=0.0.12          → integracao LangChain + pgVector
langchain-text-splitters>=0.3.0     → RecursiveCharacterTextSplitter
psycopg2-binary>=2.9.9              → driver PostgreSQL
python-dotenv>=1.0.0                → carregar .env
pypdf>=4.0.0                        → ler PDFs

NAO inclua comentarios no arquivo — apenas pacote>=versao, um por linha.

Apos criar o arquivo, execute:
pip install -r requirements.txt

Criterio de sucesso: python -c "import langchain; print(langchain.__version__)" funciona.
```

---

### 🖥️ Cursor — Docker Compose para PostgreSQL + pgVector

```
@bash-scripting @database-design

Crie o docker-compose.yml para PostgreSQL com a extensao pgVector.

Servico unico:
- Nome: postgres
- Imagem: pgvector/pgvector:pg17
  (imagem oficial do pgVector — ja vem com a extensao instalada)
- Porta: 5432:5432
- Variaveis de ambiente:
  POSTGRES_USER: langchain
  POSTGRES_PASSWORD: langchain
  POSTGRES_DB: langchain
- Volume nomeado: pgdata:/var/lib/postgresql/data
  (persiste dados entre restarts do container)

NAO inclua nenhum outro servico — apenas PostgreSQL.
NAO inclua healthcheck — a imagem padrao ja gerencia isso.

Criterio de sucesso: docker compose up -d && docker compose ps mostra postgres running.
```

---

### 🖥️ Cursor — Variaveis de ambiente e .gitignore

```
@bash-scripting

Crie os arquivos .env.example e .gitignore para o projeto.

Arquivo .env.example (este e commitado — mostra quais variaveis sao necessarias):
Conteudo:
  Comentario explicando que o usuario deve escolher UMA opcao.
  Opcao 1 — OpenAI: OPENAI_API_KEY=sk-...
  Opcao 2 — Google Gemini: GOOGLE_API_KEY=AIza...

Arquivo .gitignore (protege arquivos sensiveis e temporarios):
  venv/
  .env
  __pycache__/
  *.pyc
  .idea/
  .vscode/
  scripts/

Apos criar os dois arquivos, instrua o usuario a:
  cp .env.example .env
  # Editar .env e colar a API key real

REGRA: .env NUNCA pode ser versionado. .env.example sim.

Criterio de sucesso: .env.example existe, .gitignore lista .env.
```

---

### 🖥️ Cursor — Criar scripts/create-pr.sh

```
@bash-scripting

Crie o script scripts/create-pr.sh para abrir PR ao final de cada fase do playbook.

Uso: bash scripts/create-pr.sh {numero-da-fase}
Exemplo: bash scripts/create-pr.sh 0

Pre-requisito: gh (GitHub CLI) instalado e autenticado.
   sudo apt install gh && gh auth login

O script deve:

1. Receber o numero da fase como argumento (0 a 4).

2. Mapa de fases (declare -A):
   0 → "bootstrap"
   1 → "descoberta"
   2 → "ingestao"
   3 → "busca-chat"
   4 → "polish"

3. Mapa de titulos:
   0 → "Fase 0 — Bootstrap: ambiente, Docker e dependencias"
   1 → "Fase 1 — Descoberta: pipeline RAG e decisoes de chunking"
   2 → "Fase 2 — Ingestao: PDF → chunks → embeddings → pgVector"
   3 → "Fase 3 — Busca + Chat: similarity search e CLI interativo"
   4 → "Fase 4 — Polish: README, validacao e entrega"

4. Mapa de entregaveis (checklist por fase):
   0 → venv ativo, Docker rodando, deps instaladas, .env configurado
   1 → Pipeline RAG entendido, chunking documentado, prompt template projetado
   2 → ingest.py funcional, chunks no pgVector, validacao no banco
   3 → search.py + chat.py, CLI responde + rejeita, grounding OK
   4 → README final, validacao E2E, commit pushed, repo publico

5. Mapa de gates (comando de verificacao):
   0 → "docker compose ps + python -c 'import langchain'"
   1 → "Explicar RAG em 3 frases"
   2 → "python src/ingest.py + SELECT count(*) FROM langchain_pg_embedding"
   3 → "python src/chat.py — responde no contexto e rejeita fora"
   4 → "Validacao E2E completa + git push origin main"

6. Fluxo do script:
   a) Validar que o numero da fase esta entre 0 e 4
   b) Definir: BRANCH_ATUAL="fase-{N}-{nome}" e BASE_BRANCH="main"
   c) Verificar se gh esta instalado (command -v gh)
   d) Verificar se ha mudancas nao commitadas:
      - Se sim: git add -A && git commit -m "feat(fase-{N}): {nome} concluida"
   e) git push origin {BRANCH_ATUAL}
   f) Montar PR_TITLE e PR_BODY com entregaveis e gate
   g) gh pr create --title "{PR_TITLE}" --body "{PR_BODY}" --base main --head {BRANCH_ATUAL}
   h) Se fase < 4: criar branch da proxima fase:
      git checkout main
      git checkout -b fase-{N+1}-{proximo_nome}
   i) Printar resumo: PR URL, branch mergeada, proxima fase

Use cores no output (GREEN, YELLOW, BLUE, RED, NC).
Use set -euo pipefail no topo.
Funcoes helper: log_ok(), log_info(), log_warn(), die().

Nao inclua flag --interactive ou --dry-run — manter simples.
Base branch: main (nao develop — projeto simples).

Criterio de sucesso: bash scripts/create-pr.sh 0 abre PR no GitHub.
```

---

### 🖥️ Cursor — Configurar GitFlow com branches por fase

```
@bash-scripting

Configure o GitFlow do projeto para trabalhar com uma branch por fase.

Executar na raiz do projeto:

1. Garantir que estamos no main:
   git checkout main

2. Criar a branch da Fase 0:
   git checkout -b fase-0-bootstrap

3. Confirmar:
   git branch
   → Deve mostrar: main e * fase-0-bootstrap

O fluxo de branches sera:
   fase-0-bootstrap  → PR para main
   fase-1-descoberta → PR para main
   fase-2-ingestao   → PR para main
   fase-3-busca-chat → PR para main
   fase-4-polish     → PR para main

Cada fase trabalha numa branch separada.
Ao final da fase, o script create-pr.sh abre PR para main
e cria a branch da proxima fase automaticamente.

Criterio de sucesso: git branch mostra fase-0-bootstrap como branch ativa.
```

---

### ✅ Gate Fase 0

- [ ] Fork clonado e diretorio correto
- [ ] `which python` aponta para venv/bin/python
- [ ] `pip list | grep langchain` mostra langchain instalado
- [ ] `docker compose ps` mostra postgres running na porta 5432
- [ ] `.env` com API key configurada (OpenAI ou Google)
- [ ] `document.pdf` presente na raiz do projeto
- [ ] `.gitignore` criado (ignora venv, .env, __pycache__)
- [ ] `src/__init__.py` existe (vazio)
- [ ] `scripts/create-pr.sh` criado e executavel

```bash
bash scripts/create-pr.sh 0
```

---

## FASE 1 — Descoberta
**Gate:** Consigo explicar o pipeline RAG em 3 frases sem hesitar.
**Entregaveis:** Entendimento do fluxo · Decisoes de chunking documentadas · Pesquisa de libs validada

---

### 🧠 Claude — Entendimento do pipeline RAG

```
@rag-engineer @architecture-patterns

Explique o pipeline RAG que sera implementado neste projeto, como se fosse para
um engenheiro que nunca trabalhou com embeddings ou busca vetorial.

O projeto e um CLI Python que:
1. Ingere um PDF em um banco PostgreSQL com pgVector
2. Permite busca semantica via terminal
3. Responde perguntas baseado APENAS no conteudo do PDF

Pipeline de Ingestao (Fase 2):
1. PyPDFLoader le o PDF e extrai texto por pagina
2. RecursiveCharacterTextSplitter divide o texto em chunks de 1000 chars com 150 de overlap
3. OpenAIEmbeddings (text-embedding-3-small) converte cada chunk em vetor de 1536 dimensoes
4. PGVector.from_documents() armazena vetores + texto + metadata no PostgreSQL

Pipeline de Busca + Chat (Fase 3):
1. Pergunta do usuario e convertida em embedding pelo mesmo modelo
2. similarity_search_with_score busca os k=10 chunks mais proximos por similaridade coseno
3. Os 10 chunks sao concatenados como CONTEXTO
4. Prompt Template combina CONTEXTO + REGRAS DE GROUNDING + PERGUNTA
5. LLM (gpt-5-nano, temperature=0) gera resposta baseada APENAS no contexto
6. Regras de grounding previnem alucinacao — perguntas fora do contexto sao rejeitadas

Para cada passo explique:
- O que acontece tecnicamente (em linguagem acessivel)
- Por que essa decisao (e nao outra alternativa)
- Qual o impacto se pular ou fazer errado
```

---

### 🧠 Claude — Decisoes de chunking

```
@rag-engineer @llm-application-architect

Documente as decisoes de chunking para o projeto de busca semantica.

Parametros que serao usados:
- chunk_size: 1000 caracteres
- chunk_overlap: 150 caracteres
- Splitter: RecursiveCharacterTextSplitter (do langchain-text-splitters)

Para cada parametro responda:

1. chunk_size = 1000 — por que 1000 e nao 500 ou 2000?
   Trade-off: chunks grandes diluem relevancia, pequenos perdem contexto.

2. chunk_overlap = 150 — por que 150?
   Garante que informacoes na fronteira entre chunks nao se percam.

3. Por que RecursiveCharacterTextSplitter e nao CharacterTextSplitter?
   Recursive respeita hierarquia natural (paragrafos → frases → palavras).

4. Quando mudar esses parametros?
   - PDF tecnico denso: chunk_size menor (500-800)
   - PDF narrativo: chunk_size maior (1200-1500)
   - Respostas cortam no meio da frase: aumentar overlap

5. Como o chunk_size afeta o custo?
   Mais chunks = mais chamadas de embedding = mais custo com API.

Formate como documento de decisao que possa ser consultado depois.
```

---

### 🧠 Claude — Design do prompt template (grounding rules)

```
@prompt-engineer @rag-engineer

Projete o prompt template para o chat CLI do projeto de busca semantica.
Este prompt sera usado no src/chat.py (Fase 3) para garantir que a LLM
responda APENAS com base no contexto recuperado do pgVector.

Requisitos obrigatorios:
- temperature=0 para respostas deterministicas
- Sem alucinacao — nunca inventar ou extrapolar
- Perguntas fora do contexto rejeitadas com mensagem padrao fixa

O prompt template deve conter EXATAMENTE 4 secoes nesta ordem:

1. CONTEXTO:
   {contexto}
   → Placeholder que sera preenchido com os top 10 chunks concatenados

2. REGRAS:
   - Responda somente com base no CONTEXTO
   - Se a informacao nao estiver explicitamente no CONTEXTO, responda:
     "Nao tenho informacoes necessarias para responder sua pergunta."
   - Nunca invente ou use conhecimento externo
   - Nunca produza opinioes ou interpretacoes alem do que esta escrito

3. EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
   3 exemplos cobrindo: conhecimento geral, dados ausentes, pedido de opiniao
   Cada um com Pergunta + Resposta fixa de rejeicao

4. PERGUNTA DO USUARIO:
   {pergunta}

Entregue:
- O prompt template completo pronto para usar como string Python
- Explicacao de por que cada secao e necessaria
- O que acontece se remover cada secao
```

---

### 🔍 Gemini — Pesquisa de referencias

```
Preciso de referencias atualizadas para o projeto de busca semantica
com LangChain + pgVector + Python.

Pesquise:
1. LangChain versao mais recente — mudancas de API para PGVector e PyPDFLoader
2. langchain-postgres vs langchain-community PGVector — qual usar?
   (houve breaking changes recentes — preciso saber o import correto)
3. Configuracao do pgVector com Docker (imagem pgvector/pgvector:pg17)
4. similarity_search_with_score vs similarity_search — quando usar cada um
5. Boas praticas para prompt grounding com OpenAI (evitar alucinacao)
6. text-embedding-3-small vs text-embedding-ada-002 — qual usar e por que

Versoes alvo: LangChain 0.3+, langchain-postgres 0.0.12+, Python 3.12
Fontes de 2024 em diante. Priorize documentacao oficial.
```

---

### ✅ Gate Fase 1

- [ ] Voce consegue explicar o pipeline RAG em 3 frases sem consultar os docs
- [ ] Decisoes de chunking documentadas (chunk_size, overlap, splitter)
- [ ] Prompt template projetado com 4 secoes (CONTEXTO, REGRAS, EXEMPLOS, PERGUNTA)
- [ ] Pesquisa do Gemini revisada — versoes de lib e imports confirmados

```bash
bash scripts/create-pr.sh 1
```

---

## FASE 2 — Ingestao do PDF
**Gate:** `python src/ingest.py` executa sem erros e vetores estao no banco.
**Entregaveis:** src/ingest.py funcional · chunks no pgVector · validacao no banco

---

### 🖥️ Cursor — Criar src/ingest.py

```
@pgvector-patterns @rag-engineer

Crie o arquivo src/ingest.py — script de ingestao de PDF no banco vetorial.

Este script le um PDF, divide em chunks, gera embeddings e armazena no PostgreSQL
com pgVector. Sera executado UMA VEZ antes de usar o chat.

Fluxo (ESTA ORDEM E OBRIGATORIA):

1. Carregar variaveis de ambiente:
   from dotenv import load_dotenv
   load_dotenv()

2. Carregar o PDF:
   from langchain_community.document_loaders import PyPDFLoader
   loader = PyPDFLoader("document.pdf")
   documents = loader.load()
   → Retorna List[Document], um por pagina
   → Print: "Paginas carregadas: {len(documents)}"

3. Dividir em chunks:
   from langchain_text_splitters import RecursiveCharacterTextSplitter
   text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=1000,
       chunk_overlap=150,
   )
   chunks = text_splitter.split_documents(documents)
   → Print: "Chunks gerados: {len(chunks)}"

4. Configurar embeddings:
   from langchain_openai import OpenAIEmbeddings
   embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
   → Modelo gera vetores de 1536 dimensoes
   → Alternativa Google (deixar COMENTADO no codigo):
     from langchain_google_genai import GoogleGenerativeAIEmbeddings
     embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

5. Configurar conexao com PostgreSQL:
   CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
   COLLECTION_NAME = "documents"

6. Armazenar no pgVector:
   from langchain_postgres import PGVector
   vector_store = PGVector.from_documents(
       documents=chunks,
       embedding=embeddings,
       connection=CONNECTION_STRING,
       collection_name=COLLECTION_NAME,
       pre_delete_collection=True,
   )
   → pre_delete_collection=True limpa a colecao anterior (permite reingerir sem duplicatas)
   → Print: "Ingestao concluida! {len(chunks)} chunks armazenados no pgVector."

Imports necessarios (todos no topo do arquivo):
- os
- dotenv.load_dotenv
- langchain_community.document_loaders.PyPDFLoader
- langchain_text_splitters.RecursiveCharacterTextSplitter
- langchain_postgres.PGVector
- langchain_openai.OpenAIEmbeddings

O arquivo NAO deve ter funcao main() — e um script direto (executa ao rodar).
NAO inclua argparse ou parametros — o PDF e sempre "document.pdf" na raiz.

Criterio de sucesso: python src/ingest.py executa sem erro e printa as 3 mensagens.
```

---

### 🖥️ Cursor — Validar ingestao no banco

```
@bash-scripting @database-design

Execute a validacao da ingestao do PDF no banco PostgreSQL.

Apos executar python src/ingest.py, rode estes comandos de validacao:

1. Contar chunks armazenados:
   docker compose exec postgres psql -U langchain -d langchain -c \
     "SELECT count(*) FROM langchain_pg_embedding;"
   → Esperado: mesmo numero que o print "Chunks gerados: X" do ingest.py

2. Ver amostra do conteudo (3 primeiros chunks):
   docker compose exec postgres psql -U langchain -d langchain -c \
     "SELECT LEFT(document, 100) as texto, LEFT(cmetadata::text, 50) as metadata FROM langchain_pg_embedding LIMIT 3;"
   → Esperado: texto do PDF + metadata com numero da pagina

3. Verificar dimensao dos vetores:
   docker compose exec postgres psql -U langchain -d langchain -c \
     "SELECT vector_dims(embedding) FROM langchain_pg_embedding LIMIT 1;"
   → Esperado: 1536 (OpenAI text-embedding-3-small) ou 768 (Google)

Se o count for 0:
   - Verificar se docker compose ps mostra postgres running
   - Verificar se .env tem API key valida
   - Verificar se o PDF esta como document.pdf na raiz

Se a dimensao for diferente de 1536:
   - Verificar se o modelo de embeddings esta correto (text-embedding-3-small)
```

---

### ✅ Gate Fase 2

- [ ] `python src/ingest.py` executa sem erros
- [ ] Print mostra: paginas carregadas, chunks gerados, ingestao concluida
- [ ] PDF dividido em chunks de 1000 chars com overlap de 150
- [ ] Embeddings gerados (1536 dimensoes para OpenAI)
- [ ] `SELECT count(*) FROM langchain_pg_embedding` = numero de chunks
- [ ] Metadata dos chunks contem numero da pagina e fonte

```bash
bash scripts/create-pr.sh 2
```

---

## FASE 3 — Busca Semantica + Chat CLI
**Gate:** CLI responde perguntas no contexto e rejeita perguntas fora do contexto.
**Entregaveis:** src/search.py · src/chat.py · CLI interativo funcional

---

### 🖥️ Cursor — Criar src/search.py

```
@pgvector-patterns @rag-engineer

Crie o arquivo src/search.py — modulo de busca semantica no pgVector.

Este modulo conecta ao banco vetorial e busca os chunks mais relevantes
para uma query do usuario. Sera importado pelo chat.py.

Componentes a criar:

1. Carregar variaveis de ambiente:
   from dotenv import load_dotenv
   load_dotenv()

2. Configurar conexao (MESMOS valores do ingest.py — CRITICO):
   CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
   COLLECTION_NAME = "documents"

3. Configurar embeddings (MESMO modelo do ingest.py — CRITICO):
   from langchain_openai import OpenAIEmbeddings
   embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
   → Se o ingest usou text-embedding-3-small, o search DEVE usar o mesmo
   → Alternativa Google (COMENTADO): GoogleGenerativeAIEmbeddings(model="models/embedding-001")

4. Instanciar vector store (conecta ao banco existente — NAO cria nova colecao):
   from langchain_postgres import PGVector
   vector_store = PGVector(
       embeddings=embeddings,
       connection=CONNECTION_STRING,
       collection_name=COLLECTION_NAME,
   )

5. Funcao de busca:
   def search(query: str, k: int = 10):
       """Busca os k documentos mais relevantes para a query."""
       results = vector_store.similarity_search_with_score(query, k=k)
       return results
   → Retorna List[Tuple[Document, float]]
   → Document tem .page_content (texto) e .metadata (pagina, fonte)
   → Score: menor = mais relevante (distancia coseno)

6. Modo standalone (para teste direto):
   if __name__ == "__main__":
       query = input("Digite sua busca: ")
       results = search(query)
       for doc, score in results:
           print(f"\n[Score: {score:.4f}]")
           print(doc.page_content[:200])

Imports necessarios (topo do arquivo):
- os
- dotenv.load_dotenv
- langchain_postgres.PGVector
- langchain_openai.OpenAIEmbeddings

IMPORTANTE: CONNECTION_STRING, COLLECTION_NAME e modelo de embeddings DEVEM ser
identicos ao ingest.py. Se forem diferentes, a busca nao encontra nada.

Criterio de sucesso: python src/search.py retorna 10 resultados com scores.
```

---

### 🖥️ Cursor — Criar src/chat.py

```
@rag-engineer @llm-application-architect

Crie o arquivo src/chat.py — CLI interativo que responde perguntas sobre o PDF.

Este e o ponto de entrada principal do usuario. Combina a busca semantica
do search.py com uma LLM para gerar respostas grounded (sem alucinacao).

Componentes a criar:

1. Imports e setup:
   - from dotenv import load_dotenv; load_dotenv()
   - from search import search (import direto — funciona com python src/chat.py)
   - from langchain_openai import ChatOpenAI
   - Alternativa Google (COMENTADO): from langchain_google_genai import ChatGoogleGenerativeAI

2. Prompt template (variavel PROMPT_TEMPLATE — string com placeholders {contexto} e {pergunta}):
   IMPORTANTE: usar o prompt IDENTICO ao desafio.md (linhas 81-106).

   Secao 1 — CONTEXTO:
   {contexto}

   Secao 2 — REGRAS:
   - Responda somente com base no CONTEXTO.
   - Se a informacao nao estiver explicitamente no CONTEXTO, responda:
     "Nao tenho informacoes necessarias para responder sua pergunta."
   - Nunca invente ou use conhecimento externo.
   - Nunca produza opinioes ou interpretacoes alem do que esta escrito.

   Secao 3 — EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
   3 exemplos com Pergunta e Resposta fixa de rejeicao:
   - Conhecimento geral: "Qual e a capital da Franca?"
   - Dados ausentes: "Quantos clientes temos em 2024?"
   - Opiniao: "Voce acha isso bom ou ruim?"
   Cada um com resposta: "Nao tenho informacoes necessarias para responder sua pergunta."

   Secao 4 — PERGUNTA DO USUARIO:
   {pergunta}
   Seguido de: RESPONDA A "PERGUNTA DO USUARIO"

3. Configurar LLM:
   llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
   → temperature=0 para respostas deterministicas (sem variacao)
   → Alternativa Google (COMENTADO): ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

4. Funcao ask(question: str) -> str:
   - Chama search(question, k=10) para buscar os 10 chunks mais relevantes
   - Concatena os page_content dos chunks como contexto:
     contexto = "\n\n---\n\n".join([doc.page_content for doc, score in results])
   - Monta o prompt: PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)
   - Chama llm.invoke(prompt) e retorna response.content

5. Funcao main():
   - Banner: linha de "=", titulo "Chat com PDF — Busca Semantica + LangChain + pgVector", linha de "="
   - Print: "Digite 'sair' para encerrar."
   - Loop while True:
     - input("PERGUNTA: ").strip()
     - Se question.lower() in ("sair", "exit", "quit"): print("Ate logo!") e break
     - Se vazio: continue
     - response = ask(question)
     - print(f"RESPOSTA: {response}")
     - print linha de "-" como separador

6. Bloco if __name__ == "__main__": main()

IMPORTANTE sobre o import:
   from search import search
   → Import direto (nao usar from src.search — causaria ModuleNotFoundError)
   → Funciona porque python src/chat.py adiciona src/ ao sys.path
   → Executar com: python src/chat.py (como o desafio pede)

Criterio de sucesso:
- python src/chat.py inicia e mostra banner
- Pergunta sobre o PDF → resposta correta
- "Qual e a capital da Franca?" → "Nao tenho informacoes necessarias..."
- "sair" → encerra o chat
```

---

### 🧠 Claude — Revisao do prompt template e grounding

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

Para cada ponto: ✅ OK ou ❌ MELHORIA + sugestao concreta.
```

---

### 🧠 Claude — Code review antes do PR

```
@requesting-code-review

Faca o code review dos arquivos implementados na Fase 3 antes de abrir o PR.

Arquivos para revisao:

src/search.py:
{{COLE_SEARCH_PY}}

src/chat.py:
{{COLE_CHAT_PY}}

Verifique:
1. O modelo de embeddings no search.py e identico ao do ingest.py?
2. CONNECTION_STRING e COLLECTION_NAME consistentes?
3. Prompt template completo com as 4 secoes?
4. temperature=0 configurado?
5. Tratamento de input vazio e comandos de saida?
6. Import correto (from search import search)?
7. Alternativa Google comentada (nao removida)?

Para cada arquivo: ✅ Aprovado ou ❌ Bloqueador + correcao.
Aprovado = pode abrir PR. Bloqueador = corrigir antes.
```

---

### ✅ Gate Fase 3

- [ ] `python src/chat.py` inicia e mostra banner + prompt
- [ ] Pergunta no contexto do PDF → resposta correta baseada no PDF
- [ ] Pergunta fora do contexto → "Nao tenho informacoes necessarias..."
- [ ] Pergunta de opiniao → "Nao tenho informacoes necessarias..."
- [ ] Comando "sair" encerra o chat
- [ ] temperature=0 na LLM (respostas deterministicas)
- [ ] Busca retorna k=10 resultados
- [ ] Modelo de embeddings identico no ingest.py e search.py
- [ ] Code review aprovado (sem bloqueadores)

```bash
bash scripts/create-pr.sh 3
```

---

## FASE 4 — Polish e Entrega
**Gate:** Repositorio publico no GitHub, pronto para avaliacao do MBA.
**Entregaveis:** README final · Codigo revisado · .env seguro · Validacao end-to-end · Commit

---

### 🧠 Claude — README final

```
@readme @doc-coauthoring

Gere o README.md completo para o projeto de Ingestao e Busca Semantica.

Contexto:
- Desafio tecnico do MBA em IA da Full Cycle
- CLI Python que ingere PDF em PostgreSQL com pgVector e permite busca semantica
- Stack: Python 3.12, LangChain, PostgreSQL + pgVector, OpenAI API, Docker Compose
- NAO e uma API web — e um CLI interativo

Secoes obrigatorias:

1. Titulo: "Ingestao e Busca Semantica com LangChain e Postgres"

2. Descricao (1 paragrafo):
   Software que ingere um PDF em um banco PostgreSQL com pgVector e permite
   busca semantica via CLI usando LangChain.

3. Pre-requisitos (lista):
   - Python 3.10+
   - Docker e Docker Compose
   - API Key da OpenAI ou Google Gemini

4. Setup passo a passo:
   - git clone do repositorio
   - Criar e ativar venv (python3 -m venv venv && source venv/bin/activate)
   - pip install -r requirements.txt
   - cp .env.example .env (editar com API key real)
   - Colocar PDF na raiz como document.pdf

5. Execucao (3 comandos — identicos ao desafio.md):
   - docker compose up -d
   - python src/ingest.py
   - python src/chat.py

6. Exemplo de uso:
   - Pergunta no contexto → resposta correta do PDF
   - Pergunta fora do contexto → "Nao tenho informacoes necessarias..."
   Use exemplos realistas baseados no {{CONTEUDO_DO_SEU_PDF}}.

7. Tecnologias (lista):
   Python 3.12, LangChain, PostgreSQL + pgVector, OpenAI API, Docker Compose

Tom: tecnico mas acessivel. O avaliador deve conseguir rodar em 5 minutos.
NAO inclua API keys reais. NAO inclua badges ou CI (projeto simples).
```

---

### 🧠 Claude — Revisao final do codigo

```
@architecture-patterns @rag-engineer

Revise o codigo completo do projeto de busca semantica antes do commit final.

Cole os 3 arquivos abaixo:

src/ingest.py:
{{COLE_INGEST_PY}}

src/search.py:
{{COLE_SEARCH_PY}}

src/chat.py:
{{COLE_CHAT_PY}}

Checklist de revisao:

1. Consistencia:
   - CONNECTION_STRING e COLLECTION_NAME identicos nos 3 arquivos?
   - Modelo de embeddings identico no ingest.py e search.py? (CRITICO)
   - Todos tem load_dotenv() no topo?

2. Seguranca:
   - Nenhuma API key hardcoded?
   - .env esta no .gitignore?

3. Grounding:
   - temperature=0 no chat.py?
   - Prompt template tem as 4 secoes (CONTEXTO, REGRAS, EXEMPLOS, PERGUNTA)?

4. Funcionalidade:
   - ingest.py tem prints informativos em cada etapa?
   - search.py retorna similarity_search_with_score (com score)?
   - chat.py trata input vazio e comandos de saida?
   - Import "from search import search" funciona com python src/chat.py?

5. Limpeza:
   - Sem prints de debug?
   - Sem imports nao utilizados?
   - Alternativa Google comentada (nao removida)?

Para cada ponto: ✅ OK ou ❌ PROBLEMA + correcao exata.
```

---

### 🖥️ Cursor — Validacao end-to-end

```
@verification-before-completion @bash-scripting

Execute a validacao completa do projeto partindo do zero.
Cada passo deve ser executado na sequencia — se um falhar, pare e corrija.

1. Reset completo do banco:
   docker compose down -v
   docker compose up -d
   → Esperar 5 segundos para o banco subir

2. Verificar banco:
   docker compose ps
   → Esperado: postgres running na porta 5432

3. Ingestao:
   python src/ingest.py
   → Esperado: 3 prints (paginas, chunks, concluido)

4. Contar chunks no banco:
   docker compose exec postgres psql -U langchain -d langchain -c \
     "SELECT count(*) FROM langchain_pg_embedding;"
   → Esperado: mesmo numero que o print "Chunks gerados: X"

5. Testar chat com pergunta no contexto:
   Abrir: python src/chat.py
   Digitar uma pergunta sobre o conteudo do PDF
   → Esperado: resposta correta baseada no PDF

6. Testar chat com pergunta FORA do contexto:
   "Qual e a capital da Franca?"
   → Esperado: "Nao tenho informacoes necessarias para responder sua pergunta."

7. Testar comando de saida:
   "sair"
   → Esperado: "Ate logo!" e encerrar

8. Verificar seguranca:
   git status
   → .env NAO deve aparecer (esta no .gitignore)

Se todos passarem, o projeto esta pronto para commit.
```

---

### 🖥️ Cursor — Commit e push final

```
@bash-scripting

Prepare o commit final do projeto para entrega do MBA.

Verificacoes ANTES do commit (executar cada uma):

1. git status
   → Confirmar que .env NAO esta listado
   → Confirmar que .env.example ESTA listado

2. ls src/
   → Confirmar: __init__.py, ingest.py, search.py, chat.py

3. cat .gitignore
   → Confirmar: venv/, .env, __pycache__/ presentes

Se tudo OK, executar:

git add .
git status   (revisar uma ultima vez)

git commit -m "feat: ingestao e busca semantica com LangChain e pgVector

- Ingestao de PDF com PyPDFLoader + RecursiveCharacterTextSplitter
- Embeddings com OpenAI text-embedding-3-small
- Armazenamento vetorial com pgVector no PostgreSQL
- Busca semantica com similarity_search_with_score (k=10)
- CLI interativo com prompt grounded (sem alucinacao)
- Docker Compose para PostgreSQL + pgVector"

git push origin main

Verificacao pos-push:
   git log --oneline -1
   → Confirmar que o commit aparece

ALERTA: se .env estiver no historico do git, remover com:
   git rm --cached .env
   git commit -m "fix: remove .env do tracking"
   git push origin main
```

---

### ✅ Gate Fase 4 — Checklist Final

- [ ] `docker compose up -d` sobe o banco sem erros
- [ ] `python src/ingest.py` ingere o PDF e armazena no pgVector
- [ ] `python src/chat.py` inicia o CLI interativo
- [ ] Perguntas no contexto → respostas corretas baseadas no PDF
- [ ] Perguntas fora do contexto → "Nao tenho informacoes necessarias..."
- [ ] README.md com instrucoes claras de execucao
- [ ] .env.example presente (sem chaves reais)
- [ ] .env no .gitignore (nao versionado)
- [ ] requirements.txt com todas as dependencias
- [ ] Repositorio publico no GitHub
- [ ] Codigo limpo, sem prints de debug
- [ ] Commit feito e pushed

```bash
bash scripts/create-pr.sh 4
```

---

## FASE 5 — Divulgacao no LinkedIn
**Gate:** Artigo publicado + post no feed.
**Entregaveis:** Artigo LinkedIn · Post curto · Screenshot do terminal · Diagramas

---

### 🧠 Claude — Artigo para o LinkedIn

```
@doc-coauthoring

Gere o artigo completo para publicar no LinkedIn sobre o projeto de busca semantica.

Acesse: LinkedIn > "Escrever artigo" (Write article)

Titulo:
"Como construi um sistema de busca semantica com Python, LangChain e pgVector"

Estrutura (cada secao abaixo e uma secao do artigo):

1. O problema (2 paragrafos):
   - PDFs contem informacoes valiosas mas busca por palavra-chave falha
   - Exemplo: "Qual o faturamento?" nao encontra "receita bruta"
   - Busca semantica resolve isso entendendo significado, nao palavras

2. A solucao — busca semantica (2 paragrafos):
   - Embeddings: representacao matematica do significado do texto
   - Similaridade coseno: encontra os trechos mais proximos em significado

3. Arquitetura (fluxo textual + placeholder para diagrama):
   - Ingestao: PDF → PyPDFLoader → Chunks (1000 chars) → Embeddings → pgVector
   - Busca: Pergunta → Embedding → Similaridade → Contexto → LLM → Resposta

4. Stack tecnica (lista com breve explicacao de cada):
   - Python 3.12, LangChain, PostgreSQL + pgVector, OpenAI, Docker Compose

5. O que aprendi (3 pontos com explicacao):
   a) Chunking importa: 1000 chars com 150 overlap como sweet spot
   b) Grounding previne alucinacao: "responda APENAS com base no CONTEXTO"
   c) pgVector e simples: com LangChain, integracao transparente

6. Resultado (1 paragrafo + placeholder para screenshot):
   CLI que responde perguntas sobre qualquer PDF sem inventar informacoes

7. Link do codigo: placeholder [link do GitHub]

8. Hashtags (na ultima linha):
   #Python #LangChain #pgVector #RAG #IA #MachineLearning #MBA #FullCycle
   #BuscaSemantica #Embeddings #PostgreSQL #OpenAI

Tom: tecnico mas acessivel. Deve interessar engenheiros e gestores de tecnologia.
```

---

### 🧠 Claude — Post curto para o feed

```
@doc-coauthoring

Gere o post curto para o feed do LinkedIn (maximo 1300 caracteres).
Publicar DEPOIS do artigo, linkando para ele.

Estrutura:

1. Gancho (1 linha):
   "Acabei de entregar meu desafio do MBA em IA da Full Cycle:"

2. O que faz (3 bullets com seta →):
   → Ingere qualquer PDF em um banco PostgreSQL com vetores
   → Responde perguntas via CLI baseado APENAS no conteudo do documento
   → Rejeita perguntas fora do contexto (zero alucinacao)

3. Insight pessoal (2-3 linhas):
   "O que mais me surpreendeu:
   A diferenca entre busca keyword e semantica e brutal.
   'Qual o faturamento?' encontra a resposta mesmo quando o PDF fala
   em 'receita bruta' — porque o modelo entende o significado."

4. Stack (1 linha):
   Stack: Python 3.12 · LangChain · pgVector · OpenAI · Docker

5. Links (2 linhas):
   Artigo completo: [link do artigo]
   Codigo: [link do GitHub]

6. Hashtags (5-7):
   #Python #LangChain #pgVector #RAG #IA #BuscaSemantica #MBA #FullCycle

Dicas de publicacao (incluir como comentario no final):
- Publicar em dia util (terca a quinta, 8h-10h)
- Adicionar screenshot do terminal (pergunta + resposta)
- Responder comentarios nas primeiras 2 horas
- Marcar @FullCycle no post
```

---

### 🧠 Claude — Diagramas de arquitetura para o artigo

```
@architecture-patterns @doc-coauthoring

Gere diagramas profissionais de arquitetura para usar no artigo do LinkedIn
e no README do GitHub.

Opcao 1 — Mermaid (para GitHub README — renderiza nativamente):

Gere 3 diagramas Mermaid:

Diagrama 1 — Fluxo de Ingestao (flowchart LR):
   document.pdf → PyPDFLoader → RecursiveCharacterTextSplitter (1000 chars, 150 overlap)
   → OpenAI Embeddings (text-embedding-3-small) → PostgreSQL pgVector
   Cores: verde para processamento, azul para banco

Diagrama 2 — Fluxo de Busca RAG (flowchart LR):
   Pergunta do usuario → Embedding da pergunta → similarity_search (k=10)
   → pgVector → Top 10 chunks → Prompt Template (contexto + regras) → LLM (gpt-5-nano) → Resposta
   Cores: verde para usuario, azul para banco, roxo para LLM

Diagrama 3 — Arquitetura Completa (graph TB com 3 subgraphs):
   Subgraph "Fase 1 — Ingestao": PDF → Loader → Splitter → Embeddings → Store
   Subgraph "PostgreSQL + pgVector": tabela langchain_pg_embedding
   Subgraph "Fase 2-3 — Busca + Chat": Usuario → Embeddings → Search ↔ pgVector → Prompt → LLM → Usuario
   pgVector compartilhado entre ingestao e busca

Formato: blocos ```mermaid prontos para colar no README.

Opcao 2 — Prompt para Eraser.io (colar em eraser.io/diagramgpt):
   Texto descritivo do sistema para gerar diagrama com IA.
   Resultado: diagrama visual profissional exportavel como PNG.

Opcao 3 — Prompt para InfraSketch (colar em infrasketch.net):
   Texto descritivo para gerar diagrama + documento de design.

Para Eraser e InfraSketch, gere o texto pronto para colar — nao o diagrama em si.
O usuario cola no site e a ferramenta gera visualmente.

> Guia completo de ferramentas: veja guia-diagramas-arquitetura.md
```

---

### ✅ Gate Fase 5

- [ ] Artigo publicado no LinkedIn com titulo, arquitetura, stack e aprendizados
- [ ] Post curto publicado no feed linkando o artigo
- [ ] Screenshot do terminal incluido (pergunta no contexto + fora do contexto)
- [ ] Link do repositorio GitHub no artigo e no post
- [ ] Hashtags relevantes (5-7)
- [ ] Full Cycle marcada no post
- [ ] Respondeu comentarios nas primeiras 2 horas

---

## Resumo de Comandos por Fase

| Fase | Comando de verificacao | Gate principal |
|------|----------------------|----------------|
| 0 | `docker compose ps` + `pip list` | Ambiente funcionando |
| 1 | Leitura dos docs | Explicar RAG em 3 frases |
| 2 | `python src/ingest.py` | Chunks no pgVector |
| 3 | `python src/chat.py` | CLI responde + rejeita |
| 4 | Validacao end-to-end | Repositorio publico |
| 5 | LinkedIn | Artigo + post publicados |

---

## Apendice — Referencia Rapida

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker compose up -d

# Executar
python src/ingest.py        # Ingestao do PDF
python src/chat.py          # Chat interativo
python src/search.py        # Busca standalone (teste)

# Banco de dados
docker compose exec postgres psql -U langchain -d langchain
SELECT count(*) FROM langchain_pg_embedding;  -- ver chunks
docker compose down -v                         -- reset completo

# Limpar e reingerir
docker compose down -v && docker compose up -d
python src/ingest.py
```

---

## Apendice — Troubleshooting

| Problema | Solucao |
|---|---|
| `ModuleNotFoundError: langchain_postgres` | `pip install langchain-postgres` |
| `psycopg2` nao instala | `pip install psycopg2-binary` |
| Conexao recusada ao PostgreSQL | Verificar `docker compose ps` — banco esta rodando? |
| `OPENAI_API_KEY not set` | Verificar `.env` e `load_dotenv()` no topo do script |
| Import error no chat.py | Usar `from search import search` (nao `from src.search`) |
| Chunks com pouco contexto | Aumentar `chunk_size` ou diminuir `chunk_overlap` |
| Respostas inventadas (alucinacao) | Verificar `temperature=0` na LLM e prompt template correto |

---

## Apendice — Stack de Referencia

| Componente | Tecnologia | Versao |
|-----------|-----------|--------|
| Linguagem | Python | 3.12 |
| Orquestracao LLM | LangChain | 0.3+ |
| Embeddings | OpenAI text-embedding-3-small | 1536 dim |
| LLM | OpenAI gpt-5-nano | temperature=0 |
| Banco Vetorial | PostgreSQL + pgVector | pg17 |
| Loader de PDF | PyPDFLoader (pypdf) | 4.0+ |
| Splitter | RecursiveCharacterTextSplitter | 1000/150 |
| Container | Docker Compose | pgvector/pgvector:pg17 |
| Variaveis | python-dotenv | 1.0+ |

---

## Apendice — Skills Utilizadas neste Playbook

| Skill | Tipo | Onde usada |
|---|---|---|
| `@rag-engineer` | Global (antigravity) | Pipeline RAG, chunking, busca |
| `@pgvector-patterns` | Custom (ProjectForge) | pgVector, embeddings, ingestao |
| `@llm-application-architect` | Custom (ProjectForge) | Arquitetura LLM, prompt design |
| `@prompt-engineer` | Global (antigravity) | Prompt template, grounding rules |
| `@doc-coauthoring` | Global (antigravity) | README, artigo LinkedIn |
| `@architecture-patterns` | Global (antigravity) | Revisao de arquitetura |
| `@bash-scripting` | Global (antigravity) | Docker, scripts, validacao |
| `@database-design` | Global (antigravity) | pgVector, validacao no banco |
| `@readme` | Global (antigravity) | README final |
| `@verification-before-completion` | Global (antigravity) | Validacao end-to-end |
| `@requesting-code-review` | Global (antigravity) | Code review antes de PR |

---

*Prompt Playbook — Desafio MBA IA · Full Cycle · Wesley Taumaturgo · 2026-03*
