import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.spiellogik import SpiellogikRequest, SpiellogikResponse

router = APIRouter(prefix="/api/spiellogik", tags=["spiellogik"])


def _load_config(name: str) -> dict:
    path = settings.gamelogic_path / "config" / name
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_setting(setting_name: str) -> dict:
    path = settings.gamelogic_path / "settings" / f"{setting_name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Setting '{setting_name}' nicht gefunden")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.post("/attribut/steigern", response_model=SpiellogikResponse)
def attribut_steigern(req: SpiellogikRequest):
    daten = req.charakter_daten
    attr_name = req.element_name
    if not attr_name or attr_name not in daten.get("attribute", {}):
        return SpiellogikResponse(success=False, message=f"Attribut '{attr_name}' nicht gefunden")

    verbleibend = daten.get("verbleibende_attributsteigerungen", 0)
    if verbleibend <= 0:
        return SpiellogikResponse(
            success=False,
            message="Keine Attributsteigerungen mehr verfügbar",
            charakter_daten=daten,
        )

    attr = daten["attribute"][attr_name]
    wert = attr.get("wert", 4)
    modifier = attr.get("modifier", 0)

    if wert == 12 and modifier >= 2:
        return SpiellogikResponse(
            success=False,
            message=f"{attr_name} ist bereits auf dem Maximum (W12+2)",
            charakter_daten=daten,
        )

    if wert == 12:
        attr["modifier"] = modifier + 1
    elif wert == 4 and modifier == -2:
        attr["modifier"] = 0
    else:
        attr["wert"] = wert + 2

    daten["verbleibende_attributsteigerungen"] = verbleibend - 1
    daten["attribute"][attr_name] = attr
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/attribut/senken", response_model=SpiellogikResponse)
def attribut_senken(req: SpiellogikRequest):
    daten = req.charakter_daten
    attr_name = req.element_name
    if not attr_name or attr_name not in daten.get("attribute", {}):
        return SpiellogikResponse(success=False, message=f"Attribut '{attr_name}' nicht gefunden")

    attr = daten["attribute"][attr_name]
    wert = attr.get("wert", 4)
    modifier = attr.get("modifier", 0)
    max_steig = daten.get("maximale_attributsteigerungen", 5)
    verbleibend = daten.get("verbleibende_attributsteigerungen", 0)

    if wert <= 4 and modifier <= 0:
        return SpiellogikResponse(
            success=False,
            message=f"{attr_name} kann nicht weiter gesenkt werden",
            charakter_daten=daten,
        )

    if verbleibend >= max_steig:
        return SpiellogikResponse(
            success=False,
            message="Keine Steigerungen zum Rückgängigmachen",
            charakter_daten=daten,
        )

    if wert == 12 and modifier > 0:
        attr["modifier"] = modifier - 1
    elif wert > 4:
        attr["wert"] = wert - 2
    else:
        return SpiellogikResponse(success=False, message="Minimum erreicht", charakter_daten=daten)

    daten["verbleibende_attributsteigerungen"] = verbleibend + 1
    daten["attribute"][attr_name] = attr
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/fertigkeit/steigern", response_model=SpiellogikResponse)
def fertigkeit_steigern(req: SpiellogikRequest):
    daten = req.charakter_daten
    fert_name = req.element_name
    if not fert_name or fert_name not in daten.get("fertigkeiten", {}):
        return SpiellogikResponse(success=False, message=f"Fertigkeit '{fert_name}' nicht gefunden")

    verbleibend = daten.get("verbleibende_fertigkeitssteigerungen", 0)
    if verbleibend <= 0:
        return SpiellogikResponse(
            success=False,
            message="Keine Fertigkeitssteigerungen mehr verfügbar",
            charakter_daten=daten,
        )

    fert = daten["fertigkeiten"][fert_name]
    wuerfel = fert.get("wuerfel", {"value": 4, "modifier": -2})
    wert = wuerfel.get("value", 4)
    modifier = wuerfel.get("modifier", -2)

    attr_name = fert.get("attribut", "")
    attr_wert = daten.get("attribute", {}).get(attr_name, {}).get("wert", 4)

    kosten = 1
    if wert > attr_wert:
        kosten = 2

    if modifier == -2:
        wuerfel["modifier"] = 0
        kosten = 1
    elif wert == 12 and modifier < 2:
        wuerfel["modifier"] = modifier + 1
    elif wert < 12:
        wuerfel["value"] = wert + 2
    else:
        return SpiellogikResponse(success=False, message="Maximum erreicht", charakter_daten=daten)

    if verbleibend < kosten:
        return SpiellogikResponse(
            success=False,
            message=f"Nicht genug Punkte ({kosten} benötigt, {verbleibend} verfügbar)",
            charakter_daten=daten,
        )

    fert["wuerfel"] = wuerfel
    fert["ausgewaehlt"] = True
    daten["fertigkeiten"][fert_name] = fert
    daten["verbleibende_fertigkeitssteigerungen"] = verbleibend - kosten
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/fertigkeit/senken", response_model=SpiellogikResponse)
def fertigkeit_senken(req: SpiellogikRequest):
    daten = req.charakter_daten
    fert_name = req.element_name
    if not fert_name or fert_name not in daten.get("fertigkeiten", {}):
        return SpiellogikResponse(success=False, message=f"Fertigkeit '{fert_name}' nicht gefunden")

    fert = daten["fertigkeiten"][fert_name]
    wuerfel = fert.get("wuerfel", {"value": 4, "modifier": 0})
    wert = wuerfel.get("value", 4)
    modifier = wuerfel.get("modifier", 0)
    grundfertigkeit = fert.get("grundfertigkeit", False)

    min_modifier = 0 if grundfertigkeit else -2
    if wert <= 4 and modifier <= min_modifier:
        return SpiellogikResponse(
            success=False,
            message=f"{fert_name} kann nicht weiter gesenkt werden",
            charakter_daten=daten,
        )

    attr_name = fert.get("attribut", "")
    attr_wert = daten.get("attribute", {}).get(attr_name, {}).get("wert", 4)
    refund = 2 if wert > attr_wert else 1

    if wert == 12 and modifier > 0:
        wuerfel["modifier"] = modifier - 1
    elif wert > 4:
        wuerfel["value"] = wert - 2
    elif wert == 4 and modifier == 0 and not grundfertigkeit:
        wuerfel["modifier"] = -2
        refund = 1
    else:
        return SpiellogikResponse(success=False, message="Minimum erreicht", charakter_daten=daten)

    fert["wuerfel"] = wuerfel
    if wuerfel["value"] == 4 and wuerfel["modifier"] == -2:
        fert["ausgewaehlt"] = False
    daten["fertigkeiten"][fert_name] = fert
    daten["verbleibende_fertigkeitssteigerungen"] = daten.get("verbleibende_fertigkeitssteigerungen", 0) + refund
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/handicap/waehlen", response_model=SpiellogikResponse)
def handicap_waehlen(req: SpiellogikRequest):
    daten = req.charakter_daten
    handicap_name = req.element_name
    setting_name = daten.get("active_setting_name", "SWAE")

    try:
        setting = _load_setting(setting_name)
    except HTTPException:
        return SpiellogikResponse(success=False, message=f"Setting '{setting_name}' nicht gefunden")

    handicap_data = setting.get("handicaps", {}).get(handicap_name)
    if not handicap_data:
        return SpiellogikResponse(success=False, message=f"Handicap '{handicap_name}' nicht gefunden")

    selected = daten.get("selected_handicaps", [])
    if handicap_name in selected:
        return SpiellogikResponse(success=False, message=f"'{handicap_name}' bereits ausgewählt")

    stufe = handicap_data.get("stufe", "leicht").lower()
    punkte = 1 if stufe == "leicht" else 2
    gesamt = daten.get("gesamt_handicap_punkte", 0)
    if gesamt + punkte > 4:
        return SpiellogikResponse(success=False, message="Maximale Handicap-Punkte (4) erreicht")

    selected.append(handicap_name)
    daten["selected_handicaps"] = selected
    daten["gesamt_handicap_punkte"] = gesamt + punkte
    daten["verbleibende_handicap_punkte"] = punkte
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/handicap/entfernen", response_model=SpiellogikResponse)
def handicap_entfernen(req: SpiellogikRequest):
    daten = req.charakter_daten
    handicap_name = req.element_name
    selected = daten.get("selected_handicaps", [])

    if handicap_name not in selected:
        return SpiellogikResponse(success=False, message=f"'{handicap_name}' ist nicht ausgewählt")

    setting_name = daten.get("active_setting_name", "SWAE")
    try:
        setting = _load_setting(setting_name)
    except HTTPException:
        return SpiellogikResponse(success=False, message=f"Setting '{setting_name}' nicht gefunden")

    handicap_data = setting.get("handicaps", {}).get(handicap_name, {})
    stufe = handicap_data.get("stufe", "leicht").lower()
    punkte = 1 if stufe == "leicht" else 2

    selected.remove(handicap_name)
    daten["selected_handicaps"] = selected
    daten["gesamt_handicap_punkte"] = max(0, daten.get("gesamt_handicap_punkte", 0) - punkte)
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/talent/waehlen", response_model=SpiellogikResponse)
def talent_waehlen(req: SpiellogikRequest):
    daten = req.charakter_daten
    talent_name = req.element_name
    selected = daten.get("selected_talente", [])

    if talent_name in selected:
        return SpiellogikResponse(success=False, message=f"'{talent_name}' bereits ausgewählt")

    selected.append(talent_name)
    daten["selected_talente"] = selected
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/talent/entfernen", response_model=SpiellogikResponse)
def talent_entfernen(req: SpiellogikRequest):
    daten = req.charakter_daten
    talent_name = req.element_name
    selected = daten.get("selected_talente", [])

    if talent_name not in selected:
        return SpiellogikResponse(success=False, message=f"'{talent_name}' ist nicht ausgewählt")

    selected.remove(talent_name)
    daten["selected_talente"] = selected
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/volk/waehlen", response_model=SpiellogikResponse)
def volk_waehlen(req: SpiellogikRequest):
    daten = req.charakter_daten
    volk_name = req.element_name
    setting_name = daten.get("active_setting_name", "SWAE")

    try:
        setting = _load_setting(setting_name)
    except HTTPException:
        return SpiellogikResponse(success=False, message=f"Setting '{setting_name}' nicht gefunden")

    volk_data = setting.get("voelker", {}).get(volk_name)
    if not volk_data:
        return SpiellogikResponse(success=False, message=f"Volk '{volk_name}' nicht gefunden")

    daten["voelker_selected"] = {volk_name: volk_data}
    return SpiellogikResponse(success=True, charakter_daten=daten)


