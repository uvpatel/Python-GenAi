
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports (latest structure)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
import os

# Load environment variables
load_dotenv()

# =========================
# 1. Load PDF
# =========================
pdf_path = Path(__file__).parent / "nodejs.pdf"

loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()

print("Sample document:\n")
print(docs[0])

# =========================
# 2. Split into chunks
# =========================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents=docs)

print(f"\nTotal chunks created: {len(chunks)}")

# =========================
# 3. Create Embeddings (Gemini)
# =========================
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"
)

# =========================
# 4. Store in Qdrant
# =========================
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_rag"
)

print("\nIndexing of documents done...")

# =========================
# 5. Create Retriever
# =========================
retriever = vector_store.as_retriever()

# =========================
# 6. LLM (Gemini Chat Model)
# =========================
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.3,
    api_key=os.getenv("GEMINI_API_KEY"),
)

# =========================
# 7. Query Loop (RAG)
# =========================
print("\nAsk questions about your PDF (type 'exit' to quit)\n")

while True:
    query = input("You: ")
    
    if query.lower() == "exit":
        break

    # Retrieve relevant chunks
    relevant_docs = retriever.get_relevant_documents(query)

    # Combine context
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Create prompt
    prompt = f"""
Answer the question based only on the context below.

Context:
{context}

Question:
{query}
"""

    # Get response
    response = llm.invoke(prompt)

    print("\nAnswer:")
    print(response.content)
    print("\n" + "="*50 + "\n")