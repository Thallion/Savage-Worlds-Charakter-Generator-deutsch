from typing import Any

from pydantic import BaseModel


class SpiellogikRequest(BaseModel):
    charakter_daten: dict[str, Any]
    element_name: str | None = None


class SpiellogikResponse(BaseModel):
    success: bool
    message: str = ""
    charakter_daten: dict[str, Any] | None = None


class BerechneResponse(BaseModel):
    parade: int
    robustheit: int
    bewegungsweite: int
    verbleibende_attributsteigerungen: int
    verbleibende_fertigkeitssteigerungen: int
    verbleibende_handicap_punkte: int
