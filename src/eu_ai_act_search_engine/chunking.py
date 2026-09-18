import json

from anyio import Path

PROJECT_ROOT=Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "eu_ai_output.json"
OUTPUT_PATH = PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "eu_ai_output_chunked.json"



def chunk_text(text,chunk_size=1000,overlap=100):
    chunks=[]


    if text is None or len(text)==0:
        return chunks

    else:
        if len(text) <= chunk_size:
            return [text]

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            start += chunk_size - overlap
        
            return chunks


def chunk_articles(articles):
    chunked_articles=[]
    for article in articles:
        text=chunk_text(article["text"])


        for i,piece in enumerate(text):
            chunked_articles.append({
                "text": piece,
                "article_number": article["article_number"],
                "article_title": article["article_title"],
                "chunk_index": i,           # position within this article
                "total_chunks_in_article": len(text),
            })


    return chunked_articles



if __name__=="__main__":
    with open(INPUT_PATH,"r", encoding="utf-8") as f:
        articles=json.load(f)
        print(f"Loaded {len(articles)} articles.")
 
    chunks = chunk_articles(articles)
    print(f"Split into {len(chunks)} chunks.")
 
    if chunks:
        print("\nFirst chunk example:")
        print(chunks[0]["text"][:200])
        print(f"Article: {chunks[0]['article_number']} - {chunks[0]['article_title']}")
        print(f"Chunk {chunks[0]['chunk_index'] + 1} of {chunks[0]['total_chunks_in_article']}")
 
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
 
    print(f"\nSaved {len(chunks)} chunks to {OUTPUT_PATH}")
 
