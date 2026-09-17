import re
import json
import pdfplumber
import requests



PDF_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32024R1689"
LOCAL_FILE= None
OUTPUT_PATH = "eu_ai_output.json"


def get_pdf(PDF_URL,LOCAL_FILE):
    if LOCAL_FILE:
        with open(LOCAL_FILE,'rb') as f:
            pdf=pdfplumber.open(f)

    else:
        print("Downloading AI Act PDF from EUR-Lex...")
        response=requests.get(PDF_URL,timeout=300)
        response.raise_for_status()

        return response.content


def clean_pdf(raw_text):
    









