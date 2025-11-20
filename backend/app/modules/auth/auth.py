import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.infra.database import get_db

from app.modules.usuarios import repository as user_repository
from app.modules.usuarios import models as user_models
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.infra.config import Config
    SECRET_KEY = Config.SECRET_KEY
    ALGORITHM = Config.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
except Exception:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM = os.environ.get("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repository.get_user_by_id(db, int(user_id))
    if not user:
        raise credentials_exception
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return user


def require_admin(current_user = Depends(get_current_user)):
    try:
        is_admin = (current_user.role == user_models.RoleEnum.admin or str(current_user.role) == "admin")
    except Exception:
        is_admin = False
    if not is_admin:
        raise HTTPException(status_code=403, detail="Privilégios de administrador necessários")
    return current_user