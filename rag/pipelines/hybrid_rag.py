import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from rag.retrieval.hybrid import hybrid_search
from rag.retrieval.reranker import reranker

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)

def hybrid_rag_chain(query:str, role:str):
    results = hybrid_search(query, role, limit=10)

    if not results:
        return {
            "answer": "I'm sorry, I couldn't find any relevant information to answer your question"
        }

    reranked_results = reranker(query, results)

    context_blocks = []
    for r in reranked_results:
        doc_name = r["metadata"].get("source_document", "Unknown Document")
        section = r["metadata"].get("section_title", "General")

        context_blocks.append(
            f"Document: {doc_name} | Section: {section} \n Content: {r['content']}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    system_prompt = f"""You are MediBot, an intelligent internal assistant for MediAssist Health Network.
    Answer the user's question as accurately as possible using ONLY the provided context blocks. 
    If the context does not contain the answer or is not relevant, clearly state that you do not know. 
    Do not make up facts or use outside knowledge. 
    Context Chunks:
    {context}
    Question: {query}
    Answer:"""

    final_answer = llm.invoke(system_prompt).content

    sources = []
    seen_sources = set()
    for r in reranked_results:
        source_key = (r["metadata"].get("source_document"), r["metadata"].get("section_title"))
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                "source_document": r["metadata"].get("source_document"),
                "section_title": r["metadata"].get("section_title"),
                "collection": r["metadata"].get("collection")
            })
            
    return {
        "answer": final_answer,
        "sources": sources,
        "retrieval_type": "hybrid_rag",
        "role": role
    }


if __name__ == "__main__":
    test_queries = [
        ("What is the leave policy?", "nurse")
    ]
    
    for q_text, user_role in test_queries:
        print(f"\n=== Question: {q_text} | Role: {user_role} ===")
        output = hybrid_rag_pipeline(q_text, role=user_role)
        print(f"Answer: {output['answer']}")
        print(f"Sources: {output['sources']}")
    

    