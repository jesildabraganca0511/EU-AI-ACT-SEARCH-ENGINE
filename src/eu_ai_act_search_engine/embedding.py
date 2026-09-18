import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT=Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "eu_ai_output_chunked.json"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  
CHROMA_PATH= PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "chroma_db"
COLLECTION_NAME = "eu_ai_act_articles"

def load_chunks(path):
    with open(path,"r",encoding="utf-8") as f:
        chunks=json.load(f)

    return chunks


def embed_store_db(chunks, embedding_model_name=EMBEDDING_MODEL_NAME, chroma_path=CHROMA_PATH, collection_name=COLLECTION_NAME):
    print(f"Embedding and storing {len(chunks)} chunks into ChromaDB...")
    model=SentenceTransformer(embedding_model_name)
    client=chromadb.PersistentClient(path=str(chroma_path))

    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception as e:
        print(f"No existing collection '{collection_name}' to delete. Proceeding to create a new one.") 

    collection=client.create_collection(name=collection_name)
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    texts=[chunk["text"] for chunk in chunks]
    metadatas=[{
        "article_number": chunk["article_number"],
        "article_title": chunk["article_title"],
        "chunk_index": chunk["chunk_index"],
    } for chunk in chunks]  

    embedding=model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embedding    
    )

    return collection


if __name__=="__main__":
    chunks=load_chunks(INPUT_PATH)
    collection=embed_store_db(chunks)
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)


    test_query = "What are the requirements for high-risk AI systems?"
    query_embedding = model.encode([test_query]).tolist()
 
    results = collection.query(query_embeddings=query_embedding, n_results=1)
    print("\nSanity check retrieval:")
    print(f"Query: {test_query}")
    print(f"Top match: {results['metadatas'][0][0]['article_number']} - "
          f"{results['metadatas'][0][0]['article_title']}")
    print(results['documents'][0][0][:200])
 
