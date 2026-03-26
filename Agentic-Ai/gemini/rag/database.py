from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv



load_dotenv()


pdf_path=Path(__file__).parent / "nodejs.pdf"

# load this file in python program
loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()
print(docs[0])


# Split the docs into smaller chunks

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
chunk_overlap=400 # prev and next

)


chunks = text_splitter.split_documents(documents=docs)


# vector embeddings

# langchain openai embedding

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",

    
)

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_rag"

)

print("Indexing of  documents done...")





# qudrant 
# languchain