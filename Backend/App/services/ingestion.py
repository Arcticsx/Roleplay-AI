import os
import shutil
import uuid
from sqlalchemy.orm import Session

from services.documents import chunk_document, embed_chunks
from services.vectorstore import save_chunks_to_chromadb
from models import SourceDocument

UPLOAD_DIR = "app/data/uploads"
ALLOWED_EXTENSIONS = {".pdf"}


def ingest_pdf_to_session(db: Session, session_id: str, file, filename: str) -> SourceDocument:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    source_doc = SourceDocument(
        session_id=session_id,
        filename=filename,
        status="processing",
        chunk_count=0,
    )
    db.add(source_doc)
    db.commit()
    db.refresh(source_doc)

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file, f)

        chunks = chunk_document(temp_path)
        if not chunks:
            raise ValueError("No content could be extracted from the document")

        embeddings = embed_chunks(chunks)
        result = save_chunks_to_chromadb(
            chunks=chunks,
            embeddings=embeddings,
            session_id=session_id,
            source_pdf=filename,
            collection_type="lore",
        )

        source_doc.status = "ready"
        source_doc.chunk_count = result["chunks_saved"]
        db.commit()
        return source_doc

    except Exception:
        source_doc.status = "failed"
        db.commit()
        raise

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)