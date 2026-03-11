# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema de **Ingestão e Busca Semântica** utilizando LangChain, PostgreSQL com pgVector e modelos de linguagem (OpenAI ou Google Gemini). O sistema lê um PDF, armazena seus conteúdos como vetores de embeddings e responde perguntas via CLI com base exclusivamente no conteúdo do documento.

## Arquitetura

```
document.pdf → ingest.py → pgVector (PostgreSQL)
                                  ↓
             chat.py → search.py → LLM → RESPOSTA
```

1. **Ingestão** (`src/ingest.py`): lê o PDF, divide em chunks de 1000 caracteres (overlap 150), gera embeddings e armazena no PostgreSQL com pgVector.
2. **Busca** (`src/search.py`): vetoriza a pergunta e busca os 10 chunks mais relevantes via similaridade de cosseno.
3. **Chat** (`src/chat.py`): monta o prompt com os chunks encontrados e chama a LLM, que responde apenas com base no contexto do PDF.

## Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- Chave de API da **OpenAI** ou do **Google Gemini** (escolha uma)

## Configuração

### 1. Clonar o repositório e criar o ambiente virtual

```bash
git clone <url-do-repositorio>
cd mba-ia-desafio-ingestao-busca

python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` e preencha **apenas uma** das opções:

```env
# Opção 1 — OpenAI
OPENAI_API_KEY=sk-...

# Opção 2 — Google Gemini
GOOGLE_API_KEY=AIza...
```

> Se optar pelo Gemini, veja a seção [Alternativa com Google Gemini](#alternativa-com-google-gemini) abaixo.

## Ordem de execução

### 1. Subir o banco de dados

```bash
docker compose up -d
```

Isso inicia um container PostgreSQL 17 com a extensão pgVector na porta `5432`.

### 2. Executar a ingestão do PDF

```bash
python src/ingest.py
```

Saída esperada:
```
Paginas carregadas: X
Chunks gerados: Y
Ingestao concluida! Y chunks armazenados no pgVector.
```

### 3. Rodar o chat

```bash
python src/chat.py
```

## Exemplo de uso

```
============================================================
Chat com PDF — Busca Semântica + LangChain + pgVector
============================================================
Digite 'sair' para encerrar.

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
------------------------------------------------------------

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
------------------------------------------------------------

PERGUNTA: sair
Até logo!
```

Perguntas fora do contexto do PDF sempre retornam: `"Não tenho informações necessárias para responder sua pergunta."`

## Tecnologias utilizadas

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Framework IA | LangChain |
| Banco de dados | PostgreSQL 17 + pgVector |
| Infraestrutura | Docker / Docker Compose |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI `gpt-5-nano` |
| Carregamento PDF | `langchain_community.document_loaders.PyPDFLoader` |
| Split de texto | `langchain_text_splitters.RecursiveCharacterTextSplitter` |
| Armazenamento vetorial | `langchain_postgres.PGVector` |

## Alternativa com Google Gemini

Para usar o Google Gemini em vez da OpenAI, descomente as linhas marcadas como `# Alternativa Google` em cada script e comente as linhas correspondentes da OpenAI:

**`src/ingest.py`**:
```python
# from langchain_openai import OpenAIEmbeddings
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
```

**`src/search.py`**: mesma substituição de embeddings acima.

**`src/chat.py`**:
```python
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
```

Certifique-se de que o `.env` contém `GOOGLE_API_KEY` preenchido.

## Estrutura do projeto

```
├── docker-compose.yml     # PostgreSQL + pgVector
├── requirements.txt       # Dependências Python
├── .env.example           # Template de variáveis de ambiente
├── src/
│   ├── ingest.py          # Ingestão do PDF no banco vetorial
│   ├── search.py          # Busca semântica por similaridade
│   └── chat.py            # CLI interativo com LLM
├── document.pdf           # PDF para ingestão
└── README.md
```
