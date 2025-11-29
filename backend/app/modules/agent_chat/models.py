import enum
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.infra.database import Base

class MessageType(enum.Enum):
    AI = "ai_message"
    HUMAN = "human_message"
    CHECKLIST = "checklist"

class Conversa(Base):
    __tablename__ = "conversa"

    thread_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=True, index=True)
    titulo = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mensagens = relationship("Mensagem", cascade="all, delete-orphan")

class Mensagem(Base):
    __tablename__ = "mensagem"

    id = Column(Integer, nullable=True, primary_key=True, index=True)
    content = Column(String, nullable=False)
    type = Column(Enum(MessageType, native_enum=False), nullable=False)
    conversa_id = Column(UUID(as_uuid=True), ForeignKey("conversa.thread_id"))