import os
import re
from typing import List, Dict
from pypdf import PdfReader
from apps.config import CHUNK_SIZE, CHUNK_OVERLAP

# 1 - Text Extraction 

# 1a. Extract texst from PDF files
def extract_text_from_pdf(file_path:str)->List[Dict]:
    
    reader=PdfReader(file_path)

    pages=[]

    for i, page in enumerate(reader.pages):
        text=page.extract_text() or ""
        if text.strip():  # Only add non-empty pages
            pages.append({
                "page_number":i+1,
                "text":text
            })
    return pages

# 1b. Extract texst from TEXT files

def extract_text_from_txt(file_path:str)->List[Dict]:
    with open(file_path,'r', encoding='utf-8') as f:
        return(
            {
                "page_number":1,
                "text":f.read()
            }
        )
    

# combine both functions into one
def extract_pages(file_path:str)->List[Dict]:
    ext=os.path.splitext(file_path)[1].lower()
    if ext=='.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.txt','.md']:
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f'Unsupported file type: {ext}')
    

#print(result[0])  # Print the first page's content
    


# 2 - Text Cleaning and Chunking

def clean_text(text:str)->str:
    text=re.sub(r'\s+', " ",text).strip()
    return text.strip()

def chunk_pages(
        pages:List[Dict],
        chunk_size:int=CHUNK_SIZE,
        chunk_overlap:int=CHUNK_OVERLAP
)->List[Dict]:
    
    full_text = "" 
    char_to_pages:List[int]=[]

    for p in pages:
        cleaned = clean_text(p['text'])

        if cleaned:
            if full_text:
                full_text += " "
                char_to_pages.extend(p["page_number"])
            full_text += cleaned
            char_to_pages.extend([p["page_number"]] * len(cleaned))
                                     

        chunks:List[Dict]=[]
        start=0
        while start < len(full_text):
            end = min(start + chunk_size, len(full_text))
            chunk = full_text[start:end]
            
            if chunk:
                page_set=set(char_to_pages[start:end])
                chunks.append({
                    "chunk_text": chunk,
                    "source_pages": list(page_set)
                })
            start += chunk_size - chunk_overlap

        return chunks


def ingest_document(file_path:str)-> List[Dict]:
    file_name=os.path.basename(file_path)

    pages=extract_pages(file_path)
    chunks=chunk_pages(pages)
    records=[]
    for idx, chunk in enumerate(chunks):
        page_str=', '.join(str(p) for p in chunk["source_pages"])
        records.append({
            "chunk_id": idx+1,
            "file_name": file_name,
            "chunk_text": chunk["chunk_text"],
            "source_pages": chunk["source_pages"]
        })
    
    print(f"Ingested {len(records)} chunks from {file_name}")

    return records

result=ingest_document('/Users/priyankaneogi/Desktop/RAG_CLASSIC_PIPELINE/Apple_Q24.pdf')
print(result[2])