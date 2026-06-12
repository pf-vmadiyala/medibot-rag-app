from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from pathlib import Path
from rag.config import DB_PATH, COLLECTION_NAME
import atexit


client = QdrantClient(path=str(DB_PATH))
atexit.register(client.close) # Registers clean shutdown of Qdrant client, otherwise a warning is thrown - ImportError: sys.meta_path is None, Python is likely shutting down

# Configuring both dense and sparse in the same collection, 
# WE are telling Qdrant to store a dense semantic vector and a sparse keyword vector side-by-side for every chunk. 
# This makes a single-query hybrid search in Qdrant 

def initialize_collection():
    # Check if collection exists and create if not
    if not client.collection_exists(COLLECTION_NAME):
        # CReating collection with dense and sparse vectors
        client.create_collection(
            collection_name=COLLECTION_NAME,
            # Dense vector configuration
            vectors_config = {
                "dense": models.VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config = {
                "sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(
                        on_disk=False
                    )
                )
            }
        )
    print("Collection initialized")

def upsert_points(points):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )
    print("Points upserted")

#Automatically initialize the collection on load
initialize_collection()