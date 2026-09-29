import hashlib
import os
import shutil
import time
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def load_policy_documents():
    documents = []

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    for path in sorted(DATA_DIR.iterdir()):
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            print(f"   -> Loading PDF: {path.name}")
            documents.extend(PyPDFLoader(str(path)).load())

        elif suffix in {".txt", ".md"}:
            print(f"   -> Loading text: {path.name}")
            loader = TextLoader(str(path), encoding="utf-8")
            documents.extend(loader.load())

    return documents


def ingest_documents():
    print("📚 Scanning policy documents in /data...")
    raw_docs = load_policy_documents()

    if not raw_docs:
        raise RuntimeError("No PDF, TXT, or MD policy documents were found.")

    print(f"✅ Loaded {len(raw_docs)} source pages/files.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        separators=["\n\n", "\n", "।", ".", " ", ""],
    )
    docs = splitter.split_documents(raw_docs)

    for doc in docs:
        source = Path(str(doc.metadata.get("source", "unknown"))).name
        doc.metadata["source"] = source
        doc.metadata["collection"] = "pacs-policy"
        doc.metadata["indexed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"✂️ Created {len(docs)} searchable chunks.")

    # chroma_db is a derived index. Rebuild it so the embedding model and
    # document set always match the current data/ directory.
    if CHROMA_DIR.exists():
        print("🧹 Removing old vector index...")
        shutil.rmtree(CHROMA_DIR)

    print(f"🧠 Embedding with {EMBEDDING_MODEL}...")
    embedding_model = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

    Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=str(CHROMA_DIR),
        collection_name="pacs_policy",
    )

    print(f"🎉 Vector database rebuilt at: {CHROMA_DIR}")
    print(f"📦 Indexed chunks: {len(docs)}")
    return len(docs)


def list_available_policy_documents(data_dir="data"):
    directory = BASE_DIR / data_dir
    if not directory.exists():
        return []

    supported = {".pdf", ".txt", ".md"}
    result = []

    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in supported:
            result.append({
                "filename": path.name,
                "size_kb": round(path.stat().st_size / 1024, 1),
            })

    return result


def verify_vector_db_health(chroma_dir=None):
    directory = Path(chroma_dir) if chroma_dir else CHROMA_DIR
    sqlite_file = directory / "chroma.sqlite3"

    if not directory.exists():
        return {"status": "UNINITIALIZED", "reason": "Directory missing"}

    if not sqlite_file.exists():
        return {"status": "CORRUPTED", "reason": "chroma.sqlite3 missing"}

    return {"status": "HEALTHY", "path": str(directory)}


def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            buf = f.read(65536)
            if not buf:
                break
            hasher.update(buf)
    return hasher.hexdigest()


def track_document_ingestion(file_path):
    path = Path(file_path)
    if not path.exists():
        return {"status": "FAILED", "reason": "File not found"}

    start = time.time()
    return {
        "status": "SUCCESS",
        "file_name": path.name,
        "size_kb": round(path.stat().st_size / 1024, 1),
        "latency_sec": round(time.time() - start, 3),
    }


if __name__ == "__main__":
    ingest_documents()
