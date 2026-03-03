from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
COLLECTION_NAME = "documents"

# Alternativa Google (descomente para usar):
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

loader = PyPDFLoader("document.pdf")
documents = loader.load()
print(f"Paginas carregadas: {len(documents)}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)
chunks = text_splitter.split_documents(documents)
print(f"Chunks gerados: {len(chunks)}")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
    pre_delete_collection=True,
)
print(f"Ingestao concluida! {len(chunks)} chunks armazenados no pgVector.")
