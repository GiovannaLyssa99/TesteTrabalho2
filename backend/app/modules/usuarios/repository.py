from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: models.User) -> models.User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.email == email).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def update(self, user: models.User) -> models.User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: models.User):
        self.db.delete(user)
        self.db.commit()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    profile_data = user.profile
    db_profile = models.InventorProfile(
        user_id=db_user.id,
        area_atuacao=profile_data.area_atuacao,
        experiencia=profile_data.experiencia,
        descricao_inovacao=profile_data.descricao_inovacao,
        estagio_inovacao=profile_data.estagio_inovacao,
        palavras_chave=profile_data.palavras_chave
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    repo = UserRepository(db)
    user = repo.get_by_email(email)
    if not user:
        return None
    hashed = getattr(user, "hashed_password", None) or getattr(user, "password", None)
    if not hashed:
        return None
    if not verify_password(password, hashed):
        return None
    return user

def get_user_by_email(db: Session, email: str):
    repo = UserRepository(db)
    return repo.get_by_email(email)

def get_user_by_id(db: Session, user_id: int):
    repo = UserRepository(db)
    return repo.get_by_id(user_id)