"""
Natürliche Waffen (Klauen, Biss, Hörner, waffenlose Schläge).

Der Bestand wird nicht fortgeschrieben, sondern bei jeder Änderung neu aus
Abstammung + gewählten Talenten abgeleitet und mit dem Inventar abgeglichen
(synchronisiere). Das ist nötig, weil Talente vorhandene Waffen verbessern
(Kampfkünstler W4 -> Kampfkunstmeister W6 -> Schläger W8) und ein Snapshot je
Talent diese Ketten nicht sauber zurücknehmen könnte.

Quellen, in dieser Reihenfolge:

1. Abstammung, effects.spezielle_effekte: Settings-Völker setzen nur ein Flag
   ({"klauen": true}) und nennen den Schaden im Fließtext von
   "besonderheiten" ("Klauen (Stä+W4 Schaden, PB 2)"); eigene Abstammungen aus
   volkseigenarten_config.json liefern den Würfel direkt ({"klauen": "W6",
   "panzerbrechend": 2}).
2. Abstammung, "besonderheiten" ohne passendes Flag ("Natürliche Waffen
   (Biss: Stä+W4)", z. B. Horror-Vampir). Bedingte Formulierungen werden
   übersprungen: Alternativfähigkeiten (optionaler Tausch) und
   formabhängige Angaben ("Hybridform: ...", z. B. Horror-Werwolf).
3. Talente aus config/natuerliche_waffen_config.json, je gewählter Kopie in
   Konfigurationsreihenfolge.

Das Ergebnis sind Namen von Ausrüstungs-Einträgen der Kategorie "Waffe"
(Unterkategorie "Natürliche Waffe"), die in jedem Setting vorliegen.
"""

import json
import os
import re
from pathlib import Path

from kivy.logger import Logger

STANDARD_WUERFEL = "W4"
_CONFIG_DATEI = "natuerliche_waffen_config.json"
_config_cache = None

# besonderheiten-Zeile je Gruppe (Völker aus den Setting-JSONs)
_ZEILEN_MUSTER = {
    "biss_klauen": r"Biss\s*(?:/|oder)\s*Klaue|Klauen?\s*/\s*(?:Biss|Zähne)",
    "klauen": r"\bKlauen\b",
    "biss": r"\bBiss\b|\bReißzähne\b",
    "hoerner": r"\bH[öo]rn",
}
# Reihenfolge: die kombinierte Gruppe zuerst, damit "Biss/Klauen" nicht als
# "Biss" durchgeht
_GRUPPEN_REIHENFOLGE = ("biss_klauen", "klauen", "biss", "hoerner", "unbewaffnet")

_WUERFEL_MUSTER = re.compile(r"St[äa](?:rke)?\s*\+\s*(W\d+)")
_PB_MUSTER = re.compile(r"\b(?:PB|AP)\s*\+?\s*(\d+)")
# Zeilen, die die Waffe nur unter Bedingungen gewähren
_BEDINGT_MUSTER = re.compile(r"Alternativfähigkeit|\b\w*form\s*:", re.IGNORECASE)
_NATUERLICHE_WAFFE_MUSTER = re.compile(r"Nat[üu]rliche\s+Waffen?", re.IGNORECASE)


def lade_config():
    """Lädt config/natuerliche_waffen_config.json (mit Modul-Cache)."""
    global _config_cache
    if _config_cache is None:
        pfad = Path(__file__).parent.parent / 'config' / _CONFIG_DATEI
        try:
            if os.path.exists(pfad):
                with open(pfad, 'r', encoding='utf-8') as f:
                    _config_cache = json.load(f)
                Logger.info(f"Natürliche-Waffen-Config geladen von {pfad}")
            else:
                Logger.error(f"Natürliche-Waffen-Config nicht gefunden: {pfad}")
                _config_cache = {}
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Natürliche-Waffen-Config: {e}")
            _config_cache = {}
    return _config_cache


def waffen_name(gruppe_label, wuerfel, pb=0):
    """Name des Ausrüstungs-Eintrags, z. B. 'Klauen (Stä+W6, PB 2)'"""
    pb_teil = f", PB {pb}" if pb else ""
    return f"{gruppe_label} (Stä+{wuerfel}{pb_teil})"


def _steigere(wuerfel, stufen, kette):
    """Erhöht um n Würfeltypen, begrenzt auf das Ende der Kette."""
    if wuerfel not in kette:
        return wuerfel
    return kette[min(kette.index(wuerfel) + stufen, len(kette) - 1)]


def _maximum(a, b, kette):
    """Der höhere der beiden Würfel (unbekannte Würfel gewinnen nicht)."""
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b, key=lambda w: kette.index(w) if w in kette else -1)


