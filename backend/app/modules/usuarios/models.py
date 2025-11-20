from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infra.database import Base
import enum

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    role = Column(SAEnum(RoleEnum, native_enum=False, length=50), default=RoleEnum.user, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    profile = relationship("InventorProfile", back_populates="user", uselist=False, lazy="joined")


class InventorProfile(Base):
    __tablename__ = "inventor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    area_atuacao = Column(String(150), nullable=False)
    experiencia = Column(String(255))
    descricao_inovacao = Column(Text, nullable=False)
    estagio_inovacao = Column(String(50))
    palavras_chave = Column(String(255))

    user = relationship("User", back_populates="profile")
