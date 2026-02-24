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
from models.superkraft import Superkraft

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
    OPTIMIERT: Speichert nur die tatsächlichen Charakterdaten, nicht die kompletten Setting-Elemente
    
    Args:
        charakter: Das zu konvertierende Charakterobjekt
        
    Returns:
        dict: Ein Dictionary mit den Charakterdaten (ohne komplette Setting-Daten)
    """
    # Sicherstellen, dass selected_handicaps aktualisiert sind
    charakter.selected_handicaps = [name for name, handicap in charakter.handicaps.items() if handicap.ausgewaehlt]

    # Pathfinder-spezifische Attribute mit Standardwerten
    pathfinder_kostenlose_talente_gewaehlt = getattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt', 0)

    # Nur die ausgewählten/gekauften Elemente mit ihren individuellen Daten speichern
    selected_elements = _get_selected_elements_with_data(charakter)
    
    return {
        # === GRUNDDATEN ===
        'profil_daten': charakter.profil_daten,
        'active_setting_name': charakter.custom_element_manager.active_setting_name,
        'char_gen_completed': charakter.char_gen_completed,
        'settingregeln': charakter.settingregeln.to_dict(),
        
        # === ATTRIBUTE UND FERTIGKEITEN ===
        'attribute': {name: attribut.to_dict() for name, attribut in charakter.attribute.items()},
        'fertigkeiten': {name: fertigkeit.to_dict() for name, fertigkeit in charakter.fertigkeiten.items()},
        
        # === NUR AUSGEWÄHLTE ELEMENTE MIT INDIVIDUELLEN DATEN ===
        'selected_elements': selected_elements,
        
        # === AUSWAHL-LISTEN (nur Namen/IDs) ===
        'selected_handicaps': charakter.selected_handicaps,
        'selected_talente': charakter.selected_talente,
        'selected_maechte': charakter.selected_maechte,
        'selected_superkraefte': charakter.selected_superkraefte,
        'voelker_selected': charakter.voelker_selected,
        'selected_allgemeine_ausruestung': [item.name for item in charakter.selected_allgemeine_ausruestung],
        'selected_waffen': [item.name for item in charakter.selected_waffen],
        'selected_ruestungen': [item.name for item in charakter.selected_ruestungen],
        'selected_schilde': [item.name for item in charakter.selected_schilde],
        
        # === CHARAKTER-STATUS ===
        'verbleibende_attributsteigerungen': charakter.verbleibende_attributsteigerungen,
        'verbleibende_fertigkeitssteigerungen': charakter.verbleibende_fertigkeitssteigerungen,
        'maximale_attributsteigerungen': charakter.maximale_attributsteigerungen,
        'maximale_fertigkeitssteigerungen': charakter.maximale_fertigkeitssteigerungen,
        'verbleibende_aufstiege': charakter.verbleibende_aufstiege,
        'aufstiege_gesamt': charakter.aufstiege_gesamt,
        'verfuegbare_maechte': charakter.verfuegbare_maechte,
        'anzahl_maechte': charakter.anzahl_maechte,
        'machtpunkte': charakter.machtpunkte,
        'machtstufe': charakter.machtstufe,
        'superkraft_punkte_gesamt': charakter.superkraft_punkte_gesamt,
        'superkraft_punkte_verbraucht': charakter.superkraft_punkte_verbraucht,
        'kraftobergrenze': charakter.kraftobergrenze,
        'vermoegen': charakter.vermoegen,
        'erschoepfung': charakter.erschoepfung,
        'zusaetzliche_talente': charakter.zusaetzliche_talente,
        'gesamt_handicap_punkte': charakter.gesamt_handicap_punkte,
        'pathfinder_kostenlose_talente_gewaehlt': pathfinder_kostenlose_talente_gewaehlt,

        # === STEIGERUNGS-JOURNAL ===
        'steigerungs_journal': charakter.steigerungs_journal
    }

def _get_selected_elements_with_data(charakter):
    """
    Extrahiert nur die ausgewählten Elemente mit ihren individuellen Charakterdaten
    
    Returns:
        dict: Dictionary mit nur den ausgewählten Elementen und deren individuellen Daten
    """
    selected_elements = {
        'voelker': {},
        'handicaps': {},
        'talente': {},
        'maechte': {},
        'superkraefte': {},
        'ausruestung': {}
    }
    
    # Nur ausgewählte Völker mit individuellen Daten
    if hasattr(charakter, 'voelker_selected'):
        for name, selected in charakter.voelker_selected.items():
            if selected and name in charakter.voelker:
                # Nur individuelle Charakterdaten, nicht die komplette Setting-Definition
                selected_elements['voelker'][name] = {
                    'ausgewaehlt': True,
                    # Hier könnten weitere individuelle Daten hinzugefügt werden
                }
    
    # Nur ausgewählte Handicaps mit individuellen Daten
    for name, handicap in charakter.handicaps.items():
        if handicap.ausgewaehlt:
            handicap_dict = {
                'ausgewaehlt': True,
                'stufe': handicap.stufe,
                'punkte': handicap.punkte,
            }
            if hasattr(handicap, 'individuelle_beschreibung') and handicap.individuelle_beschreibung:
                handicap_dict['beschreibung'] = handicap.individuelle_beschreibung
            selected_elements['handicaps'][name] = handicap_dict
    
    # Nur ausgewählte Talente mit individuellen Daten
    for talent_name in charakter.selected_talente:
        if talent_name in charakter.talente:
            talent = charakter.talente[talent_name]
            talent_dict = {
                'ausgewaehlt': True,
                'rang': talent.rang,
                'neue_maechte': talent.neue_maechte,
                'machtpunkte': talent.machtpunkte,
            }
            if hasattr(talent, 'individuelle_beschreibung') and talent.individuelle_beschreibung:
                talent_dict['beschreibung'] = talent.individuelle_beschreibung
            selected_elements['talente'][talent_name] = talent_dict
    
    # Nur ausgewählte Mächte mit individuellen Daten
    for macht_name in charakter.selected_maechte:
        if macht_name in charakter.maechte:
            macht = charakter.maechte[macht_name]
            macht_dict = {
                'ausgewaehlt': True,
                'rang': macht.rang,
                'machtpunkte': macht.machtpunkte,
                'reichweite': macht.reichweite,
                'dauer': macht.dauer,
            }
            if hasattr(macht, 'individuelle_beschreibung') and macht.individuelle_beschreibung:
                macht_dict['beschreibung'] = macht.individuelle_beschreibung
            selected_elements['maechte'][macht_name] = macht_dict
    
    # Nur ausgewählte Superkräfte mit individuellen Daten
    for kraft_name in getattr(charakter, 'selected_superkraefte', []):
        if kraft_name in getattr(charakter, 'superkraefte', {}):
            kraft = charakter.superkraefte[kraft_name]
            kraft_dict = {
                'ausgewaehlt': True,
                'gewaehlte_kosten': kraft.gewaehlte_kosten,
                'gewaehlte_modifikatoren': [mod.to_dict() for mod in kraft.gewaehlte_modifikatoren],
            }
            selected_elements['superkraefte'][kraft_name] = kraft_dict

    # Nur ausgewählte Ausrüstung mit individuellen Daten
    all_selected_equipment = (
        charakter.selected_allgemeine_ausruestung + 
        charakter.selected_waffen + 
        charakter.selected_ruestungen + 
        charakter.selected_schilde
    )
    
    for item in all_selected_equipment:
        if hasattr(item, 'name') and item.name in charakter.ausruestung:
            selected_elements['ausruestung'][item.name] = {
                'ausgewaehlt': True,
                'anzahl': getattr(item, 'anzahl', 1),
                'zustand': getattr(item, 'zustand', 'neu'),
                # Weitere individuelle Daten falls vorhanden
            }
    
    return selected_elements

def from_dict(self, data):
    """
    Lädt Daten aus einem Dictionary in das Charakterobjekt.
    ÜBERARBEITET: Unterstützt sowohl altes Format (mit kompletten Setting-Daten) 
    als auch neues Format (nur mit ausgewählten Elementen + Setting-Referenz)
    
    Args:
        data (dict): Ein Dictionary mit Charakterdaten
    """
    try:
        # Profildaten setzen
        for key, value in data.get('profil_daten', {}).items():
            self.set_profil_daten(key, value)
            if key == "Name":
                self.char_name = value

        # Setting-Name setzen
        setting_name = data.get('active_setting_name', 'SWAE')
        self.active_setting_name = setting_name

        # Prüfen ob neues Format (nur selected_elements) oder altes Format (komplette Daten)
        if 'selected_elements' in data:
            # NEUES FORMAT: Nur ausgewählte Elemente laden
            Logger.info("Lade Charakter mit neuem Format (nur ausgewählte Elemente)")
            _load_new_format(self, data)
        else:
            # ALTES FORMAT: Komplette Setting-Daten in Charakter-Datei
            Logger.info("Lade Charakter mit altem Format (komplette Setting-Daten)")
            _load_old_format(self, data)

        # Gemeinsame Nachbearbeitung für beide Formate
        _finalize_character_loading(self, data)
        
    except Exception as e:
        Logger.error(f"Fehler beim Laden der Charakterdaten: {e}")
        raise


def _load_new_format(charakter, data):
    """
    Lädt Charakter im neuen Format (nur ausgewählte Elemente + Setting-Referenz)
    """
    # Setting aktivieren und alle verfügbaren Elemente laden
    charakter.custom_element_manager.set_active_setting(charakter.active_setting_name)
    charakter.load_elements_from_active_setting(replace_mode=True)
    
    # Attribute und Fertigkeiten laden (werden immer vollständig gespeichert)
    _load_attributes_and_skills(charakter, data)
    
    # Nur die ausgewählten Elemente mit ihren individuellen Daten laden
    selected_elements = data.get('selected_elements', {})
    
    # Auswahl-Listen laden
    charakter.selected_handicaps = data.get('selected_handicaps', [])
    charakter.selected_talente = data.get('selected_talente', [])
    charakter.selected_maechte = data.get('selected_maechte', [])
    charakter.selected_superkraefte = data.get('selected_superkraefte', [])
    charakter.voelker_selected = data.get('voelker_selected', {})
    
    # Individuelle Daten auf die Setting-Elemente anwenden
    _apply_individual_element_data(charakter, selected_elements)
    
    # Ausrüstungslisten laden
    _load_equipment_selections(charakter, data)


def _load_old_format(charakter, data):
    """
    Lädt Charakter im alten Format (komplette Setting-Daten in Charakter-Datei)
    """
    # Attribute und Fertigkeiten laden
    _load_attributes_and_skills(charakter, data)
    
    # Völker laden
    voelker_data = data.get('voelker', {})
    charakter.voelker = {}
    for name, volk_dict in voelker_data.items():
        try:
            charakter.voelker[name] = Volk.from_dict(volk_dict)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden des Volkes '{name}': {e}")

    # Völker-Auswahl laden
    charakter.voelker_selected = data.get('voelker_selected', {})
    for name, selected in charakter.voelker_selected.items():
        if name in charakter.voelker:
            charakter.voelker[name].ausgewaehlt = selected

    # Handicaps laden
    charakter.handicaps = {}
    handicaps_data = data.get('handicaps', {})
    for name_key, handicap_data in handicaps_data.items():
        try:
            charakter.handicaps[name_key] = Handicap.from_dict_static(handicap_data)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden des Handicaps '{name_key}': {e}")

    charakter.selected_handicaps = data.get('selected_handicaps', [])
    for name, handicap in charakter.handicaps.items():
        handicap.ausgewaehlt = name in charakter.selected_handicaps

    # Talente laden
    charakter.talente = {}
    talente_data = data.get('talente', {})
    for name_key, talent_data in talente_data.items():
        try:
            charakter.talente[name_key] = Talent.from_dict_static(talent_data)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden des Talents '{name_key}': {e}")

    charakter.selected_talente = data.get('selected_talente', [])
    for name_key in charakter.selected_talente:
        if name_key in charakter.talente:
            charakter.talente[name_key].ausgewaehlt = True

    # Mächte laden
    charakter.maechte = {}
    maechte_data = data.get('maechte', {})
    for name_key, macht_data in maechte_data.items():
        try:
            charakter.maechte[name_key] = Macht.from_dict_static(macht_data)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden der Macht '{name_key}': {e}")

    charakter.selected_maechte = data.get('selected_maechte', [])
    for name_key in charakter.selected_maechte:
        if name_key in charakter.maechte:
            charakter.maechte[name_key].ausgewaehlt = True

    # Ausrüstung laden
    charakter.ausruestung = {}
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
            charakter.ausruestung[name] = item
        except Exception as e:
            Logger.warning(f"Fehler beim Laden des Ausrüstungsgegenstands '{name}': {e}")

    # Auswahllisten für altes Format laden
    _load_old_format_selections(charakter, data)


def _load_attributes_and_skills(charakter, data):
    """
    Lädt Attribute und Fertigkeiten (beide Formate verwenden diese Daten vollständig)
    """
    # Attribute laden
    attribute_data = data.get('attribute', {})
    charakter.attribute = {}
    for name, attr_data in attribute_data.items():
        try:
            charakter.attribute[name] = Attribut.from_dict_static(attr_data)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden des Attributs '{name}': {e}")

    # Fertigkeiten laden
    fertigkeiten_data = data.get('fertigkeiten', {})
    charakter.fertigkeiten = {}
    for name, fert_data in fertigkeiten_data.items():
        try:
            charakter.fertigkeiten[name] = Fertigkeit.from_dict_static(fert_data, charakter.attribute)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden der Fertigkeit '{name}': {e}")


def _apply_individual_element_data(charakter, selected_elements):
    """
    Wendet individuelle Charakterdaten auf die vom Setting geladenen Elemente an
    """
    # Völker-Auswahlen anwenden
    voelker_data = selected_elements.get('voelker', {})
    for name, data in voelker_data.items():
        if name in charakter.voelker:
            charakter.voelker[name].ausgewaehlt = data.get('ausgewaehlt', False)

    # Handicap-Daten anwenden
    handicaps_data = selected_elements.get('handicaps', {})
    for name, data in handicaps_data.items():
        if name in charakter.handicaps:
            charakter.handicaps[name].ausgewaehlt = data.get('ausgewaehlt', False)
            if 'stufe' in data:
                charakter.handicaps[name].stufe = data['stufe']
            if 'punkte' in data:
                charakter.handicaps[name].punkte = data['punkte']
            if 'beschreibung' in data:
                charakter.handicaps[name].individuelle_beschreibung = data['beschreibung']
                charakter.handicaps[name].beschreibung = data['beschreibung']

    # Talent-Daten anwenden
    talente_data = selected_elements.get('talente', {})
    for name, data in talente_data.items():
        if name in charakter.talente:
            charakter.talente[name].ausgewaehlt = data.get('ausgewaehlt', False)
            if 'rang' in data:
                charakter.talente[name].rang = data['rang']
            if 'neue_maechte' in data:
                charakter.talente[name].neue_maechte = data['neue_maechte']
            if 'machtpunkte' in data:
                charakter.talente[name].machtpunkte = data['machtpunkte']
            if 'beschreibung' in data:
                charakter.talente[name].individuelle_beschreibung = data['beschreibung']
                charakter.talente[name].beschreibung = data['beschreibung']

    # Macht-Daten anwenden
    maechte_data = selected_elements.get('maechte', {})
    for name, data in maechte_data.items():
        if name in charakter.maechte:
            charakter.maechte[name].ausgewaehlt = data.get('ausgewaehlt', False)
            if 'rang' in data:
                charakter.maechte[name].rang = data['rang']
            if 'machtpunkte' in data:
                charakter.maechte[name].machtpunkte = data['machtpunkte']
            if 'reichweite' in data:
                charakter.maechte[name].reichweite = data['reichweite']
            if 'dauer' in data:
                charakter.maechte[name].dauer = data['dauer']
            if 'beschreibung' in data:
                charakter.maechte[name].individuelle_beschreibung = data['beschreibung']
                charakter.maechte[name].beschreibung = data['beschreibung']

    # Superkraft-Daten anwenden
    superkraefte_data = selected_elements.get('superkraefte', {})
    from models.superkraft import SuperkraftModifikator
    for name, data in superkraefte_data.items():
        if name in getattr(charakter, 'superkraefte', {}):
            kraft = charakter.superkraefte[name]
            kraft.ausgewaehlt = data.get('ausgewaehlt', False)
            kraft.gewaehlte_kosten = data.get('gewaehlte_kosten', 0)
            # Gewählte Modifikatoren wiederherstellen
            kraft.gewaehlte_modifikatoren = []
            for mod_data in data.get('gewaehlte_modifikatoren', []):
                kraft.gewaehlte_modifikatoren.append(
                    SuperkraftModifikator.from_dict(mod_data)
                )

    # Ausrüstungs-Daten anwenden
    ausruestung_data = selected_elements.get('ausruestung', {})
    for name, data in ausruestung_data.items():
        if name in charakter.ausruestung:
            item = charakter.ausruestung[name]
            item.ausgewaehlt = data.get('ausgewaehlt', False)
            if 'anzahl' in data:
                item.menge = data['anzahl']
            if 'zustand' in data:
                item.zustand = data['zustand']


def _load_equipment_selections(charakter, data):
    """
    Lädt die Ausrüstungsauswahllisten
    """
    # Listen zurücksetzen
    charakter.selected_waffen = []
    charakter.selected_schilde = []
    charakter.selected_ruestungen = []
    charakter.selected_allgemeine_ausruestung = []

    # Ausgewählte Waffen
    selected_waffen_names = data.get('selected_waffen', [])
    for name in selected_waffen_names:
        if name in charakter.ausruestung:
            waffe = charakter.ausruestung[name]
            if isinstance(waffe, Waffe):
                waffe.angelegt = True
                charakter.selected_waffen.append(waffe)

    # Ausgewählte Schilde
    selected_schilde_names = data.get('selected_schilde', [])
    for name in selected_schilde_names:
        if name in charakter.ausruestung:
            schild = charakter.ausruestung[name]
            if isinstance(schild, Schild):
                schild.angelegt = True
                charakter.selected_schilde.append(schild)

    # Ausgewählte Rüstungen
    selected_ruestungen_names = data.get('selected_ruestungen', [])
    for name in selected_ruestungen_names:
        if name in charakter.ausruestung:
            ruestung = charakter.ausruestung[name]
            if isinstance(ruestung, Ruestung):
                ruestung.angelegt = True
                charakter.selected_ruestungen.append(ruestung)
                if ruestung not in charakter.selected_allgemeine_ausruestung:
                    charakter.selected_allgemeine_ausruestung.append(ruestung)

    # Ausgewählte allgemeine Ausrüstung
    selected_allgemeine_ausruestung_names = data.get('selected_allgemeine_ausruestung', [])
    for name in selected_allgemeine_ausruestung_names:
        if name in charakter.ausruestung:
            item = charakter.ausruestung[name]
            if not isinstance(item, (Waffe, Ruestung, Schild)):
                charakter.selected_allgemeine_ausruestung.append(item)


def _load_old_format_selections(charakter, data):
    """
    Lädt die Auswahllisten für das alte Format
    """
    # Ausgewählte Talente wiederherstellen
    charakter.selected_talente = data.get('selected_talente', [])
    for name_key in charakter.selected_talente:
        if name_key in charakter.talente:
            charakter.talente[name_key].ausgewaehlt = True

    # Ausgewählte Mächte wiederherstellen
    charakter.selected_maechte = data.get('selected_maechte', [])
    for name_key in charakter.selected_maechte:
        if name_key in charakter.maechte:
            charakter.maechte[name_key].ausgewaehlt = True

    # Ausrüstungsauswahlen laden
    _load_equipment_selections(charakter, data)


def _finalize_character_loading(charakter, data):
    """
    Gemeinsame Nachbearbeitung für beide Lade-Formate
    """
    # Charakter-Status-Werte setzen
    charakter.verbleibende_attributsteigerungen = data.get('verbleibende_attributsteigerungen', charakter.verbleibende_attributsteigerungen)
    charakter.verbleibende_fertigkeitssteigerungen = data.get('verbleibende_fertigkeitssteigerungen', charakter.verbleibende_fertigkeitssteigerungen)
    charakter.maximale_attributsteigerungen = data.get('maximale_attributsteigerungen', charakter.maximale_attributsteigerungen)
    charakter.maximale_fertigkeitssteigerungen = data.get('maximale_fertigkeitssteigerungen', charakter.maximale_fertigkeitssteigerungen)
    charakter.verbleibende_aufstiege = data.get('verbleibende_aufstiege', charakter.verbleibende_aufstiege)
    charakter.aufstiege_gesamt = data.get('aufstiege_gesamt', charakter.aufstiege_gesamt)
    charakter.verfuegbare_maechte = data.get('verfuegbare_maechte', charakter.verfuegbare_maechte)
    charakter.anzahl_maechte = data.get('anzahl_maechte', charakter.anzahl_maechte)
    charakter.machtpunkte = data.get('machtpunkte', charakter.machtpunkte)
    charakter.vermoegen = data.get('vermoegen', charakter.vermoegen)
    charakter.erschoepfung = data.get('erschoepfung', charakter.erschoepfung)
    charakter.machtstufe = data.get('machtstufe', getattr(charakter, 'machtstufe', 'III'))
    charakter.superkraft_punkte_gesamt = data.get('superkraft_punkte_gesamt', getattr(charakter, 'superkraft_punkte_gesamt', 0))
    charakter.superkraft_punkte_verbraucht = data.get('superkraft_punkte_verbraucht', getattr(charakter, 'superkraft_punkte_verbraucht', 0))
    charakter.kraftobergrenze = data.get('kraftobergrenze', getattr(charakter, 'kraftobergrenze', 15))
    charakter.zusaetzliche_talente = data.get('zusaetzliche_talente', charakter.zusaetzliche_talente)
    charakter.gesamt_handicap_punkte = data.get('gesamt_handicap_punkte', charakter.gesamt_handicap_punkte)
    charakter.char_gen_completed = data.get('char_gen_completed', charakter.char_gen_completed)

    # Savage Pathfinder Support
    charakter.pathfinder_kostenlose_talente_gewaehlt = data.get('pathfinder_kostenlose_talente_gewaehlt', 0)

    # Steigerungs-Journal laden (falls vorhanden)
    charakter.steigerungs_journal = data.get('steigerungs_journal', None)

    # Setting-Einstellungen
    if 'settingregeln' in data:
        try:
            settingregeln_data = data.get('settingregeln', {})
            if charakter.settingregeln:
                charakter.settingregeln.from_dict(settingregeln_data)
        except Exception as e:
            Logger.warning(f"Fehler beim Laden der Settingregeln: {e}")

    # UI aktualisieren
    charakter.dispatch('on_charakter_change')