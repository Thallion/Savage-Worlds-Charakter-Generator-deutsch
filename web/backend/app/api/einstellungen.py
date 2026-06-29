import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

_settings_dir = settings.gamelogic_path / "settings"


@router.get("")
def list_settings():
    result = []
    for path in sorted(_settings_dir.glob("*.json")):
        result.append({"name": path.stem, "datei": path.name})
    return result


@router.get("/{setting_name}")
def get_setting(setting_name: str):
    json_path = _settings_dir / f"{setting_name}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail=f"Setting '{setting_name}' nicht gefunden")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
