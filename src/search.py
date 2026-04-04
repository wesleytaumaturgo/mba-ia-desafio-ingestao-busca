import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "documents")

PROMPT_TEMPLATE = """
CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

_vectorstore = None


def _get_embeddings():
    provider = os.getenv("EMBEDDING_PROVIDER", "google" if os.getenv("GOOGLE_API_KEY") else "openai")
    if provider == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        model = os.getenv("GOOGLE_EMBEDDING_MODEL", "gemini-embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model)
    from langchain_openai import OpenAIEmbeddings
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model)


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        from langchain_postgres import PGVector
        _vectorstore = PGVector(
            embeddings=_get_embeddings(),
            collection_name=COLLECTION_NAME,
            connection=DATABASE_URL,
        )
    return _vectorstore


def search_prompt(question: str) -> str:
    vectorstore = _get_vectorstore()
    docs = vectorstore.similarity_search(question, k=10)
    context = "\n\n".join(doc.page_content for doc in docs) if docs else ""
    return PROMPT_TEMPLATE.format(context=context, question=question)
