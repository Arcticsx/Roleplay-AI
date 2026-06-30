import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from app.database import Base

def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)

class RpgSession(Base):
    __tablename__ = "rpg_sessions"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String, nullable=False)
    synopsis = Column(Text, nullable=True)
    genre = Column(String, nullable=True)
    world_key = Column(String, nullable=True, index=True)
    magic_rules_md = Column(Text, nullable=True)
    active_chapter_number = Column(Integer, nullable=False, default=1)
    word_count_total = Column(Integer, nullable=False, default=0)
    context_token_limit = Column(Integer, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    chapters = relationship(
        "ChronicleChapter",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChronicleChapter.number",
    )

    def __repr__(self) -> str:
        return f"<RpgSession id={self.id!r} title={self.title!r}>"


class ChronicleChapter(Base):

    __tablename__ = "chronicle_chapters"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(
        String, ForeignKey("rpg_sessions.id", ondelete="CASCADE"), nullable=False
    )
    number = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    messages_json = Column(Text, nullable=False, default="[]")
    token_count = Column(Integer, nullable=False, default=0)
    is_closed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    session = relationship("RpgSession", back_populates="chapters")

    def __repr__(self) -> str:
        return (
            f"<ChronicleChapter id={self.id!r} session_id={self.session_id!r} "
            f"number={self.number} closed={self.is_closed}>"
        )


class Character(Base):
    __tablename__ = "character"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("rpg_session.id"))
    name = Column(String)
    role = Column(String)
    personality_md = Column(Text)
    backstory_md = Column(Text)
    secret = Column(Text)

    session = relationship("RPGSession", back_populates="characters")
    relations_as_a = relationship(
        "CharacterRelation",
        foreign_keys="CharacterRelation.char_a_id",
        back_populates="char_a"
    )
    relations_as_b = relationship(
        "CharacterRelation",
        foreign_keys="CharacterRelation.char_b_id",
        back_populates="char_b"
    )


class CharacterRelation(Base):
    __tablename__ = "character_relation"

    char_a_id = Column(String, ForeignKey("character.id"), primary_key=True)
    char_b_id = Column(String, ForeignKey("character.id"), primary_key=True)
    relation_type = Column(String)
    notes = Column(Text)

    char_a = relationship("Character", foreign_keys=[char_a_id], back_populates="relations_as_a")
    char_b = relationship("Character", foreign_keys=[char_b_id], back_populates="relations_as_b")


class LoreEntry(Base):
    __tablename__ = "lore_entry"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("rpg_session.id"))
    category = Column(String)
    title = Column(String)
    body_md = Column(Text)
    pinned = Column(Boolean)
    embedding_id = Column(String, ForeignKey("chroma_lore_collection.lore_id"))

    session = relationship("RPGSession", back_populates="lore_entries")
    embedding = relationship("ChromaLoreCollection", back_populates="lore_entry", uselist=False)


class StoryBeat(Base):
    __tablename__ = "story_beat"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("rpg_session.id"))
    description = Column(Text)
    triggered = Column(Boolean)
    order = Column(Integer)   # 'order' is a reserved word in SQL, but quoted in models

    session = relationship("RPGSession", back_populates="story_beats")


class StoryEvent(Base):
    __tablename__ = "story_event"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("rpg_session.id"))
    chapter = Column(Integer)          # chapter number, not a FK
    description = Column(Text)
    significance = Column(String)

    session = relationship("RPGSession", back_populates="story_events")


class SourceDocument(Base):
    __tablename__ = "source_document"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("rpg_session.id"))
    filename = Column(String)
    status = Column(String)
    chunk_count = Column(Integer)

    session = relationship("RPGSession", back_populates="source_documents")


class TurnLog(Base):
    __tablename__ = "turn_log"

    id = Column(String, primary_key=True)
    chapter_id = Column(String, ForeignKey("chronicle_chapter.id"))
    player_action = Column(Text)
    dice_roll = Column(Integer)
    outcome = Column(String)
    narrative = Column(Text)

    chapter = relationship("ChronicleChapter", back_populates="turns")


class ChromaDocsCollection(Base):
    __tablename__ = "chroma_docs_collection"

    chunk_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("rpg_session.id"))
    embedding = Column(String)          # custom vector type (JSON or dedicated)
    chunk_text = Column(Text)
    source_page = Column(Integer)

    session = relationship("RPGSession", back_populates="chroma_docs")


class ChromaLoreCollection(Base):
    __tablename__ = "chroma_lore_collection"

    lore_id = Column(String, primary_key=True)   # this is also the FK from LoreEntry
    session_id = Column(String, ForeignKey("rpg_session.id"))
    embedding = Column(String)          # custom vector type (JSON or dedicated)
    source_text = Column(Text)

    session = relationship("RPGSession", back_populates="chroma_lore")
    lore_entry = relationship("LoreEntry", back_populates="embedding", uselist=False)