from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.modules.usuarios import schemas, service
from app.modules.auth.auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=schemas.UserRead, status_code=201)
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    svc = service.UserService(db)
    try:
        created = await svc.create_user_with_profile(user.name, user.email, user.password, user.profile.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created

@router.get("/", response_model=List[schemas.UserOut], dependencies=[Depends(require_admin)])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    svc = service.UserService(db)
    return await svc.list_users(skip=skip, limit=limit)

@router.get("/me", response_model=schemas.UserRead)
async def read_own_profile(current_user = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(require_admin)])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    svc = service.UserService(db)
    db_user = await svc.get_user(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.put("/me", response_model=schemas.UserRead)
async def update_me(payload: schemas.UserUpdate, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = service.UserService(db)
    updated = await svc.update_user(current_user, payload.dict(exclude_unset=True))
    return updated

@router.put("/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(require_admin)])
async def update_user(user_id: int, payload: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    svc = service.UserService(db)
    user = await svc.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    updated = await svc.update_user(user, payload.dict(exclude_unset=True))
    return updated

@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    svc = service.UserService(db)
    user = await svc.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    await svc.delete_user(user, soft=True)
    return None