def _setze(zustand, gruppe, wuerfel, pb, kette):
    eintrag = zustand.setdefault(gruppe, {"wuerfel": None, "pb": 0})
    eintrag["wuerfel"] = _maximum(eintrag["wuerfel"], wuerfel, kette)
    eintrag["pb"] = max(eintrag["pb"], pb)


def _spezielle_effekte(volk):
    """
    Spezielle Effekte des Volkes als {typ: wert}.

    Unterstützt das Dict-Format der Setting-JSONs und das Listen-Format des
    Volksgenerators ([{'typ': 'klauen', 'wert': 'W6'}]).
    """
    spezielle = (getattr(volk, 'effects', None) or {}).get('spezielle_effekte') or {}
    if isinstance(spezielle, dict):
        return spezielle
    if isinstance(spezielle, list):
        return {e.get('typ'): e.get('wert') for e in spezielle if isinstance(e, dict)}
    return {}


def _volk_besonderheit(volk, gruppe):
    """Die besonderheiten-Zeile, die den Schaden der Gruppe beschreibt."""
    muster = _ZEILEN_MUSTER.get(gruppe)
    if not muster:
        return ""
    for zeile in getattr(volk, 'besonderheiten', None) or []:
        text = str(zeile).strip()
        if _BEDINGT_MUSTER.search(text):
            continue
        if re.search(muster, text, re.IGNORECASE):
            return text
    return ""


def _aus_volk(volk, zustand, kette):
    """Natürliche Waffen der Abstammung in den Zustand eintragen."""
    spezielle = _spezielle_effekte(volk)
    # aus der Eigenart "Klauen, Stufe 3" (volkseigenarten_config.json)
    try:
        pb_effekt = int(spezielle.get('panzerbrechend') or 0)
    except (TypeError, ValueError):
        pb_effekt = 0
    zuordnung = lade_config().get('volkseigenarten') or {}

    gefunden = set()
    for key, gruppe in zuordnung.items():
        wert = spezielle.get(key)
        if not wert:
            continue
        gefunden.add(gruppe)
        if isinstance(wert, str) and wert in kette:
            # eigene Abstammung: Würfel steht im Effekt; der PB-Effekt gehört
            # zur Eigenart "Klauen" und nicht zu Biss oder Hörnern
            wuerfel = wert
            pb = pb_effekt if gruppe in ('klauen', 'biss_klauen') else 0
        else:
            text = _volk_besonderheit(volk, gruppe)
            treffer = _WUERFEL_MUSTER.search(text)
            pb_treffer = _PB_MUSTER.search(text)
            wuerfel = treffer.group(1) if treffer else STANDARD_WUERFEL
            pb = int(pb_treffer.group(1)) if pb_treffer else 0
        _setze(zustand, gruppe, wuerfel, pb, kette)

    # Abstammungen, die die Waffe nur im Text führen (z. B. Horror-Vampir)
    for zeile in getattr(volk, 'besonderheiten', None) or []:
        text = str(zeile).strip()
        if _BEDINGT_MUSTER.search(text) or not _NATUERLICHE_WAFFE_MUSTER.search(text):
            continue
        treffer = _WUERFEL_MUSTER.search(text)
        if not treffer:
            continue
        for gruppe in _GRUPPEN_REIHENFOLGE:
            muster = _ZEILEN_MUSTER.get(gruppe)
            if not muster or gruppe in gefunden or not re.search(muster, text, re.IGNORECASE):
                continue
            pb_treffer = _PB_MUSTER.search(text)
            _setze(zustand, gruppe, treffer.group(1),
                   int(pb_treffer.group(1)) if pb_treffer else 0, kette)
            gefunden.add(gruppe)
            break


def _reihenfolge(eintrag):
    """
    Erst die Talente, die eine Waffe verleihen, dann die steigernden.

    Sonst hinge das Ergebnis an der Reihenfolge in der Konfiguration: Der Mönch
    (Waffenloser Schlag, Stä+W4) mit Kampfkünstler muss auf Stä+W6 kommen —
    Kampfkünstler steigert nur, wenn schon ein Würfel da ist.
    """
    index, (_, regel) = eintrag
    return (1 if regel.get('steigert') else 0, 0 if regel.get('grundwuerfel') else 1, index)


def _aus_talenten(charakter, zustand, kette):
    """Natürliche Waffen aus den gewählten Talenten in den Zustand eintragen."""
    gewaehlt = getattr(charakter, 'selected_talente', None) or []
    talente = lade_config().get('talente') or {}
    for _, (talent_name, regel) in sorted(enumerate(talente.items()), key=_reihenfolge):
        anzahl = sum(1 for t in gewaehlt if t == talent_name)
        if not anzahl:
            continue
        gruppe = regel.get('gruppe')
        wiederholung = regel.get('wiederholung') or {}
        for kopie in range(anzahl):
            aktiv = {**regel, **wiederholung} if kopie else regel
            eintrag = zustand.setdefault(gruppe, {"wuerfel": None, "pb": 0})
            if aktiv.get('setzt'):
                eintrag["wuerfel"] = _maximum(eintrag["wuerfel"], aktiv['setzt'], kette)
            elif eintrag["wuerfel"] is None and aktiv.get('grundwuerfel'):
                eintrag["wuerfel"] = aktiv['grundwuerfel']
            elif aktiv.get('steigert') and eintrag["wuerfel"]:
                eintrag["wuerfel"] = _steigere(eintrag["wuerfel"], aktiv['steigert'], kette)
            eintrag["pb"] = max(eintrag["pb"], int(aktiv.get('pb') or 0))


