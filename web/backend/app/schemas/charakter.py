from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CharakterCreate(BaseModel):
    char_name: str = ""
    active_setting_name: str = "SWAE"


class CharakterUpdate(BaseModel):
    char_name: str | None = None
    active_setting_name: str | None = None
    char_gen_completed: bool | None = None
    charakter_daten: dict[str, Any] | None = None


class CharakterResponse(BaseModel):
    id: int
    char_name: str
    active_setting_name: str
    char_gen_completed: bool
    erstellt_am: datetime
    aktualisiert_am: datetime

    model_config = {"from_attributes": True}


class CharakterDetail(CharakterResponse):
    charakter_daten: dict[str, Any]


class CharakterListItem(BaseModel):
    id: int
    char_name: str
    active_setting_name: str
    char_gen_completed: bool
    aktualisiert_am: datetime

    model_config = {"from_attributes": True}
