#charakter.py

from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.event import EventDispatcher
from pathlib import Path
import json, os, sys, copy
from kivy.clock import Clock
from manager.volk_manager import VolkManager
import functions.ausruestung_funktionen as ausruestung_funktionen
import functions.charakter_speicher as charakter_speicher
import functions.abgeleitete_werte as abgeleitete_werte
import functions.character_advancement as character_advancement
import functions.talent_funktionen as talent_funktionen
import functions.macht_funktionen as macht_funktionen
import functions.handicap_funktionen as handicap_funktionen
import functions.eigenschaften_funktionen as eigenschaften_funktionen
import functions.setting_funktionen as setting_funktionen
from functions.setting_funktionen import CustomElementManager, SetEncoder
from models.wuerfel import Wuerfel
from models.attribut import Attribut
from models.fertigkeit import Fertigkeit
from models.handicap import Handicap
from models.talent import Talent
from models.volk import Volk
from models.macht import Macht
from models.ausruestung import Ausruestung
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild
from models.settingregeln import SettingRegeln
from kivy.logger import Logger, LOG_LEVELS
from kivy.config import Config

app = App.get_running_app()

# Bereinigte Grundfertigkeiten-Liste
grundfertigkeiten = [
    "Allgemeinwissen",
    "Athletik",
    "Heimlichkeit",
    "Überreden",
    "Wahrnehmung",
]

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


