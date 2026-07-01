from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import RpgSession
from services.ingestion import ingest_pdf_to_session

router = APIRouter(prefix="/story", tags=["chronicle"])


@router.post("")
async def create_session(
    title: str = Form(...),
    synopsis: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    world_key: Optional[str] = Form(None),
    magic_rules_md: Optional[str] = Form(None),
    context_token_limit: Optional[int] = Form(None),
    pdf: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    session = RpgSession(
        title=title,
        synopsis=synopsis,
        genre=genre,
        world_key=world_key,
        magic_rules_md=magic_rules_md,
        context_token_limit=context_token_limit,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    source_doc = None
    if pdf is not None and pdf.filename:
        try:
            source_doc = ingest_pdf_to_session(db, session.id, pdf.file, pdf.filename)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Session created but PDF ingestion failed: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Session created but ingestion error: {e}")

    return {
        "id": session.id,
        "title": session.title,
        "synopsis": session.synopsis,
        "genre": session.genre,
        "world_key": session.world_key,
        "created_at": session.created_at.isoformat(),
        "source_document_id": source_doc.id if source_doc else None,
        "chunks_saved": source_doc.chunk_count if source_doc else 0,
    }