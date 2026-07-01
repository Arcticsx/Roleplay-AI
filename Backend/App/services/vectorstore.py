try:
    from ..config import CHROMA_PERSIST_DIR
except ImportError:
    from config import CHROMA_PERSIST_DIR
import chromadb
import uuid  

_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

def get_or_create_collection(session_id: str, collection_type: str):
    """collection_type: 'lore' or 'memory'"""
    if collection_type not in ("lore", "memory"):
        raise ValueError(f"Invalid collection_type: {collection_type}")

    client = _client
    collection_name = f"session_{session_id}_{collection_type}"
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"session_id": session_id, "type": collection_type},
    )


def _infer_category(metadata: dict) -> str:
    """Best-effort category from header metadata, for optional where-filtering later."""
    header = metadata.get("subsection") or metadata.get("section") or ""
    return header.strip().lower() if header else "general"


def save_chunks_to_chromadb(
    chunks,
    embeddings,
    session_id: str,
    source_pdf: str,
    collection_type: str = "lore",
):
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Mismatch between chunks ({len(chunks)}) and embeddings ({len(embeddings)})"
        )

    if not chunks:
        return {"chunks_saved": 0}

    collection = get_or_create_collection(session_id, collection_type)

    documents = [chunk.page_content for chunk in chunks]
    metadatas = [
        {
            **{k: v for k, v in chunk.metadata.items() if v is not None},
            "category": _infer_category(chunk.metadata),
            "source_pdf": source_pdf,
            "session_id": session_id,
        }
        for chunk in chunks
    ]
    ids = [f"{session_id}_{uuid.uuid4()}" for _ in chunks]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=ids,
    )

    return {
        "chunks_saved": len(chunks),
        "collection": collection.name,
    }