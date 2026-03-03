from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
COLLECTION_NAME = "documents"

# Alternativa Google (descomente para usar):
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = PGVector(
    embeddings=embeddings,
    connection=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
)


def search(query: str, k: int = 10):
    """Busca os k documentos mais relevantes para a query."""
    results = vector_store.similarity_search_with_score(query, k=k)
    return results


if __name__ == "__main__":
    query = input("Digite sua busca: ")
    results = search(query)
    for doc, score in results:
        print(f"\n[Score: {score:.4f}]")
        print(doc.page_content[:200])
