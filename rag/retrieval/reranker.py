from sentence_transformers import CrossEncoder
from operator import itemgetter

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def reranker(query: str, results: list, top_k: int = 3):
    query_pairs = []
    # Create Query Pairs (query with each result)
    for r in results:
        query_pairs.append([query, r["content"]])
    # Predict scores for the pairs
    scores = model.predict(query_pairs)
    # Update scores for each result
    for i, score in enumerate(scores):
        results[i]["score"] = float(score)
    # Sort results based on score
    sorted_results = sorted(results, key=itemgetter("score"), reverse=True)
    # Return top k results
    return sorted_results[:top_k]   

if __name__ == "__main__":
    from rag.retrieval.hybrid import hybrid_search

    query = "What is the policy for leaves?"
    results = hybrid_search(query, role="nurse", limit=5)
    
    for i, r in enumerate(results):
        print(f"Result {i+1}:\nScore: {r['score']}\nContent: {r['content']}\nMetadata: {r['metadata']}\n")
    print("*" * 100)
    rerank_results = reranker(query, results, top_k=5)
    for i, r in enumerate(rerank_results):
        print(f"Rerank Result {i+1}:\nScore: {r['score']}\nContent: {r['content']}\nMetadata: {r['metadata']}\n")

    
        