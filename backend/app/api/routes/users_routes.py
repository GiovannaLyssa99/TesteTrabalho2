from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.infra.database import get_db
from app.modules.usuarios import schemas, service
from app.modules.auth.auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=schemas.UserRead, status_code=201)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    svc = service.UserService(db)
    try:
        created = svc.create_user_with_profile(user.name, user.email, user.password, user.profile.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created

@router.get("/", response_model=List[schemas.UserOut], dependencies=[Depends(require_admin)])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    svc = service.UserService(db)
    return svc.list_users(skip=skip, limit=limit)

@router.get("/me", response_model=schemas.UserRead)
def read_own_profile(current_user = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(require_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    svc = service.UserService(db)
    db_user = svc.get_user(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.put("/me", response_model=schemas.UserRead)
def update_me(payload: schemas.UserUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = service.UserService(db)
    updated = svc.update_user(current_user, payload.dict(exclude_unset=True))
    return updated

@router.put("/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(require_admin)])
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    svc = service.UserService(db)
    user = svc.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    updated = svc.update_user(user, payload.dict(exclude_unset=True))
    return updated

@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    svc = service.UserService(db)
    user = svc.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    svc.delete_user(user, soft=True)
    return None