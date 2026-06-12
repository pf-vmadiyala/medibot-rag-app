from pathlib import Path

# Ingestion Directories
RAG_ROOT = Path(__file__).resolve().parent
BASE_DIR = RAG_ROOT / "data/documents"
DB_PATH = RAG_ROOT / "data/db/qdrant_storage"
SQLITE_DB_PATH = RAG_ROOT / "data/db/mediassist.db"

# Qdrant Config
COLLECTION_NAME = "medibot"

# Embedding Models
DENSE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SPARSE_EMBEDDING_MODEL = "Qdrant/bm25"  # Standard, highly optimized local BM25 model

# Chunker Config
MAX_TOKENS = 256
OVERLAP = 32
