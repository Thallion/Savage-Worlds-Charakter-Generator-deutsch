# functions/charakter_speicher.py

import json
import os
from kivy.logger import Logger
from pathlib import Path
from models.volk import Volk
from models.handicap import Handicap
from models.talent import Talent
from models.macht import Macht
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild
from models.ausruestung import Ausruestung
from models.wuerfel import Wuerfel
from models.attribut import Attribut
from models.fertigkeit import Fertigkeit

class SetEncoder(json.JSONEncoder):
    """Ermöglicht das Serialisieren von Sets in JSON."""
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

def speichern_als_json(charakter, dateipfad):
    """
    Speichert einen Charakter als JSON-Datei.
    
    Args:
        charakter: Das zu speichernde Charakterobjekt
        dateipfad: Der Pfad zur Zieldatei
    """
    try:
        charakter_daten = to_dict(charakter)
        with open(dateipfad, 'w', encoding='utf-8') as f:
            json.dump(charakter_daten, f, ensure_ascii=False, indent=4, cls=SetEncoder)
        Logger.info(f"Charakter erfolgreich in {dateipfad} gespeichert.")
    except Exception as e:
        Logger.error(f"Fehler beim Speichern des Charakters: {e}")

def laden_von_json(charakter, dateipfad):
    """
    Lädt einen Charakter aus einer JSON-Datei.
    
    Args:
        charakter: Das Charakterobjekt, in das die Daten geladen werden sollen
        dateipfad: Der Pfad zur Quelldatei
    """
    try:
        with open(dateipfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)

        from_dict(charakter, daten)
        Logger.info(f"Charakter erfolgreich von {dateipfad} geladen.")

        charakter.voelker_selected = daten.get('voelker_selected', charakter.voelker_selected)
        charakter.active_setting_name = daten.get('active_setting_name', charakter.active_setting_name)

        # Setting aktivieren
        if charakter.custom_element_manager:
            success = charakter.custom_element_manager.set_active_setting(charakter.active_setting_name)
            if not success:
                Logger.warning(f"Das Setting '{charakter.active_setting_name}' konnte nicht aktiviert werden. Verwende Standard-Setting.")
                charakter.active_setting_name = "SWAE"
                charakter.custom_element_manager.set_active_setting(charakter.active_setting_name)

    except Exception as e:
        Logger.error(f"Fehler beim Laden des Charakters: {e}")

def to_dict(charakter):
    """
    Konvertiert ein Charakterobjekt in ein Dictionary.
    
    Args:
        charakter: Das zu konvertierende Charakterobjekt
        
    Returns:
        dict: Ein Dictionary mit den Charakterdaten
    """
    # Sicherstellen, dass selected_handicaps aktualisiert sind
    # alle Handicaps, die ausgewaehlt sind, in selected_handicaps aufnehmen
    charakter.selected_handicaps = [name for name, handicap in charakter.handicaps.items() if handicap.ausgewaehlt]

    return {
        'profil_daten': charakter.profil_daten,
        "voelker": {name: volk.to_setting_dict() for name, volk in charakter.voelker.items()},
        'attribute': {name: attribut.to_dict() for name, attribut in charakter.attribute.items()},
        'fertigkeiten': {name: fertigkeit.to_dict() for name, fertigkeit in charakter.fertigkeiten.items()},
        'handicaps': {name: handicap.to_dict() for name, handicap in charakter.handicaps.items()},
        'talente': {name: talent.to_dict() for name, talent in charakter.talente.items()},
        'maechte': {name: macht.to_dict() for name, macht in charakter.maechte.items()},
        "ausruestung": {name: ausruestung.to_dict() for name, ausruestung in charakter.ausruestung.items()},
        'selected_handicaps': charakter.selected_handicaps,
        'selected_talente': charakter.selected_talente,
        'selected_maechte': charakter.selected_maechte,
        'selected_allgemeine_ausruestung': [item.name for item in charakter.selected_allgemeine_ausruestung],
        'selected_waffen': [item.name for item in charakter.selected_waffen],
        'selected_ruestungen': [item.name for item in charakter.selected_ruestungen],
        'selected_schilde': [item.name for item in charakter.selected_schilde],
        'voelker_selected': charakter.voelker_selected,
        'verbleibende_attributsteigerungen': charakter.verbleibende_attributsteigerungen,
        'verbleibende_fertigkeitssteigerungen': charakter.verbleibende_fertigkeitssteigerungen,
        'maximale_attributsteigerungen': charakter.maximale_attributsteigerungen,
        'maximale_fertigkeitssteigerungen': charakter.maximale_fertigkeitssteigerungen,
        'verbleibende_aufstiege': charakter.verbleibende_aufstiege,
        'aufstiege_gesamt': charakter.aufstiege_gesamt,
        'verfuegbare_maechte': charakter.verfuegbare_maechte,
        'machtpunkte': charakter.machtpunkte,
        'vermoegen': charakter.vermoegen,
        'erschoepfung': charakter.erschoepfung,
        'zusaetzliche_talente': charakter.zusaetzliche_talente,
        'gesamt_handicap_punkte': charakter.gesamt_handicap_punkte,
        'settingregeln': charakter.settingregeln.to_dict(),
        'active_setting_name': charakter.custom_element_manager.active_setting_name
    }

