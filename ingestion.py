import re
import json
import pdfplumber
import requests
from langchain_community.document_loaders import PyPDFLoader




PDF_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32024R1689"
LOCAL_FILE= None
LOCAL_PATH="eu_ai_act.pdf"
OUTPUT_PATH = "eu_ai_output.json"


def get_pdf():
    if LOCAL_FILE:
        return LOCAL_FILE

    
    print("Downloading AI Act PDF from EUR-Lex...")
    response=requests.get(PDF_URL,timeout=300)
    response.raise_for_status()
    with open(LOCAL_PATH, 'wb') as f:
        f.write(response.content)
    return LOCAL_PATH


def extract_clean_text(pdf_path):
    footer_patterns = [
        r"OJ L,? 12\.7\.2024 EN",
        r"EN OJ L,? 12\.7\.2024",
        r"ELI: http://data\.europa\.eu/eli/reg/2024/1689/oj",
        r"\d+/144",  # page number like "7/144"
    ]

    loader=PyPDFLoader(pdf_path)
    documents=loader.load()
    print(f"Loaded {len(documents)} pages from the PDF.")


    text_list=[]
    for doc in documents:
        text=doc.page_content
        for pattern in footer_patterns:
            text=re.sub(pattern, '', text)
        text_list.append(text.strip())

    full_text= "\n".join(text_list)



    return full_text



def chunk_text(full_text):

    article_pattern = re.compile(r"^Article (\d+)\s*$", re.MULTILINE)

    matches=list(article_pattern.finditer(full_text))
    articles=[]

    for i,match in enumerate(matches):
        article_number=match.group(1)
        start_index=match.end()
        end_index=matches[i+1].start() if i+1<len(matches) else len(full_text)


        article_text=full_text[start_index:end_index].strip()

        lines=article_text.split("\n",1)
        article_title = lines[0].strip() if lines else ""
        article_body = lines[1].strip() if len(lines) > 1 else ""

        articles.append({
            "article_number": f"Article {article_number}",
            "article_title": article_title,
            "text": article_body,
        })
 
    return articles

def split_into_annexes(annex_text):
    annex_pattern = re.compile(r"^ANNEX ([IVXLC]+)\s*$", re.MULTILINE)
    matches=list(annex_pattern.finditer(annex_text))

    annexes=[]

    for i,match in enumerate(matches):
        annex_number=match.group(1)
        start_index=match.start()
        end_index=matches[i+1].start() if i+1<len(matches) else len(annex_text)

        annex_content=annex_text[start_index:end_index].strip()

        lines=annex_content.split("\n",1)
        annex_title = lines[0].strip() if lines else ""
        annex_body = lines[1].strip() if len(lines) > 1 else ""     

        annexes.append({
            "article_number": f"Annex {annex_number}",
            "article_title": annex_title,
            "text": annex_body,
        })          

    return annexes


if __name__ == "__main__":
    pdf_path = get_pdf()
    full_text = extract_clean_text(pdf_path)
    annex_start = full_text.find("ANNEX I")

    if annex_start== -1:
        print("did not find annexure, using full text")
        body_text,annex_text=full_text,""

    else:
        annex_text=full_text[annex_start:]
        body_text=full_text[:annex_start]


    articles = chunk_text(body_text)
    annexes = split_into_annexes(annex_text)
    all_sections = articles + annexes
 
    print(f"Found {len(articles)} articles (expected 113).")
    print(f"Found {len(annexes)} annexes (expected 13).")
    print("First article found:", articles[0]["article_number"], "-", articles[0]["article_title"])
    if annexes:
        print("First annex found:", annexes[0]["article_number"], "-", annexes[0]["article_title"])
 
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_sections, f, indent=2, ensure_ascii=False)
 
    print(f"Saved {len(all_sections)} sections (articles + annexes) to {OUTPUT_PATH}")
 









