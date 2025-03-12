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
        'active_setting_name': charakter.custom_element_manager.active_setting_name,
        'char_gen_completed': charakter.char_gen_completed  # Hinzugefügt
    }

def from_dict(self, data):
    """
    Lädt Daten aus einem Dictionary in das Charakterobjekt.
    
    Args:
        data (dict): Ein Dictionary mit Charakterdaten
    """
    try:
        # Profildaten setzen
        for key, value in data.get('profil_daten', {}).items():
            self.set_profil_daten(key, value)
            if key == "Name":
                self.char_name = value

        # Völker laden
        voelker_data = data.get('voelker', {})
        self.voelker = {}
        for name, volk_dict in voelker_data.items():
            try:
                self.voelker[name] = Volk.from_dict(volk_dict)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Volkes '{name}': {e}")
        Logger.info("Völker geladen.")

        # Völker-Auswahl laden
        self.voelker_selected = data.get('voelker_selected', {})
        for name, selected in self.voelker_selected.items():
            if name in self.voelker:
                self.voelker[name].ausgewaehlt = selected
            else:
                Logger.warning(f"Volk '{name}' existiert nicht in den geladenen Völkern.")

        # Attribute laden
        attribute_data = data.get('attribute', {})
        self.attribute = {}  # Zurücksetzen um Duplikate zu vermeiden
        for name, attr_data in attribute_data.items():
            try:
                self.attribute[name] = Attribut.from_dict_static(attr_data)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Attributs '{name}': {e}")

        # Fertigkeiten laden
        fertigkeiten_data = data.get('fertigkeiten', {})
        self.fertigkeiten = {}  # Zurücksetzen um Duplikate zu vermeiden
        for name, fert_data in fertigkeiten_data.items():
            try:
                self.fertigkeiten[name] = Fertigkeit.from_dict_static(fert_data, self.attribute)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden der Fertigkeit '{name}': {e}")

        # Handicaps laden und zurücksetzen
        self.handicaps = {}
        handicaps_data = data.get('handicaps', {})
        for name_key, handicap_data in handicaps_data.items():
            try:
                self.handicaps[name_key] = Handicap.from_dict_static(handicap_data)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Handicaps '{name_key}': {e}")

        self.selected_handicaps = data.get('selected_handicaps', [])
        # Synchronisiere die ausgewählt-Eigenschaft in den handicaps mit selected_handicaps
        for name, handicap in self.handicaps.items():
            handicap.ausgewaehlt = name in self.selected_handicaps

        # Talente laden und zurücksetzen
        self.talente = {}
        talente_data = data.get('talente', {})
        for name_key, talent_data in talente_data.items():
            try:
                self.talente[name_key] = Talent.from_dict_static(talent_data)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Talents '{name_key}': {e}")

        # Mächte laden und zurücksetzen
        self.maechte = {}
        maechte_data = data.get('maechte', {})
        for name_key, macht_data in maechte_data.items():
            try:
                self.maechte[name_key] = Macht.from_dict_static(macht_data)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden der Macht '{name_key}': {e}")

        # Ausrüstung laden und zurücksetzen
        self.ausruestung = {}
        ausruestung_data = data.get('ausruestung', {})
        for name, item_data in ausruestung_data.items():
            try:
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

                self.ausruestung[name] = item
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Ausrüstungsgegenstands '{name}': {e}")

        # Ausgewählte Talente wiederherstellen
        self.selected_talente = data.get('selected_talente', [])
        for name_key in self.selected_talente:
            if name_key in self.talente:
                self.talente[name_key].ausgewaehlt = True
            else:
                Logger.warning(f"Talent '{name_key}' nicht in self.talente gefunden.")

        # Ausgewählte Mächte wiederherstellen
        self.selected_maechte = data.get('selected_maechte', [])
        for name_key in self.selected_maechte:
            if name_key in self.maechte:
                self.maechte[name_key].ausgewaehlt = True
            else:
                Logger.warning(f"Macht '{name_key}' nicht in self.maechte gefunden.")

        # Ausrüstungslisten zurücksetzen
        self.selected_waffen = []
        self.selected_schilde = []
        self.selected_ruestungen = []
        self.selected_allgemeine_ausruestung = []

        # Ausgewählte Waffen wiederherstellen
        selected_waffen_names = data.get('selected_waffen', [])
        for name in selected_waffen_names:
            if name in self.ausruestung:
                waffe = self.ausruestung[name]
                if isinstance(waffe, Waffe):
                    waffe.angelegt = True
                    self.selected_waffen.append(waffe)
                    Logger.debug(f"Waffe '{waffe.name}' als angelegt markiert.")
                else:
                    Logger.warning(f"'{name}' ist keine Waffe, sondern {type(waffe).__name__}")
            else:
                Logger.warning(f"Waffe '{name}' nicht in self.ausruestung gefunden.")

        # Ausgewählte Schilde wiederherstellen
        selected_schilde_names = data.get('selected_schilde', [])
        for name in selected_schilde_names:
            if name in self.ausruestung:
                schild = self.ausruestung[name]
                if isinstance(schild, Schild):
                    schild.angelegt = True
                    self.selected_schilde.append(schild)
                    Logger.debug(f"Schild '{schild.name}' als angelegt markiert.")
                else:
                    Logger.warning(f"'{name}' ist kein Schild, sondern {type(schild).__name__}")
            else:
                Logger.warning(f"Schild '{name}' nicht in self.ausruestung gefunden.")

        # Ausgewählte Rüstungen wiederherstellen
        selected_ruestungen_names = data.get('selected_ruestungen', [])
        for name in selected_ruestungen_names:
            if name in self.ausruestung:
                ruestung = self.ausruestung[name]
                if isinstance(ruestung, Ruestung):
                    ruestung.angelegt = True
                    self.selected_ruestungen.append(ruestung)
                    Logger.debug(f"Rüstung '{ruestung.name}' als angelegt markiert.")
                else:
                    Logger.warning(f"'{name}' ist keine Rüstung, sondern {type(ruestung).__name__}")
            else:
                Logger.warning(f"Rüstung '{name}' nicht in self.ausruestung gefunden.")

        # Ausgewählte allgemeine Ausrüstung wiederherstellen
        selected_allgemeine_ausruestung_names = data.get('selected_allgemeine_ausruestung', [])
        for name in selected_allgemeine_ausruestung_names:
            if name in self.ausruestung:
                item = self.ausruestung[name]
                if not isinstance(item, (Waffe, Ruestung, Schild)):
                    self.selected_allgemeine_ausruestung.append(item)
                    Logger.debug(f"Allgemeiner Ausrüstungsgegenstand '{item.name}' ausgewählt.")
                else:
                    Logger.warning(f"'{name}' ist kein allgemeiner Ausrüstungsgegenstand.")
            else:
                Logger.warning(f"Ausrüstungsgegenstand '{name}' nicht in self.ausruestung gefunden.")

        # Zuweisungen der anderen Werte
        self.verbleibende_attributsteigerungen = data.get('verbleibende_attributsteigerungen', self.verbleibende_attributsteigerungen)
        self.verbleibende_fertigkeitssteigerungen = data.get('verbleibende_fertigkeitssteigerungen', self.verbleibende_fertigkeitssteigerungen)
        self.maximale_attributsteigerungen = data.get('maximale_attributsteigerungen', self.maximale_attributsteigerungen)
        self.maximale_fertigkeitssteigerungen = data.get('maximale_fertigkeitssteigerungen', self.maximale_fertigkeitssteigerungen)
        self.verbleibende_aufstiege = data.get('verbleibende_aufstiege', self.verbleibende_aufstiege)
        self.aufstiege_gesamt = data.get('aufstiege_gesamt', self.aufstiege_gesamt)
        self.verfuegbare_maechte = data.get('verfuegbare_maechte', self.verfuegbare_maechte)
        self.machtpunkte = data.get('machtpunkte', self.machtpunkte)
        self.vermoegen = data.get('vermoegen', self.vermoegen)
        self.erschoepfung = data.get('erschoepfung', self.erschoepfung)
        self.zusaetzliche_talente = data.get('zusaetzliche_talente', self.zusaetzliche_talente)
        self.gesamt_handicap_punkte = data.get('gesamt_handicap_punkte', self.gesamt_handicap_punkte)
        self.char_gen_completed = data.get('char_gen_completed', self.char_gen_completed) 

        # Setting-Einstellungen
        if 'settingregeln' in data:
            try:
                settingregeln_data = data.get('settingregeln', {})
                if self.settingregeln:
                    self.settingregeln.from_dict(settingregeln_data)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden der Settingregeln: {e}")

        # Aktives Setting setzen
        self.active_setting_name = data.get('active_setting_name', "SWAE")
        Logger.info(f"Active Setting Name aus Datei: {self.active_setting_name}")

        # UI aktualisieren (optional hier - wird auch im laden_von_json aufgerufen)
        self.dispatch('on_charakter_change')
    except Exception as e:
        Logger.error(f"Kritischer Fehler in from_dict: {e}", exc_info=True)
        raise

