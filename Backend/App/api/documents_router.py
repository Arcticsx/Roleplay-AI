import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

try:
    from ..services.documents import chunk_document, embed_chunks
    from ..services.vectorstore import save_chunks_to_chromadb
    from ..database import get_db
    from ..models import SourceDocument
except ImportError:
    from services.documents import chunk_document, embed_chunks
    from services.vectorstore import save_chunks_to_chromadb
    from app.database import get_db
    from app.models import SourceDocument

router = APIRouter(prefix="/story", tags=["documents"])

UPLOAD_DIR = "app/data/uploads"
ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/{id}/docs")
async def create_story_document(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    source_doc = SourceDocument(
        session_id=id,
        filename=file.filename,
        status="processing",
        chunk_count=0,
    )
    db.add(source_doc)
    db.commit()
    db.refresh(source_doc)

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            chunks = chunk_document(temp_path)
        except Exception as e:
            source_doc.status = "failed"
            db.commit()
            raise HTTPException(status_code=422, detail=f"Failed to process document: {e}")

        if not chunks:
            source_doc.status = "failed"
            db.commit()
            raise HTTPException(status_code=422, detail="No content could be extracted from the document")

        embeddings = embed_chunks(chunks)

        result = save_chunks_to_chromadb(
            chunks=chunks,
            embeddings=embeddings,
            session_id=id,
            source_pdf=file.filename,
            collection_type="lore",
        )

        source_doc.status = "ready"
        source_doc.chunk_count = result["chunks_saved"]
        db.commit()

        return {
            "status": "success",
            "session_id": id,
            "source_document_id": source_doc.id,
            "source_pdf": file.filename,
            **result,
        }

    except HTTPException:
        raise
    except Exception as e:
        source_doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)