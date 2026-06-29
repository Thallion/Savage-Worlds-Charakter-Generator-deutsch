import hashlib
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from app.jwt_utils import encode as jwt_encode
from sqlalchemy.orm import Session

from app.config import settings
from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models as db_models
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + key.hex()


def _verify_password(password: str, stored: str) -> bool:
    salt_hex, key_hex = stored.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return key.hex() == key_hex


def _create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt_encode(
        {"sub": user_id, "exp": expire.timestamp()},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(db_models.User).filter(db_models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
    if db.query(db_models.User).filter(db_models.User.benutzername == user_in.benutzername).first():
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")

    user = db_models.User(
        email=user_in.email,
        benutzername=user_in.benutzername,
        hashed_password=_hash_password(user_in.passwort),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(db_models.User.email == user_in.email).first()
    if not user or not _verify_password(user_in.passwort, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail oder Passwort falsch",
        )
    return Token(access_token=_create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def me(current_user: db_models.User = Depends(get_current_user)):
    return current_user
