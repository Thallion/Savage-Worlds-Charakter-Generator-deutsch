from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models as db_models
from app.schemas.charakter import (
    CharakterCreate,
    CharakterUpdate,
    CharakterDetail,
    CharakterListItem,
)

router = APIRouter(prefix="/api/charaktere", tags=["charaktere"])


@router.get("", response_model=list[CharakterListItem])
def list_charaktere(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    return (
        db.query(db_models.Charakter)
        .filter(db_models.Charakter.user_id == current_user.id)
        .order_by(db_models.Charakter.aktualisiert_am.desc())
        .all()
    )


@router.post("", response_model=CharakterDetail, status_code=status.HTTP_201_CREATED)
def create_charakter(
    data: CharakterCreate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    charakter = db_models.Charakter(
        user_id=current_user.id,
        char_name=data.char_name,
        active_setting_name=data.active_setting_name,
        charakter_daten={
            "profil_daten": {"Name": data.char_name},
            "active_setting_name": data.active_setting_name,
            "char_gen_completed": False,
            "attribute": {},
            "fertigkeiten": {},
            "selected_handicaps": [],
            "selected_talente": [],
            "selected_maechte": [],
            "voelker_selected": {},
        },
    )
    db.add(charakter)
    db.commit()
    db.refresh(charakter)
    return charakter


@router.get("/{charakter_id}", response_model=CharakterDetail)
def get_charakter(
    charakter_id: int,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    charakter = _get_own_charakter(db, charakter_id, current_user.id)
    return charakter


@router.put("/{charakter_id}", response_model=CharakterDetail)
def update_charakter(
    charakter_id: int,
    data: CharakterUpdate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    charakter = _get_own_charakter(db, charakter_id, current_user.id)

    if data.char_name is not None:
        charakter.char_name = data.char_name
    if data.active_setting_name is not None:
        charakter.active_setting_name = data.active_setting_name
    if data.char_gen_completed is not None:
        charakter.char_gen_completed = data.char_gen_completed
    if data.charakter_daten is not None:
        charakter.charakter_daten = data.charakter_daten

    charakter.aktualisiert_am = datetime.utcnow()
    db.commit()
    db.refresh(charakter)
    return charakter


@router.delete("/{charakter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_charakter(
    charakter_id: int,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    charakter = _get_own_charakter(db, charakter_id, current_user.id)
    db.delete(charakter)
    db.commit()


@router.get("/{charakter_id}/export")
def export_charakter(
    charakter_id: int,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    charakter = _get_own_charakter(db, charakter_id, current_user.id)
    return JSONResponse(
        content=charakter.charakter_daten,
        headers={
            "Content-Disposition": f'attachment; filename="{charakter.char_name or "charakter"}.json"'
        },
    )


def _get_own_charakter(db: Session, charakter_id: int, user_id: int) -> db_models.Charakter:
    charakter = (
        db.query(db_models.Charakter)
        .filter(
            db_models.Charakter.id == charakter_id,
            db_models.Charakter.user_id == user_id,
        )
        .first()
    )
    if not charakter:
        raise HTTPException(status_code=404, detail="Charakter nicht gefunden")
    return charakter
