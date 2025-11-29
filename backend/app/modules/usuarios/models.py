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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "profile": self.profile.to_dict() if self.profile else None
        }

class InventorProfile(Base):
    __tablename__ = "inventor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    area_atuacao = Column(String(150), nullable=True)
    experiencia = Column(String(255), nullable=True)
    descricao_inovacao = Column(Text, nullable=True)
    estagio_inovacao = Column(String(50), nullable=True)
    palavras_chave = Column(String(255), nullable=True)

    user = relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "area_atuacao": self.area_atuacao,
            "experiencia": self.experiencia,
            "descricao_inovacao": self.descricao_inovacao,
            "estagio_inovacao": self.estagio_inovacao,
            "palavras_chave": self.palavras_chave
        }