import os
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "documents")


def _get_embeddings():
    provider = os.getenv("EMBEDDING_PROVIDER", "google" if os.getenv("GOOGLE_API_KEY") else "openai")
    if provider == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        model = os.getenv("GOOGLE_EMBEDDING_MODEL", "gemini-embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model)
    from langchain_openai import OpenAIEmbeddings
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model)


def ingest_pdf():
    if not PDF_PATH:
        raise ValueError("PDF_PATH não definido no .env")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não definido no .env")

    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_postgres import PGVector

    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    embeddings = _get_embeddings()

    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        pre_delete_collection=True,
    )

    print(f"Ingeridos {len(chunks)} chunks com sucesso.")


if __name__ == "__main__":
    ingest_pdf()