class Charakter(EventDispatcher):
    """
    Klasse zur Darstellung eines Charakters.
    """
    __events__ = ('on_charakter_change',)

    # Definierte Properties auf Klassenebene
    profil_daten = DictProperty({})
    verbleibende_attributsteigerungen = NumericProperty(5)
    verbleibende_fertigkeitssteigerungen = NumericProperty(12)
    maximale_attributsteigerungen = NumericProperty(5)
    maximale_fertigkeitssteigerungen = NumericProperty(12)
    verbleibende_aufstiege = NumericProperty(0)
    aufstiege_gesamt = NumericProperty(0)
    rang = StringProperty("Anfänger")
    char_gen_completed = BooleanProperty(False)
    verfuegbare_maechte = NumericProperty(0)
    machtpunkte = NumericProperty(0)
    vermoegen = NumericProperty(500)
    waehrungseinheit = StringProperty("Gold")
    vermoegen_text = StringProperty("Vermögen: 500 Gold")
    erschoepfung = NumericProperty(0)
    talente = DictProperty({})
    handicaps = DictProperty({})
    fertigkeiten_daten = DictProperty({})
    verbleibende_handicap_punkte = NumericProperty(0)
    gesamt_handicap_punkte = NumericProperty(0)
    maechte = DictProperty({})
    ausruestung = DictProperty({})
    konzept = DictProperty({})
    details = DictProperty({})
    settingregeln = ObjectProperty(None)
    voelker = DictProperty({})
    voelker_selected = DictProperty({})
    maximale_traglast = NumericProperty(40)
    gesamtgewicht = NumericProperty(0)
    selected_handicaps = ListProperty([])
    selected_talente = ListProperty([])
    selected_maechte = ListProperty([])
    selected_allgemeine_ausruestung = ListProperty([])
    selected_waffen = ListProperty([])
    selected_ruestungen = ListProperty([])
    selected_schilde = ListProperty([])
    char_name = StringProperty("")
    active_setting_name = StringProperty("")   

    # Abgeleitete Werte als Properties
    bewegungsweite = NumericProperty(6)
    parade = NumericProperty(3)
    robustheit = NumericProperty(3)
    robustheit_basis = NumericProperty(3)
    robustheit_mit_ruestung = StringProperty("")
    wunden = NumericProperty(0)
    bennys = NumericProperty(3)
    entschlossenheit = NumericProperty(0)

    # Attribute und Fertigkeiten
    attribute = DictProperty({})
    fertigkeiten = DictProperty({})

    def __init__(
        self,
        active_setting_name=None,
        char_name="",
        alter="",
        geschlecht="",
        konzept="",
        sprachen="",
        bennys="3",
        entschlossenheit="0",
        beschreibung="",
        hintergrund="",
        **kwargs,
    ):
        # Superklasse initialisieren
        super().__init__(**kwargs)

        # Initialisierungen
        self.handicaps = {}
        self.gesamt_handicap_punkte = 0
        self.zusaetzliche_talente = 0
        self.talente = {}
        self.maechte = {}
        self.ausruestung = {}
        self.ruestungen = {}
        self.waffen = {}
        self.schilde = {}
        self.voelker = {}
        self.verfuegbare_maechte = 0
        self.machtpunkte = 0
        self.selected_allgemeine_ausruestung = []
        self.selected_waffen = []
        self.selected_ruestungen = []
        self.selected_schilde = []
        self.profil_daten = {}
        self.startkapital = 500
        self.settingregeln = SettingRegeln()

        self.volk_manager = VolkManager(self)
        self.volk_manager.bind(on_volk_change=self.on_charakter_change)

        # Profil-Daten setzen
        self.profil_daten = {
            "Name": char_name,
            "Alter": alter,
            "Geschlecht": geschlecht,
            "Konzept": konzept,
            "Sprachen": sprachen,
        }

        self.char_name = char_name

        # Setting setzen
        if active_setting_name:
            self.active_setting_name = active_setting_name
        else:
            self.active_setting_name = "SWAE"  # Standard-Setting

        self.custom_element_manager = CustomElementManager(self, setting_name=self.active_setting_name)

        # Versuche, das aktive Setting zu laden oder neu anzulegen
        if self.custom_element_manager.set_active_setting(self.active_setting_name):
            Logger.info(f"Setting '{self.active_setting_name}' erfolgreich geladen.")
        else:
            default_setting = self.create_default_setting()
            self.custom_element_manager.add_setting(self.active_setting_name, default_setting, overwrite=True)
            self.custom_element_manager.set_active_setting(self.active_setting_name)
            Logger.info(f"Setting '{self.active_setting_name}' erstellt und geladen.")

        # Attribute initialisieren
        self.initialisiere_attribute()

        # Fertigkeiten initialisieren (Daten wurden aus dem Setting geladen)
        self.initialisiere_fertigkeiten()
        self.bind(fertigkeiten=self.on_fertigkeiten_changed)

        # Lade nun alle Elemente aus dem aktiven Setting
        self.load_elements_from_active_setting()

        # Beispiel: Standardvolk auswählen, wenn vorhanden
        if "Mensch" in self.voelker:
            # Alle auf False setzen
            self.voelker_selected = {name: False for name in self.voelker.keys()}
            # Mensch auswählen
            self.voelker_selected["Mensch"] = True

        self.bind(voelker_selected=self.on_charakter_change)

        # Überwachung bestimmter Eigenschaften
        self.bind(
            verbleibende_attributsteigerungen=self.update_char_gen_status,
            verbleibende_fertigkeitssteigerungen=self.update_char_gen_status,
            verbleibende_handicap_punkte=self.update_char_gen_status,
            char_gen_completed=self.on_char_gen_completed,
        )

        # Überwachung von Vermögen
        self.bind(vermoegen=self.update_vermoegen_text)
        self.bind(waehrungseinheit=self.update_vermoegen_text)

        # Rang-Mapping für Aufstiege
        self.rang_mapping = [
            (0, 4, "Anfänger", 1),
            (4, 8, "Fortgeschritten", 2),
            (8, 12, "Veteran", 3),
            (12, 16, "Heroisch", 4),
            (16, 100, "Legendär", 5),
        ]
        self.update_rang()
        self.bind(aufstiege_gesamt=lambda instance, value: self.update_rang())

        # Berechnung der abgeleiteten Werte
        self.berechne_abgeleitete_werte()

        # UI-Event auslösen
        self.dispatch('on_charakter_change')

    def create_default_setting(self):
        return setting_funktionen.create_default_setting(self)

    def load_elements_from_active_setting(self):
        return setting_funktionen.load_elements_from_active_setting(self)

    def speichern_als_json(self, dateipfad):
        try:
            charakter_daten = self.to_dict()
            with open(dateipfad, 'w', encoding='utf-8') as f:
                json.dump(charakter_daten, f, ensure_ascii=False, indent=4)
            Logger.info(f"Charakter erfolgreich in {dateipfad} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Charakters: {e}")

    def laden_von_json(self, dateipfad):
        try:
            with open(dateipfad, 'r', encoding='utf-8') as f:
                daten = json.load(f)

            self.from_dict(daten)
            Logger.info(f"Charakter erfolgreich von {dateipfad} geladen.")

            self.voelker_selected = daten.get('voelker_selected', self.voelker_selected)
            self.active_setting_name = daten.get('active_setting_name', self.active_setting_name)

            # Setting aktivieren
            if self.custom_element_manager:
                success = self.custom_element_manager.set_active_setting(self.active_setting_name)
                if not success:
                    Logger.warning(f"Das Setting '{self.active_setting_name}' konnte nicht aktiviert werden. Verwende Standard-Setting.")
                    self.active_setting_name = "SWAE"
                    self.custom_element_manager.set_active_setting(self.active_setting_name)

        except Exception as e:
            Logger.error(f"Fehler beim Laden des Charakters: {e}")


    def reload_character_data(self):
        """Aktualisiert den Charakter, um nach dem Laden eines neuen Settings alle Elemente korrekt zu laden."""
        data = self.to_dict()
        self.from_dict(data)


    def to_dict(self):
        # Sicherstellen, dass selected_handicaps aktualisiert sind
        # alle Handicaps, die ausgewaehlt sind, in selected_handicaps aufnehmen
        self.selected_handicaps = [name for name, handicap in self.handicaps.items() if handicap.ausgewaehlt]

        return {
            'profil_daten': self.profil_daten,
            "voelker": {name: volk.to_setting_dict() for name, volk in self.voelker.items()},
            'attribute': {name: attribut.to_dict() for name, attribut in self.attribute.items()},
            'fertigkeiten': {name: fertigkeit.to_dict() for name, fertigkeit in self.fertigkeiten.items()},
            'handicaps': {name: handicap.to_dict() for name, handicap in self.handicaps.items()},
            'talente': {name: talent.to_dict() for name, talent in self.talente.items()},
            'maechte': {name: macht.to_dict() for name, macht in self.maechte.items()},
            "ausruestung": {name: ausruestung.to_dict() for name, ausruestung in self.ausruestung.items()},
            'selected_handicaps': self.selected_handicaps,
            'selected_talente': self.selected_talente,
            'selected_maechte': self.selected_maechte,
            'selected_allgemeine_ausruestung': [item.name for item in self.selected_allgemeine_ausruestung],
            'selected_waffen': [item.name for item in self.selected_waffen],
            'selected_ruestungen': [item.name for item in self.selected_ruestungen],
            'selected_schilde': [item.name for item in self.selected_schilde],
            'voelker_selected': self.voelker_selected,
            'verbleibende_attributsteigerungen': self.verbleibende_attributsteigerungen,
            'verbleibende_fertigkeitssteigerungen': self.verbleibende_fertigkeitssteigerungen,
            'maximale_attributsteigerungen': self.maximale_attributsteigerungen,
            'maximale_fertigkeitssteigerungen': self.maximale_fertigkeitssteigerungen,
            'verbleibende_aufstiege': self.verbleibende_aufstiege,
            'aufstiege_gesamt': self.aufstiege_gesamt,
            'verfuegbare_maechte': self.verfuegbare_maechte,
            'machtpunkte': self.machtpunkte,
            'vermoegen': self.vermoegen,
            'erschoepfung': self.erschoepfung,
            'zusaetzliche_talente': self.zusaetzliche_talente,
            'gesamt_handicap_punkte': self.gesamt_handicap_punkte,
            'settingregeln': self.settingregeln.to_dict(),
            'active_setting_name': self.custom_element_manager.active_setting_name
        }


    def from_dict(self, data):
        # Profildaten setzen
        for key, value in data.get('profil_daten', {}).items():
            self.set_profil_daten(key, value)

        # Völker laden
        voelker_data = data.get('voelker', {})
        self.voelker = {}
        for name, volk_dict in voelker_data.items():
            self.voelker[name] = Volk.from_dict(volk_dict)
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
        for name, attr_data in attribute_data.items():
            self.attribute[name] = Attribut.from_dict_static(attr_data)

        # Fertigkeiten laden
        fertigkeiten_data = data.get('fertigkeiten', {})
        for name, fert_data in fertigkeiten_data.items():
            self.fertigkeiten[name] = Fertigkeit.from_dict_static(fert_data, self.attribute)

        # Handicaps laden
        handicaps_data = data.get('handicaps', {})
        for name_key, handicap_data in handicaps_data.items():
            # Prüfen ob es schon ein Handicap mit diesem Namen gibt
            if name_key in self.handicaps:
                # Existierendes Handicap aktualisieren
                self.handicaps[name_key].update_from_dict(handicap_data)
            else:
                # Handicap neu erzeugen, falls es noch nicht existiert
                self.handicaps[name_key] = Handicap.from_dict_static(handicap_data)

        self.selected_handicaps = [name for name, handicap in self.handicaps.items() if handicap.ausgewaehlt]

        # Talente laden
        talente_data = data.get('talente', {})
        for name_key, talent_data in talente_data.items():
            self.talente[name_key] = Talent.from_dict_static(talent_data)
            if name_key not in self.custom_element_manager.active_setting['talente']:
                self.custom_element_manager.active_setting['talente'][name_key] = talent_data

        # Mächte laden
        maechte_data = data.get('maechte', {})
        for name_key, macht_data in maechte_data.items():
            self.maechte[name_key] = Macht.from_dict_static(macht_data)
            if name_key not in self.custom_element_manager.active_setting['maechte']:
                self.custom_element_manager.active_setting['maechte'][name_key] = macht_data

        # Ausrüstung laden
        ausruestung_data = data.get('ausruestung', {})
        self.ausruestung = {}
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

            self.ausruestung[name] = item

            if name not in self.custom_element_manager.active_setting['ausruestung']:
                self.custom_element_manager.active_setting['ausruestung'][name] = item_data
                #Logger.info(f"Ausrüstungsgegenstand '{name}' wurde dem Setting hinzugefügt.")

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

        # Ausgewählte Waffen wiederherstellen
        selected_waffen_names = data.get('selected_waffen', [])
        self.selected_waffen = []
        for name in selected_waffen_names:
            if name in self.ausruestung:
                waffe = self.ausruestung[name]
                waffe.angelegt = True
                self.selected_waffen.append(waffe)
                Logger.debug(f"Waffe '{waffe.name}' als angelegt markiert.")
            else:
                Logger.warning(f"Waffe '{name}' nicht in self.ausruestung gefunden.")

        # Setze angelegt=False für andere Waffen
        for waffe in self.ausruestung.values():
            if isinstance(waffe, Waffe) and waffe.name not in selected_waffen_names:
                if waffe.angelegt:
                    waffe.angelegt = False
                    Logger.debug(f"Waffe '{waffe.name}' als nicht angelegt markiert.")

        # Ausgewählte Schilde wiederherstellen
        selected_schilde_names = data.get('selected_schilde', [])
        self.selected_schilde = []
        for name in selected_schilde_names:
            if name in self.ausruestung:
                schild = self.ausruestung[name]
                schild.angelegt = True
                self.selected_schilde.append(schild)
                Logger.debug(f"Schild '{schild.name}' als angelegt markiert.")
            else:
                Logger.warning(f"Schild '{name}' nicht in self.ausruestung gefunden.")

        # Setze angelegt=False für andere Schilde
        for schild in self.ausruestung.values():
            if isinstance(schild, Schild) and schild.name not in selected_schilde_names:
                if schild.angelegt:
                    schild.angelegt = False
                    Logger.debug(f"Schild '{schild.name}' als nicht angelegt markiert.")

        # Ausgewählte Rüstungen wiederherstellen
        selected_ruestungen_names = data.get('selected_ruestungen', [])
        self.selected_ruestungen = []
        for name in selected_ruestungen_names:
            if name in self.ausruestung:
                ruestung = self.ausruestung[name]
                ruestung.angelegt = True
                self.selected_ruestungen.append(ruestung)
                Logger.debug(f"Rüstung '{ruestung.name}' als angelegt markiert.")
            else:
                Logger.warning(f"Rüstung '{name}' nicht in self.ausruestung gefunden.")

        # Setze angelegt=False für andere Rüstungen
        for ruestung in self.ausruestung.values():
            if isinstance(ruestung, Ruestung) and ruestung.name not in selected_ruestungen_names:
                if ruestung.angelegt:
                    ruestung.angelegt = False
                    Logger.debug(f"Rüstung '{ruestung.name}' als nicht angelegt markiert.")

        # Ausgewählte allgemeine Ausrüstung wiederherstellen
        selected_allgemeine_ausruestung_names = data.get('selected_allgemeine_ausruestung', [])
        self.selected_allgemeine_ausruestung = [self.ausruestung[name] for name in selected_allgemeine_ausruestung_names if name in self.ausruestung]

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

        # Aktiven Setting-Namen setzen und Setting aktivieren
        self.active_setting_name = data.get('active_setting_name', self.active_setting_name)
        Logger.debug(f"Active Setting Name gesetzt auf: {self.active_setting_name}")

        success = self.custom_element_manager.set_active_setting(self.active_setting_name)
        if success:
            Logger.debug(f"Setting '{self.active_setting_name}' erfolgreich aktiviert.")
        else:
            Logger.error(f"Setting '{self.active_setting_name}' konnte nicht aktiviert werden.")

        # UI aktualisieren
        self.dispatch('on_charakter_change')

    def initialisiere_attribute(self):
        eigenschaften_funktionen.initialisiere_attribute(self)

    def get_attribute_dict(self):
        return eigenschaften_funktionen.get_attribute_dict(self)

    def steigere_attribut(self, attribut_name):
        return eigenschaften_funktionen.steigere_attribut(self, attribut_name)

    def senke_attribut(self, attribut_name):
        return eigenschaften_funktionen.senke_attribut(self, attribut_name)

    def initialisiere_fertigkeiten(self):
        eigenschaften_funktionen.initialisiere_fertigkeiten(self)

    def steigere_fertigkeit(self, fertigkeit_name):
        return eigenschaften_funktionen.steigere_fertigkeit(self, fertigkeit_name)

    def senke_fertigkeit(self, fertigkeit_name):
        return eigenschaften_funktionen.senke_fertigkeit(self, fertigkeit_name)

    def add_fertigkeit(self, fertigkeit):
        return eigenschaften_funktionen.add_fertigkeit(self, fertigkeit)

    def remove_fertigkeit(self, fertigkeit_name):
        return eigenschaften_funktionen.remove_fertigkeit(self, fertigkeit_name)

    def save_custom_fertigkeiten(self):
        eigenschaften_funktionen.save_custom_fertigkeiten(self)

    def load_custom_fertigkeiten(self):
        eigenschaften_funktionen.load_custom_fertigkeiten(self)

    def on_attribut_wert_change(self, instance, value):
        Logger.debug(f"Attribut '{instance.attribut_name}' Wert geändert zu {value}.")

    def on_attribut_modifier_change(self, instance, value):
        Logger.debug(f"Attribut '{instance.attribut_name}' Modifier geändert zu {value}.")

    def on_fertigkeiten_changed(self, instance, value):
        pass
        # Logger.info("Fertigkeiten haben sich geändert, UI wird aktualisiert.")
        # # Hier lösen wir ein Ereignis aus oder informieren den Controller
        # self.dispatch('on_charakter_change')

    def initialisiere_ausruestung(self, ausruestung):
        self.ausruestung = {}
        try:
            for name, item in ausruestung.items():
                self.ausruestung[name] = item
            Logger.debug("Ausrüstung erfolgreich initialisiert.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Ausrüstung: {e}")

    def on_charakter_change(self, *args):
        self.berechne_abgeleitete_werte()

    def on_attribut_wert_change(self, instance, value):
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_attribut_modifier_change(self, instance, value):
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_fertigkeit_wert_change(self, instance, value):
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_fertigkeit_modifier_change(self, instance, value):
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def set_selected_volk(self, volk_name):
        self.volk_manager.set_selected_volk(volk_name)
    
    def toggle_selected_volk(self, volk_name, value):
        self.volk_manager.toggle_selected_volk(volk_name, value)

    # Methode zum Auswählen eines Volkes
    def waehle_volk(self, volk_name):
        self.volk_manager.waehle_volk(volk_name)

    # Methode zum Abwählen des aktuellen Volkes
    def entferne_volk(self):
        self.volk_manager.entferne_volk()

    def add_ausruestung(self, ausruestung_obj):
        if ausruestung_obj.name in self.ausruestung:
            self.ausruestung[ausruestung_obj.name].erhoehe_menge(ausruestung_obj.menge)
            return True
        else:
            self.ausruestung[ausruestung_obj.name] = ausruestung_obj
            return True
        return False

    def remove_ausruestung(self, ausruestung_name):
        if ausruestung_name in self.ausruestung:
            del self.ausruestung[ausruestung_name]
            return True
        return False

    def add_ausruestung(self, item):
        if item.name in self.ausruestung:
            self.ausruestung[item.name].menge += item.menge
        else:
            self.ausruestung[item.name] = item
        return True

    def remove_ausruestung(self, item_name):
        if item_name in self.ausruestung:
            del self.ausruestung[item_name]
            return True
        else:
            return False

    def update_vermoegen_text(self, *args):
        self.vermoegen_text = f"Vermögen: {self.vermoegen} {self.waehrungseinheit}"
        Logger.info(f"Vermögen: {self.vermoegen} {self.waehrungseinheit} aktualisiert")

    def update_char_gen_status(self, *args):
        if (self.verbleibende_attributsteigerungen == 0 and 
            self.verbleibende_fertigkeitssteigerungen == 0 and
            self.verbleibende_handicap_punkte == 0):
            if not self.char_gen_completed:
                self.char_gen_completed = True
                Logger.debug("Charaktergenerierung abgeschlossen.")
        else:
            if self.char_gen_completed:
                self.char_gen_completed = False
                Logger.debug("Charaktergenerierung noch nicht abgeschlossen.")

    def on_char_gen_completed(self, instance, value):
        if value:
            Logger.debug("Charaktergenerierung abgeschlossen. `verbleibende_aufstiege` ist bereit zur Nutzung.")
            # Beispiel: Deaktiviere alle Talent-Auswahl-Buttons
            # for button in getattr(self, 'talent_buttons', []):
            #     button.disabled = True
        else:
            Logger.debug("Charaktergenerierung noch nicht abgeschlossen.")
            # Beispiel: Aktiviere alle Talent-Auswahl-Buttons
            # for button in getattr(self, 'talent_buttons', []):
            #     button.disabled = False

    def __str__(self):
        output = f"Attribute:\n"
        for attribut in self.attribute.values():
            output += f"{attribut}\n"
        output += "\nFertigkeiten:\n"
        for fertigkeit in self.fertigkeiten.values():
            output += f"{fertigkeit}\n"
        output += f"\nVerbleibende Attributsteigerungen: {self.verbleibende_attributsteigerungen}"
        output += f"\nVerbleibende Fertigkeitssteigerungen: {self.verbleibende_fertigkeitssteigerungen}"
        return output

    def steigere_attribut(self, attribut_name):
        return character_advancement.steigere_attribut(self, attribut_name)

    def senke_attribut(self, attribut_name):
        return character_advancement.senke_attribut(self, attribut_name)

    def update_rang(self):
        character_advancement.update_rang(self)

    def get_rang(self, aufstiege_gesamt):
        return character_advancement.get_rang(self, aufstiege_gesamt)

    def increase_aufstiege(self):
        character_advancement.increase_aufstiege(self)

    def erhoehe_startkapital(self):
        character_advancement.erhoehe_startkapital(self)

    def decrease_aufstiege(self):
        character_advancement.decrease_aufstiege(self)  

    def initialisiere_handicaps(self, handicap_daten):
        handicap_funktionen.initialisiere_handicaps(self, handicap_daten)

    def waehle_handicap(self, handicap_name_key):
        return handicap_funktionen.waehle_handicap(self, handicap_name_key)

    def entferne_handicap(self, handicap_name_key):
        return handicap_funktionen.entferne_handicap(self, handicap_name_key)

    def aktive_handicaps(self):
        return handicap_funktionen.aktive_handicaps(self)

    def ausgewaehlte_handicaps(self):
        return handicap_funktionen.ausgewaehlte_handicaps(self)

    def add_handicap(self, handicap):
        return handicap_funktionen.add_handicap(self, handicap)

    def remove_handicap(self, handicap_name):
        return handicap_funktionen.remove_handicap(self, handicap_name)

    def save_custom_handicaps(self):
        handicap_funktionen.save_custom_handicaps(self)

    def load_custom_handicaps(self):
        handicap_funktionen.load_custom_handicaps(self)

    def initialisiere_talente(self, talent_daten):
        talent_funktionen.initialisiere_talente(self, talent_daten)

    def ausgewaehlte_talente(self):
        return talent_funktionen.ausgewaehlte_talente(self)

    def aktive_talente(self):
        return talent_funktionen.aktive_talente(self)

    def get_freie_talente(self):
        return talent_funktionen.get_freie_talente(self)

    def talent_auswaehlen(self, talent_name_key):
        return talent_funktionen.talent_auswaehlen(self, talent_name_key)

    def waehle_talent(self, talent_name_key):
        return talent_funktionen.waehle_talent(self, talent_name_key)

    def entferne_talent(self, talent_name_key):
        return talent_funktionen.entferne_talent(self, talent_name_key)

    def add_talent(self, talent):
        return talent_funktionen.add_talent(self, talent)

    def remove_talent(self, talent_name):
        return talent_funktionen.remove_talent(self, talent_name)

    def save_custom_talents(self):
        talent_funktionen.save_custom_talents(self)

    def load_custom_talents(self):
        talent_funktionen.load_custom_talents(self)

    def erfuellt_voraussetzung(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für das Talent erfüllt.
        Da wir die Voraussetzungen vorerst ignorieren, geben wir immer True zurück.
        """
        return True

    def initialisiere_maechte(self, maechte_daten):
        macht_funktionen.initialisiere_maechte(self, maechte_daten)

    def waehle_macht(self, macht_name_key):
        return macht_funktionen.waehle_macht(self, macht_name_key)

    def entferne_macht(self, macht_name_key):
        return macht_funktionen.entferne_macht(self, macht_name_key)

    def aktive_maechte(self):
        return macht_funktionen.aktive_maechte(self)

    def ausgewaehlte_maechte(self):
        return macht_funktionen.ausgewaehlte_maechte(self)

    def add_macht(self, macht):
        return macht_funktionen.add_macht(self, macht)

    def remove_macht(self, macht_name):
        return macht_funktionen.remove_macht(self, macht_name)

    def erhoehe_machtpunkte(self, punkte):
        macht_funktionen.erhoehe_machtpunkte(self, punkte)

    def senke_machtpunkte(self, punkte):
        macht_funktionen.senke_machtpunkte(self, punkte)

    def save_custom_maechte(self):
        macht_funktionen.save_custom_maechte(self)

    def load_custom_maechte(self):
        macht_funktionen.load_custom_maechte(self)

    def berechne_abgeleitete_werte(self):
        return abgeleitete_werte.berechne_abgeleitete_werte(self)

    def berechne_traglast(self):
        return ausruestung_funktionen.berechne_traglast(self)

    def berechne_gesamtgewicht(self):
        return ausruestung_funktionen.berechne_gesamtgewicht(self)

    def berechne_gesamt_ruestungsschutz(self):
        return ausruestung_funktionen.berechne_gesamt_ruestungsschutz(self)

    def ausruestung_nach_setting(self, setting):
        """
        Gibt eine Liste der Ausrüstung für ein bestimmtes Setting zurück.

        :param setting: Das gewünschte Setting ('modern', 'mittelalter', 'futuristisch').
        """
        return [ausr for ausr in self.ausruestung.values() if ausr.setting == setting.lower()]
    
    def kaufen(self, item, anzahl=1, preis_pro_stueck=None):
        return ausruestung_funktionen.kaufen(self, item, anzahl, preis_pro_stueck)

    def verkaufen(self, item, anzahl=1, preis_pro_stueck=None):
        return ausruestung_funktionen.verkaufen(self, item, anzahl, preis_pro_stueck)

    def get_item_by_name(self, item_name):
        return ausruestung_funktionen.get_item_by_name(self, item_name)

    def berechne_gesamtkosten(self):
        return ausruestung_funktionen.berechne_gesamtkosten(self)

    def update_eigenschaften_tab(self, dt):
        app = App.get_running_app()
        try:
            eigenschaften_widget = app.root.eigenschaften_screen.eigenschaften_widget
            eigenschaften_widget.update_eigenschaften()
        except AttributeError as e:
            Logger.error(f"Charakter: Konnte eigenschaften_widget nicht finden. Fehler: {e}")

    def set_profil_daten(self, key, value):
        old_value = self.profil_daten.get(key, None)
        self.profil_daten[key] = value
        Logger.debug(f"Charakter.profil_daten: Feld '{key}' geändert von '{old_value}' auf '{value}'")

        # Wenn der Name in profil_daten geändert wird, aktualisiere char_name Property.
        if key == "Name":
            self.char_name = value