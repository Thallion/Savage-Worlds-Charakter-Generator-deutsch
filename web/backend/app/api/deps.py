from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.jwt_utils import decode as jwt_decode, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db import models as db_models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> db_models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ungültige Anmeldedaten",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt_decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    if user is None or not user.aktiv:
        raise credentials_exception
    return user
