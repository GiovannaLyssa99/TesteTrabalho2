from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: models.User) -> models.User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[models.User]:
        result = await self.db.execute(select(models.User).where(models.User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[models.User]:
        result = await self.db.execute(select(models.User).where(models.User.email == email))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        result = await self.db.execute(select(models.User).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, user: models.User) -> models.User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: models.User):
        await self.db.delete(user)
        await self.db.commit()


# --- Funções auxiliares (hash/senha) ---

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- Funções CRUD e autenticação (adaptadas para async) ---

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

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
    await db.commit()
    await db.refresh(db_profile)
    await db.refresh(db_user)

    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[models.User]:
    repo = UserRepository(db)
    user = await repo.get_by_email(email)
    if not user:
        return None

    hashed = getattr(user, "hashed_password", None) or getattr(user, "password", None)
    if not hashed:
        return None
    if not verify_password(password, hashed):
        return None

    return user


async def get_user_by_email(db: AsyncSession, email: str):
    repo = UserRepository(db)
    return await repo.get_by_email(email)

async def get_user_by_id(db: AsyncSession, user_id: int):
    repo = UserRepository(db)
    return await repo.get_by_id(user_id)