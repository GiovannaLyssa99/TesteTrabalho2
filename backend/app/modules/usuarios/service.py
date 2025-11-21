from typing import Optional, Dict
from sqlalchemy.orm import Session
from .repository import UserRepository, hash_password, verify_password
from . import models

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def create_user_with_profile(self, name: str, email: str, password: str, profile_data: dict, role: models.RoleEnum = models.RoleEnum.user, is_active: bool = True) -> models.User:
        if self.repo.get_by_email(email):
            raise ValueError("E-mail já cadastrado")
        user = models.User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            is_active=is_active
        )
        profile = models.InventorProfile(
            area_atuacao=profile_data.get("area_atuacao"),
            experiencia=profile_data.get("experiencia"),
            descricao_inovacao=profile_data.get("descricao_inovacao"),
            estagio_inovacao=profile_data.get("estagio_inovacao"),
            palavras_chave=profile_data.get("palavras_chave")
        )
        user.profile = profile
        return self.repo.create(user)

    def get_user(self, user_id: int) -> Optional[models.User]:
        return self.repo.get_by_id(user_id)

    def get_by_email(self, email: str) -> Optional[models.User]:
        return self.repo.get_by_email(email)

    def list_users(self, skip: int = 0, limit: int = 100):
        return self.repo.list(skip=skip, limit=limit)

    def update_user(self, user: models.User, data: Dict):
        if "password" in data and data["password"]:
            user.hashed_password = hash_password(data["password"])
            data.pop("password", None)
        for key in ("name", "email", "role", "is_active"):
            if key in data and data[key] is not None:
                setattr(user, key, data[key])
        profile_payload = data.get("profile")
        if profile_payload:
            if not user.profile:
                user.profile = models.InventorProfile()
            for pk, pv in profile_payload.items():
                if hasattr(user.profile, pk) and pv is not None:
                    setattr(user.profile, pk, pv)
        return self.repo.update(user)

    def delete_user(self, user: models.User, soft: bool = True):
        if soft:
            user.is_active = False
            return self.repo.update(user)
        else:
            return self.repo.delete(user)

    def authenticate_user(self, email: str, password: str) -> Optional[models.User]:
        user = self.repo.get_by_email(email)
        if not user:
            return None
        hashed = getattr(user, "hashed_password", None) or getattr(user, "password", None)
        if not hashed:
            return None
        if not verify_password(password, hashed):
            return None
        return user