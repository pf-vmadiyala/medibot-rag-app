from transformers import AutoTokenizer
from docling.chunking import HybridChunker
from langchain_huggingface import HuggingFaceEmbeddings
from rag.loading.document_loader import load_documents
from rag.config import DENSE_EMBEDDING_MODEL, MAX_TOKENS, OVERLAP
from pathlib import Path

tokenizer = AutoTokenizer.from_pretrained(DENSE_EMBEDDING_MODEL)

def chunk_documents(loaded_docs):

    all_chunks = []
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_TOKENS,
        overlap=OVERLAP,
        merge_peers=True,
        
    )
    print(f"Chunking {len(loaded_docs)} documents...")
    for doc in loaded_docs:
        print(f"Processing doc: {doc['metadata']['source_document']}")
        doc_chunks_iterator = chunker.chunk(doc["content"])

        for chunk in doc_chunks_iterator:
            headings = chunk.meta.headings
            print(headings)
            section_title = headings[-1] if headings else "No heading"
            print(section_title)
            contextualized_text = f"Section: {section_title}\n\n{chunk.text}"
            print(contextualized_text)
            chunk_type = "text"

            for item in chunk.meta.doc_items:
                label = str(item.label).lower()

                if "table" in label:
                    chunk_type = "table"
                    break
                elif "text" in label or "list_item" in label:
                    chunk_type = "text"
                elif "header" in label or "title" in label:
                    chunk_type = "heading"
                elif "code" in label:
                    chunk_type = "code"
            # Create a Chunk Payload combining all the above info

            chunk_payload = {
                "content": contextualized_text,
                "metadata": {
                    "source_document": doc["metadata"]["source_document"],
                    "collection": doc["metadata"]["collection"],
                    "access_roles": doc["metadata"]["access_roles"],
                    "section_title": section_title,
                    "chunk_type": chunk_type,
                }
            }
            print(f"Chunk payload: {chunk_payload}")
            all_chunks.append(chunk_payload)
    return all_chunks
                    

# A single chunk can contain multiple items. For example, a chunk might contain:

# A paragraph (text)
# A table (table)
# A footnote (text)
# If we didn't use break, the loop would continue running after finding the table. When it reaches the footnote at the end, it would overwrite chunk_type back to "text". By breaking immediately, we lock the chunk type to "table".            

# base_dir = Path(__file__).resolve().parents[1] / "data/documents"
# if __name__ == "__main__":
#     loaded_docs = load_documents(base_dir)
#     chunk_documents([loaded_docs[11]])
        

    