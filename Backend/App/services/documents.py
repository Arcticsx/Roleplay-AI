import pymupdf4llm
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

def extract_markdown_from_pdf(file_path):
    return pymupdf4llm.to_markdown(file_path)


def normalize_text(text):
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

_embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def token_length(text):
    return len(_embedding_model.tokenizer.encode(text))

def chunk_document(file_path):
    
    raw_md = extract_markdown_from_pdf(file_path)
    normalized_md = normalize_text(raw_md)
    
    headers_to_split_on = [
        ("#", "section"),
        ("##", "subsection"),
        ("###", "subsubsection"),
    ]
    
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    header_chunks = md_splitter.split_text(normalized_md)
    
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,       
        chunk_overlap=40,      
        length_function=token_length,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    final_chunks = fallback_splitter.split_documents(header_chunks)

    return final_chunks

def embed_chunks(chunks, batch_size: int = 32):
    if not chunks:
        return []

    texts = [chunk.page_content for chunk in chunks]

    embeddings = _embedding_model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )

    return embeddings.tolist()



    
    