import hashlib
<<<<<<< HEAD
=======
import json
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
import os
import shutil
import time
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
<<<<<<< HEAD
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def load_policy_documents():
    documents = []

=======

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = BASE_DIR / "policy_index.json"
CHROMA_DIR = BASE_DIR / "chroma_db"


def _clean(text):
    return " ".join((text or "").split())


def _chunk_text(text, source, page_no=None, chunk_size=1100, overlap=160):
    words = _clean(text).split()
    chunks = []
    start = 0
    while start < len(words):
        piece = " ".join(words[start:start + chunk_size])
        chunks.append({"text": piece, "source": source, "page": page_no})
        if start + chunk_size >= len(words):
            break
        start += max(1, chunk_size - overlap)
    return chunks


def load_policy_documents():
    chunks = []
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    for path in sorted(DATA_DIR.iterdir()):
        suffix = path.suffix.lower()
<<<<<<< HEAD

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
=======
        try:
            if suffix == ".pdf":
                print(f"   -> Loading PDF: {path.name}")
                for page_no, doc in enumerate(PyPDFLoader(str(path)).load(), 1):
                    text = _clean(doc.page_content)
                    if text:
                        chunks.extend(_chunk_text(text, path.name, page_no))
            elif suffix in {".txt", ".md"}:
                print(f"   -> Loading text: {path.name}")
                text = TextLoader(str(path), encoding="utf-8").load()[0].page_content
                if _clean(text):
                    chunks.extend(_chunk_text(text, path.name, None))
        except Exception as exc:
            print(f"   ⚠️ Could not read {path.name}: {exc}")

    return chunks


def ingest_documents():
    print("📚 Building Sahakar-Vaani policy index...")
    chunks = load_policy_documents()
    if not chunks:
        raise RuntimeError("No readable PDF, TXT or MD policy documents were found in data/.")

    for item in chunks:
        item["collection"] = "pacs-policy"
        item["indexed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    INDEX_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Created searchable policy index: {INDEX_FILE}")
    print(f"📦 Indexed chunks: {len(chunks)}")

    # Optional Chroma build. The kiosk does not depend on FastEmbed anymore.
    # If sentence-transformers/LangChain embeddings are installed, keep a vector DB too.
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma
        from langchain_core.documents import Document

        if CHROMA_DIR.exists():
            shutil.rmtree(CHROMA_DIR)
        embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        docs = [Document(page_content=x["text"], metadata={"source": x["source"], "page": x["page"]}) for x in chunks]
        Chroma.from_documents(
            documents=docs,
            embedding=embedding,
            persist_directory=str(CHROMA_DIR),
            collection_name="pacs_policy",
        )
        print("✅ Optional Chroma vector database rebuilt successfully.")
    except Exception as exc:
        print("ℹ️ Chroma vector index was not built, but the local policy index is ready.")
        print(f"   Reason: {exc}")

    return len(chunks)
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2


def list_available_policy_documents(data_dir="data"):
    directory = BASE_DIR / data_dir
    if not directory.exists():
        return []
<<<<<<< HEAD

    supported = {".pdf", ".txt", ".md"}
    result = []

    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in supported:
            result.append({
                "filename": path.name,
                "size_kb": round(path.stat().st_size / 1024, 1),
            })

=======
    result = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in {".pdf", ".txt", ".md"}:
            result.append({"filename": path.name, "size_kb": round(path.stat().st_size / 1024, 1)})
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
    return result


def verify_vector_db_health(chroma_dir=None):
    directory = Path(chroma_dir) if chroma_dir else CHROMA_DIR
<<<<<<< HEAD
    sqlite_file = directory / "chroma.sqlite3"

    if not directory.exists():
        return {"status": "UNINITIALIZED", "reason": "Directory missing"}

    if not sqlite_file.exists():
        return {"status": "CORRUPTED", "reason": "chroma.sqlite3 missing"}

    return {"status": "HEALTHY", "path": str(directory)}
=======
    if (directory / "chroma.sqlite3").exists():
        return {"status": "HEALTHY", "path": str(directory)}
    if INDEX_FILE.exists():
        return {"status": "POLICY_INDEX_READY", "path": str(INDEX_FILE)}
    return {"status": "UNINITIALIZED", "reason": "No policy index found"}
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2


def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
<<<<<<< HEAD
        while True:
            buf = f.read(65536)
            if not buf:
                break
=======
        for buf in iter(lambda: f.read(65536), b""):
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
            hasher.update(buf)
    return hasher.hexdigest()


def track_document_ingestion(file_path):
    path = Path(file_path)
    if not path.exists():
        return {"status": "FAILED", "reason": "File not found"}
<<<<<<< HEAD

    start = time.time()
    return {
        "status": "SUCCESS",
        "file_name": path.name,
        "size_kb": round(path.stat().st_size / 1024, 1),
        "latency_sec": round(time.time() - start, 3),
    }
=======
    start = time.time()
    return {"status": "SUCCESS", "file_name": path.name, "size_kb": round(path.stat().st_size / 1024, 1), "latency_sec": round(time.time() - start, 3)}
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2


if __name__ == "__main__":
    ingest_documents()
