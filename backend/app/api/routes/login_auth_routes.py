from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.modules.usuarios import service as user_service
from app.modules.usuarios import schemas as user_schemas
from app.modules.auth.auth import create_access_token

auth_router = APIRouter(tags=["auth"])

@auth_router.post("/login", response_model=user_schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    svc = user_service.UserService(db)
    user = await svc.get_by_email(form_data.username)
    if not user or not user_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos")
    token = create_access_token({"sub": str(user.id), "role": str(user.role)})
    return {"access_token": token, "token_type": "bearer"}