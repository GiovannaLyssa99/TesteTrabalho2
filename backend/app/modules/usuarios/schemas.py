from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"

class InventorProfileCreate(BaseModel):
    area_atuacao: Optional[str] = None
    experiencia: Optional[str] = None
    descricao_inovacao: Optional[str] = None
    estagio_inovacao: Optional[str] = None
    palavras_chave: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)
    profile: Optional[InventorProfileCreate] = None

class UserCreateByAdmin(UserCreate):
    role: Optional[Role] = Role.user
    is_active: Optional[bool] = True

class InventorProfileRead(BaseModel):
    area_atuacao: Optional[str] = None
    experiencia: Optional[str] = None
    descricao_inovacao: Optional[str] = None
    estagio_inovacao: Optional[str] = None
    palavras_chave: Optional[str] = None

    class Config:
        orm_mode = True

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    profile: InventorProfileRead
    role: Optional[Role] = Role.user
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    is_active: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    profile: Optional[InventorProfileCreate] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"