import hashlib
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma

data_dir = "./data"
all_docs = []

print("📄 Scanning PDFs in /data...")
for file in os.listdir(data_dir):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(data_dir, file)
        print(f"   -> Loading {file}...")
        loader = PyPDFLoader(pdf_path)
        all_docs.extend(loader.load())

print(f"✅ Loaded {len(all_docs)} total page(s). Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(all_docs)

print("⚡ Generating Embeddings using FastEmbed (Bypassing DLL Block)...")
# FastEmbed does not use scikit-learn Cython BLAS DLLs
embedding_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

vector_db = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)

print("🎉 Success! Vector DB built at ./chroma_db")
# ==========================================
# NEW FEATURE: DOCUMENT INGESTION TRACKER
# ==========================================
import time

def track_document_ingestion(file_path):
    """
    Simulates step-by-step PDF parsing and vector indexing with timing metrics.
    """
    if not os.path.exists(file_path):
        return {"status": "FAILED", "reason": "File not found"}
        
    start_time = time.time()
    file_size_kb = os.path.getsize(file_path) / 1024
    
    # Simulating processing stages
    time.sleep(0.5) 
    processing_time = round(time.time() - start_time, 2)
    
    return {
        "status": "SUCCESS",
        "file_name": os.path.basename(file_path),
        "size_kb": round(file_size_kb, 1),
        "latency_sec": processing_time
    }
# ==========================================
# NEW FEATURE: BULK DATA DIRECTORY SCANNER
# ==========================================
def list_available_policy_documents(data_dir="data"):
    """
    Scans data/ folder and returns a list of candidate PDF/TXT files ready for vector ingestion.
    """
    if not os.path.exists(data_dir):
        return []
        
    supported_extensions = (".pdf", ".txt", ".md")
    files = [f for f in os.listdir(data_dir) if f.lower().endswith(supported_extensions)]
    
    doc_details = []
    for f in files:
        full_path = os.path.join(data_dir, f)
        size_kb = round(os.path.getsize(full_path) / 1024, 1)
        doc_details.append({"filename": f, "size_kb": size_kb})
        
    return doc_details
# ==========================================
# NEW FEATURE: INGESTION HEALTH VERIFIER
# ==========================================
def verify_vector_db_health(chroma_dir="chroma_db"):
    """
    Verifies vector database directory existence and SQLite storage files.
    """
    if not os.path.exists(chroma_dir):
        return {"status": "UNINITIALIZED", "reason": "Directory missing"}
        
    sqlite_file = os.path.join(chroma_dir, "chroma.sqlite3")
    if not os.path.exists(sqlite_file):
        return {"status": "CORRUPTED", "reason": "chroma.sqlite3 missing"}
        
    return {"status": "HEALTHY", "path": chroma_dir}
# ==========================================
# NEW FEATURE: DOCUMENT HASH DUPLICATION CHECK
# ==========================================
def calculate_file_hash(filepath: str) -> str:
    """
    Computes MD5 hash of policy documents to check for content duplicates.
    """
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()