def from_dict(charakter, data):
    """
    Lädt Daten aus einem Dictionary in ein Charakterobjekt.
    
    Args:
        charakter: Das Charakterobjekt, in das die Daten geladen werden
        data: Das Quelldictionary mit den Charakterdaten
    """
    # Profildaten setzen
    for key, value in data.get('profil_daten', {}).items():
        charakter.set_profil_daten(key, value)

    # Völker laden
    voelker_data = data.get('voelker', {})
    charakter.voelker = {}
    for name, volk_dict in voelker_data.items():
        charakter.voelker[name] = Volk.from_dict(volk_dict)
    Logger.info("Völker geladen.")

    # Völker-Auswahl laden
    charakter.voelker_selected = data.get('voelker_selected', {})
    for name, selected in charakter.voelker_selected.items():
        if name in charakter.voelker:
            charakter.voelker[name].ausgewaehlt = selected
        else:
            Logger.warning(f"Volk '{name}' existiert nicht in den geladenen Völkern.")

    # Attribute laden
    attribute_data = data.get('attribute', {})
    for name, attr_data in attribute_data.items():
        charakter.attribute[name] = Attribut.from_dict_static(attr_data)

    # Fertigkeiten laden
    fertigkeiten_data = data.get('fertigkeiten', {})
    for name, fert_data in fertigkeiten_data.items():
        charakter.fertigkeiten[name] = Fertigkeit.from_dict_static(fert_data, charakter.attribute)

    # Handicaps laden
    handicaps_data = data.get('handicaps', {})
    for name_key, handicap_data in handicaps_data.items():
        # Prüfen ob es schon ein Handicap mit diesem Namen gibt
        if name_key in charakter.handicaps:
            # Existierendes Handicap aktualisieren
            charakter.handicaps[name_key].update_from_dict(handicap_data)
        else:
            # Handicap neu erzeugen, falls es noch nicht existiert
            charakter.handicaps[name_key] = Handicap.from_dict_static(handicap_data)

    charakter.selected_handicaps = [name for name, handicap in charakter.handicaps.items() if handicap.ausgewaehlt]

    # Talente laden
    talente_data = data.get('talente', {})
    for name_key, talent_data in talente_data.items():
        charakter.talente[name_key] = Talent.from_dict_static(talent_data)
        if name_key not in charakter.custom_element_manager.active_setting['talente']:
            charakter.custom_element_manager.active_setting['talente'][name_key] = talent_data

    # Mächte laden
    maechte_data = data.get('maechte', {})
    for name_key, macht_data in maechte_data.items():
        charakter.maechte[name_key] = Macht.from_dict_static(macht_data)
        if name_key not in charakter.custom_element_manager.active_setting['maechte']:
            charakter.custom_element_manager.active_setting['maechte'][name_key] = macht_data

    # Ausrüstung laden
    ausruestung_data = data.get('ausruestung', {})
    charakter.ausruestung = {}
    for name, item_data in ausruestung_data.items():
        kategorie = item_data.get('kategorie', 'Allgemein')
        if kategorie == 'Waffe':
            item = Waffe.from_dict_static(item_data)
        elif kategorie == 'Rüstung':
            item = Ruestung.from_dict_static(item_data)
        elif kategorie == 'Schild':
            item = Schild.from_dict_static(item_data)
        else:
            item = Ausruestung.from_dict_static(item_data)

        item.menge = item_data.get('menge', 0)
        item.ausgewaehlt = item_data.get('ausgewaehlt', False)
        item.aktiv = item_data.get('aktiv', True)
        item.angelegt = item_data.get('angelegt', False)

        charakter.ausruestung[name] = item

        if name not in charakter.custom_element_manager.active_setting['ausruestung']:
            charakter.custom_element_manager.active_setting['ausruestung'][name] = item_data

    # Ausgewählte Talente wiederherstellen
    charakter.selected_talente = data.get('selected_talente', [])
    for name_key in charakter.selected_talente:
        if name_key in charakter.talente:
            charakter.talente[name_key].ausgewaehlt = True
        else:
            Logger.warning(f"Talent '{name_key}' nicht in self.talente gefunden.")

    # Ausgewählte Mächte wiederherstellen
    charakter.selected_maechte = data.get('selected_maechte', [])
    for name_key in charakter.selected_maechte:
        if name_key in charakter.maechte:
            charakter.maechte[name_key].ausgewaehlt = True
        else:
            Logger.warning(f"Macht '{name_key}' nicht in self.maechte gefunden.")

    # Ausgewählte Waffen wiederherstellen
    selected_waffen_names = data.get('selected_waffen', [])
    charakter.selected_waffen = []
    for name in selected_waffen_names:
        if name in charakter.ausruestung:
            waffe = charakter.ausruestung[name]
            waffe.angelegt = True
            charakter.selected_waffen.append(waffe)
            Logger.debug(f"Waffe '{waffe.name}' als angelegt markiert.")
        else:
            Logger.warning(f"Waffe '{name}' nicht in self.ausruestung gefunden.")

    # Setze angelegt=False für andere Waffen
    for waffe in charakter.ausruestung.values():
        if isinstance(waffe, Waffe) and waffe.name not in selected_waffen_names:
            if waffe.angelegt:
                waffe.angelegt = False
                Logger.debug(f"Waffe '{waffe.name}' als nicht angelegt markiert.")

    # Ausgewählte Schilde wiederherstellen
    selected_schilde_names = data.get('selected_schilde', [])
    charakter.selected_schilde = []
    for name in selected_schilde_names:
        if name in charakter.ausruestung:
            schild = charakter.ausruestung[name]
            schild.angelegt = True
            charakter.selected_schilde.append(schild)
            Logger.debug(f"Schild '{schild.name}' als angelegt markiert.")
        else:
            Logger.warning(f"Schild '{name}' nicht in self.ausruestung gefunden.")

    # Setze angelegt=False für andere Schilde
    for schild in charakter.ausruestung.values():
        if isinstance(schild, Schild) and schild.name not in selected_schilde_names:
            if schild.angelegt:
                schild.angelegt = False
                Logger.debug(f"Schild '{schild.name}' als nicht angelegt markiert.")

    # Ausgewählte Rüstungen wiederherstellen
    selected_ruestungen_names = data.get('selected_ruestungen', [])
    charakter.selected_ruestungen = []
    for name in selected_ruestungen_names:
        if name in charakter.ausruestung:
            ruestung = charakter.ausruestung[name]
            ruestung.angelegt = True
            charakter.selected_ruestungen.append(ruestung)
            Logger.debug(f"Rüstung '{ruestung.name}' als angelegt markiert.")
        else:
            Logger.warning(f"Rüstung '{name}' nicht in self.ausruestung gefunden.")

    # Setze angelegt=False für andere Rüstungen
    for ruestung in charakter.ausruestung.values():
        if isinstance(ruestung, Ruestung) and ruestung.name not in selected_ruestungen_names:
            if ruestung.angelegt:
                ruestung.angelegt = False
                Logger.debug(f"Rüstung '{ruestung.name}' als nicht angelegt markiert.")

    # Ausgewählte allgemeine Ausrüstung wiederherstellen
    selected_allgemeine_ausruestung_names = data.get('selected_allgemeine_ausruestung', [])
    charakter.selected_allgemeine_ausruestung = [charakter.ausruestung[name] for name in selected_allgemeine_ausruestung_names if name in charakter.ausruestung]

    # Zuweisungen der anderen Werte
    charakter.verbleibende_attributsteigerungen = data.get('verbleibende_attributsteigerungen', charakter.verbleibende_attributsteigerungen)
    charakter.verbleibende_fertigkeitssteigerungen = data.get('verbleibende_fertigkeitssteigerungen', charakter.verbleibende_fertigkeitssteigerungen)
    charakter.maximale_attributsteigerungen = data.get('maximale_attributsteigerungen', charakter.maximale_attributsteigerungen)
    charakter.maximale_fertigkeitssteigerungen = data.get('maximale_fertigkeitssteigerungen', charakter.maximale_fertigkeitssteigerungen)
    charakter.verbleibende_aufstiege = data.get('verbleibende_aufstiege', charakter.verbleibende_aufstiege)
    charakter.aufstiege_gesamt = data.get('aufstiege_gesamt', charakter.aufstiege_gesamt)
    charakter.verfuegbare_maechte = data.get('verfuegbare_maechte', charakter.verfuegbare_maechte)
    charakter.machtpunkte = data.get('machtpunkte', charakter.machtpunkte)
    charakter.vermoegen = data.get('vermoegen', charakter.vermoegen)
    charakter.erschoepfung = data.get('erschoepfung', charakter.erschoepfung)
    charakter.zusaetzliche_talente = data.get('zusaetzliche_talente', charakter.zusaetzliche_talente)
    charakter.gesamt_handicap_punkte = data.get('gesamt_handicap_punkte', charakter.gesamt_handicap_punkte)

    # Aktiven Setting-Namen setzen und Setting aktivieren
    charakter.active_setting_name = data.get('active_setting_name', charakter.active_setting_name)
    Logger.debug(f"Active Setting Name gesetzt auf: {charakter.active_setting_name}")

    success = charakter.custom_element_manager.set_active_setting(charakter.active_setting_name)
    if success:
        Logger.debug(f"Setting '{charakter.active_setting_name}' erfolgreich aktiviert.")
    else:
        Logger.error(f"Setting '{charakter.active_setting_name}' konnte nicht aktiviert werden.")

    # UI aktualisieren
    charakter.dispatch('on_charakter_change')