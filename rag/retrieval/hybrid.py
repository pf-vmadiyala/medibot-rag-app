from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding, SparseTextEmbedding
from rag.config import DB_PATH, COLLECTION_NAME, DENSE_EMBEDDING_MODEL, SPARSE_EMBEDDING_MODEL
import atexit

client = QdrantClient(path=DB_PATH)
atexit.register(client.close)

dense_model = TextEmbedding(DENSE_EMBEDDING_MODEL)
sparse_model = SparseTextEmbedding(SPARSE_EMBEDDING_MODEL)

def hybrid_search(query: str, role: str, limit: int = 10):

    # Create Query Vectors
    dense_query_vector = list(dense_model.query_embed(query))[0].tolist()
    sparse_query_obj = list(sparse_model.query_embed(query))[0]
    sparse_query_vector = models.SparseVector(
        indices=sparse_query_obj.indices.tolist(),
        values=sparse_query_obj.values.tolist()
    )
    
    #RBAC Filter check the user roles exists within the chunk's allowed roles
    rbac_filter = models.Filter(
        must=[
            models.FieldCondition(
            key="metadata.access_roles",
            match=models.MatchValue(value=role.lower())
        )]
    )

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=dense_query_vector,
                using="dense",
                limit=limit
            ),
            models.Prefetch(
                query=sparse_query_vector,
                using="sparse",
                limit=limit
            )
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        query_filter=rbac_filter,
        limit=limit,
    )

    results = []
    for point in response.points:
        results.append({
            "id": point.id,
            "score": point.score,
            "content": point.payload.get("content", ""),
            "metadata": point.payload.get("metadata", {})
        })
    return results