def _gewaehlte_voelker(charakter):
    """Die aktuell gewählten Volk-Objekte des Charakters."""
    voelker = getattr(charakter, 'voelker', None) or {}
    for volk_name, ausgewaehlt in (getattr(charakter, 'voelker_selected', None) or {}).items():
        if ausgewaehlt and volk_name in voelker:
            yield voelker[volk_name]


def abgeleitete_waffen(charakter):
    """
    Namen aller Ausrüstungs-Einträge, die Abstammung und Talente stellen.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        list: Namen in fester Gruppen-Reihenfolge, ohne Duplikate
    """
    try:
        config = lade_config()
        kette = list(config.get('wuerfel_kette') or [])
        gruppen = config.get('gruppen') or {}
        zustand = {}

        for volk in _gewaehlte_voelker(charakter):
            _aus_volk(volk, zustand, kette)
        _aus_talenten(charakter, zustand, kette)

        namen = []
        for gruppe in _GRUPPEN_REIHENFOLGE:
            eintrag = zustand.get(gruppe)
            if not eintrag or not eintrag["wuerfel"]:
                continue
            name = waffen_name(gruppen.get(gruppe, gruppe), eintrag["wuerfel"], eintrag["pb"])
            if name not in namen:
                namen.append(name)
        return namen

    except Exception as e:
        Logger.error(f"Fehler beim Ableiten der natürlichen Waffen: {e}")
        return []


def _einsammeln(charakter, item):
    """
    Nimmt eine gestellte Waffe zurück: Menge 0, raus aus den Auswahllisten.

    Der Katalog-Eintrag in charakter.ausruestung bleibt bestehen (anders als
    beim Verkauf), damit dieselbe Waffe später wieder gestellt werden kann —
    etwa wenn Kampfkunstmeister abgewählt wird und Kampfkünstler bleibt.
    """
    item.verringere_menge(item.menge)
    item.angelegt = False
    for liste_name in ('selected_waffen', 'selected_allgemeine_ausruestung'):
        liste = getattr(charakter, liste_name, None)
        if liste is not None and item in liste:
            liste.remove(item)


def synchronisiere(charakter):
    """
    Gleicht das Inventar mit den abgeleiteten natürlichen Waffen ab.

    Kostenlos und gewichtslos: die Waffen werden weder bezahlt noch erstattet.
    charakter.natuerliche_waffen hält fest, was zuletzt automatisch gestellt
    wurde — nur diese Einträge werden wieder entfernt, selbst gekaufte bleiben.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        list: Die jetzt automatisch gestellten Waffennamen
    """
    from functions.ausruestung_funktionen import _item_zu_ausruestung_hinzufuegen

    try:
        katalog = getattr(charakter, 'ausruestung', None) or {}
        neu = [name for name in abgeleitete_waffen(charakter) if name in katalog]
        alt = list(getattr(charakter, 'natuerliche_waffen', None) or [])

        # Nicht mehr abgeleitete Waffen wieder einsammeln
        for name in alt:
            if name in neu:
                continue
            item = katalog.get(name)
            if not item:
                continue
            _einsammeln(charakter, item)
            Logger.info(f"Natürliche Waffe '{name}' entfernt (nicht mehr abgeleitet)")

        gestellt = []
        for name in neu:
            item = katalog.get(name)
            besitzt = getattr(item, 'menge', 0) > 0
            if name not in alt and besitzt:
                # bereits selbst gekauft — dann bleibt es in der Hand des Spielers
                continue
            if not besitzt:
                item.erhoehe_menge(1)
                _item_zu_ausruestung_hinzufuegen(charakter, item)
                Logger.info(f"Natürliche Waffe '{name}' kostenlos ins Inventar gelegt")
            gestellt.append(name)

        charakter.natuerliche_waffen = gestellt
        return gestellt

    except Exception as e:
        Logger.error(f"Fehler beim Synchronisieren der natürlichen Waffen: {e}")
        return list(getattr(charakter, 'natuerliche_waffen', None) or [])


def ist_natuerliche_waffe(charakter, item_name):
    """True, wenn der Eintrag aktuell automatisch aus Abstammung/Talenten stammt."""
    return item_name in (getattr(charakter, 'natuerliche_waffen', None) or [])
