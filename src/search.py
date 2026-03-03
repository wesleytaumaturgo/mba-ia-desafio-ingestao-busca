"""
Módulo de busca semântica no pgVector.
Conecta ao banco vetorial e retorna os chunks mais relevantes para uma query.
"""
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

# Alternativa Google (descomente para usar):
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
COLLECTION_NAME = "documents"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = PGVector(
    embeddings=embeddings,
    connection=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
)


def search(query: str, k: int = 10):
    """Busca os k documentos mais relevantes para a query.
    Retorna List[Tuple[Document, float]]. Score menor = mais relevante (distância cosseno).
    """
    results = vector_store.similarity_search_with_score(query, k=k)
    return results


if __name__ == "__main__":
    query = input("Digite sua busca: ")
    results = search(query)
    for doc, score in results:
        print(f"\n[Score: {score:.4f}]")
        print(doc.page_content[:200])