@router.post("/berechne")
def berechne_abgeleitete_werte(req: SpiellogikRequest):
    daten = req.charakter_daten

    konstitution = daten.get("attribute", {}).get("Konstitution", {})
    kon_wert = konstitution.get("wert", 4)
    kon_mod = konstitution.get("modifier", 0)

    geschicklichkeit = daten.get("attribute", {}).get("Geschicklichkeit", {})
    gesc_wert = geschicklichkeit.get("wert", 4)

    kaempfen = daten.get("fertigkeiten", {}).get("Kämpfen", {})
    kaempfen_wuerfel = kaempfen.get("wuerfel", {"value": 4, "modifier": -2})
    kaempfen_wert = kaempfen_wuerfel.get("value", 4)

    robustheit = 2 + (kon_wert // 2)
    parade = 2 + (kaempfen_wert // 2)
    bewegungsweite = 6

    return {
        "parade": parade,
        "robustheit": robustheit,
        "bewegungsweite": bewegungsweite,
        "verbleibende_attributsteigerungen": daten.get("verbleibende_attributsteigerungen", 5),
        "verbleibende_fertigkeitssteigerungen": daten.get("verbleibende_fertigkeitssteigerungen", 12),
        "verbleibende_handicap_punkte": daten.get("verbleibende_handicap_punkte", 0),
    }
