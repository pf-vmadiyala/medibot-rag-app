from fastembed import TextEmbedding, SparseTextEmbedding
from qdrant_client import models
from pathlib import Path

from rag.loading.document_loader import load_documents
from rag.indexing.chunker import chunk_documents
from rag.config import DENSE_EMBEDDING_MODEL, SPARSE_EMBEDDING_MODEL, BASE_DIR
from rag.db.qdrant_client import upsert_points

def prepare_chunks(base_dir: Path):
    docs = load_documents(base_dir)
    chunks = chunk_documents(docs)
    return chunks

def embed_and_upsert_chunks(chunks):
    print("loading the embedding models")
    dense_model = TextEmbedding(model_name=DENSE_EMBEDDING_MODEL)
    sparse_model = SparseTextEmbedding(model_name=SPARSE_EMBEDDING_MODEL)

    chunk_texts = [c["content"] for c in chunks]

    print("Generating dense embeddings")
    dense_embeddings = list(dense_model.embed(chunk_texts))
    print("Generating sparse embeddings")
    sparse_embeddings = list(sparse_model.embed(chunk_texts))
    
    # Create points
    points = []
    for i, chunk in enumerate(chunks):
        point = models.PointStruct(
            id = i,
            vector={
                "dense": dense_embeddings[i].tolist(),
                "sparse": models.SparseVector(
                    indices=sparse_embeddings[i].indices.tolist(),
                    values=sparse_embeddings[i].values.tolist(),
                )
            },
            payload={
                "content": chunk["content"],
                "metadata": chunk["metadata"]
            }
        )
        points.append(point)
    upsert_points(points)

def main():
    print("Starting ingestion pipeline...")
    chunks = prepare_chunks(BASE_DIR)
    print(f"Prepared {len(chunks)} total chunks.")
    embed_and_upsert_chunks(chunks)
    print("Ingestion pipeline finished successfully!")


if __name__ == "__main__":
    main()

    
