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
#from utils import get_application_root, SetEncoder

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

        # Lade nun alle Elemente aus dem aktiven Setting
        self.load_elements_from_active_setting()

        # Beispiel: Standardvolk auswählen, wenn vorhanden
        if "Mensch" in self.voelker:
            # Alle auf False setzen
            self.voelker_selected = {name: False for name in self.voelker.keys()}
            # Mensch auswählen
            self.voelker_selected["Mensch"] = True

        self.bind(voelker_selected=self.on_charakter_change)

        # Attribute initialisieren
        self.initialisiere_attribute()

        # Fertigkeiten initialisieren (Daten wurden aus dem Setting geladen)
        self.initialisiere_fertigkeiten()
        self.bind(fertigkeiten=self.on_fertigkeiten_changed)

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


    def load_elements_from_active_setting(self):
        """Lädt alle Elemente aus der aktiven Einstellung."""
        active_setting = self.custom_element_manager.get_active_setting()
        if not active_setting:
            Logger.error("Keine aktive Einstellung zum Laden der Elemente.")
            return

        # Völker laden
        voelker_data = active_setting.get('voelker', {})
        self.voelker = {}
        for name, volk_dict in voelker_data.items():
            self.voelker[name] = Volk.from_dict(volk_dict)
        Logger.info("Völker geladen.")

        # Fertigkeiten-Daten laden
        fertigkeiten_daten_loaded = active_setting.get('fertigkeiten_daten', {})
        self.fertigkeiten_daten = {name: set(attribut_list) for name, attribut_list in fertigkeiten_daten_loaded.items()}
        self.initialisiere_fertigkeiten()
        Logger.info("Fertigkeiten aktualisiert und geladen.")

        # Talente laden
        talente_data = active_setting.get('talente', {})
        self.talente = {}
        if isinstance(talente_data, dict):
            for name, data in talente_data.items():
                talent = Talent.from_dict_static(data)
                if talent:
                    self.talente[name] = talent
        Logger.info("Talente geladen.")

        # Handicaps laden
        self.handicaps = {}
        handicaps_data = active_setting.get('handicaps', {})
        if isinstance(handicaps_data, dict):
            for name, data in handicaps_data.items():
                handicap = Handicap.from_dict_static(data)
                if handicap:
                    self.handicaps[name] = handicap
        Logger.info("Handicaps geladen.")

        # Mächte laden
        self.maechte = {}
        maechte_data = active_setting.get('maechte', {})
        if isinstance(maechte_data, dict):
            for name, data in maechte_data.items():
                macht = Macht.from_dict_static(data)
                if macht:
                    self.maechte[name] = macht
        Logger.info("Mächte geladen.")

        # Ausrüstung laden
        Logger.debug("Beginne mit dem Laden der Ausrüstung.")
        try:
            self.ausruestung = {}
            ausruestung_data = active_setting.get('ausruestung', {})
            if isinstance(ausruestung_data, dict):
                for name, data in ausruestung_data.items():
                    kategorie = data.get('kategorie', 'Allgemein')
                    if kategorie == 'Waffe':
                        obj = Waffe.from_setting_dict(data)
                    elif kategorie == 'Rüstung':
                        obj = Ruestung.from_setting_dict(data)
                    elif kategorie == 'Schild':
                        obj = Schild.from_setting_dict(data)
                    else:
                        obj = Ausruestung.from_setting_dict(data)

                    if obj:
                        self.ausruestung[name] = obj
            Logger.info("Ausrüstung geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Ausrüstung: {e}")

        # Settingregeln laden
        settingregeln_data = active_setting.get('settingregeln', {})
        self.settingregeln.from_dict(settingregeln_data)
        Logger.info("Settingregeln geladen.")

        # Listen für ausgewählte Gegenstände neu erstellen, falls benötigt
        self.selected_allgemeine_ausruestung = [item for item in self.ausruestung.values() if item.ausgewaehlt and not isinstance(item, (Waffe, Ruestung, Schild))]
        self.selected_waffen = [item for item in self.ausruestung.values() if isinstance(item, Waffe) and item.ausgewaehlt]
        self.selected_ruestungen = [item for item in self.ausruestung.values() if isinstance(item, Ruestung) and item.ausgewaehlt]
        self.selected_schilde = [item for item in self.ausruestung.values() if isinstance(item, Schild) and item.ausgewaehlt]

        # UI-Event auslösen
        self.dispatch('on_charakter_change')


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
        """
        Initialisiert die Attribute, die für Fertigkeiten benötigt werden.
        Da die Attribute immer gleich sind, werden sie einmalig beim Start geladen.
        """
        attribut_namen = ["Geschicklichkeit", "Verstand", "Stärke", "Konstitution", "Willenskraft"]
        for attr in attribut_namen:
            attribut = Attribut(attribut_name=attr, wert=4, modifier=0)
            attribut.bind(wert=self.on_attribut_wert_change)
            attribut.bind(modifier=self.on_attribut_modifier_change)
            self.attribute[attr] = attribut

    def on_attribut_wert_change(self, instance, value):
        Logger.debug(f"Attribut '{instance.attribut_name}' Wert geändert zu {value}.")

    def on_attribut_modifier_change(self, instance, value):
        Logger.debug(f"Attribut '{instance.attribut_name}' Modifier geändert zu {value}.")

    def get_attribute_dict(self):
        """
        Gibt ein Wörterbuch aller Attribute zurück.
        """
        return self.attribute

    # Methoden für Handicaps

    def add_handicap(self, handicap):
        if handicap.name in self.handicaps:
            Logger.warning(f"Handicap '{handicap.name}' existiert bereits.")
            return False
        self.handicaps[handicap.name] = handicap
        Logger.info(f"Handicap '{handicap.name}' hinzugefügt.")
        self.save_custom_handicaps()
        return True

    def remove_handicap(self, handicap_name):
        if handicap_name in self.handicaps:
            del self.handicaps[handicap_name]
            Logger.info(f"Handicap '{handicap_name}' entfernt.")
            self.save_custom_handicaps()
            return True
        Logger.warning(f"Handicap '{handicap_name}' existiert nicht.")
        return False

    def save_custom_handicaps(self):
        """
        Speichert die benutzerdefinierten Handicaps in einer JSON-Datei.
        """
        # Finde die benutzerdefinierten Handicaps
        custom_handicaps = {
            name: handicap.to_dict()
            for name, handicap in self.handicaps.items()
            if getattr(handicap, 'custom', False)
        }
        if custom_handicaps:
            custom_handicaps_file = os.path.join(os.path.dirname(__file__), 'custom_handicaps.json')
            try:
                with open(custom_handicaps_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_handicaps, f, ensure_ascii=False, indent=4)
                Logger.info(f"Benutzerdefinierte Handicaps wurden in {custom_handicaps_file} gespeichert.")
            except Exception as e:
                Logger.error(f"Fehler beim Speichern der benutzerdefinierten Handicaps: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Handicaps zum Speichern.")

    def load_custom_handicaps(self):
        """
        Lädt die benutzerdefinierten Handicaps aus einer JSON-Datei und fügt sie der Handicaps-Liste hinzu.
        """
        custom_handicaps_file = os.path.join(os.path.dirname(__file__), 'custom_handicaps.json')
        if os.path.exists(custom_handicaps_file):
            try:
                with open(custom_handicaps_file, 'r', encoding='utf-8') as f:
                    custom_handicaps_data = json.load(f)
                for name, data in custom_handicaps_data.items():
                    handicap = Handicap.from_dict_static(data)
                    if handicap:
                        self.handicaps[name] = handicap
                Logger.info(f"Benutzerdefinierte Handicaps wurden aus {custom_handicaps_file} geladen.")
            except Exception as e:
                Logger.error(f"Fehler beim Laden der benutzerdefinierten Handicaps: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Handicaps zum Laden gefunden.")

    # Methoden für Fertigkeiten

    def add_fertigkeit(self, fertigkeit):
        if fertigkeit.fertigkeit_name in self.fertigkeiten:
            Logger.warning(f"Fertigkeit '{fertigkeit.fertigkeit_name}' existiert bereits.")
            return False
        self.fertigkeiten[fertigkeit.fertigkeit_name] = fertigkeit
        Logger.info(f"Fertigkeit '{fertigkeit.fertigkeit_name}' hinzugefügt.")
        self.save_custom_fertigkeiten()
        return True

    def remove_fertigkeit(self, fertigkeit_name):
        if fertigkeit_name in self.fertigkeiten:
            del self.fertigkeiten[fertigkeit_name]
            Logger.info(f"Fertigkeit '{fertigkeit_name}' entfernt.")
            self.save_custom_fertigkeiten()
            return True
        Logger.warning(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
        return False

    def save_custom_fertigkeiten(self):
        """
        Speichert die benutzerdefinierten Fertigkeiten in einer JSON-Datei.
        """
        # Finde die benutzerdefinierten Fertigkeiten
        custom_fertigkeiten = {
            name: fertigkeit.to_dict()
            for name, fertigkeit in self.fertigkeiten.items()
            if getattr(fertigkeit, 'custom', False)
        }
        if custom_fertigkeiten:
            custom_fertigkeiten_file = os.path.join(os.path.dirname(__file__), 'custom_fertigkeiten.json')
            try:
                with open(custom_fertigkeiten_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_fertigkeiten, f, ensure_ascii=False, indent=4)
                Logger.info(f"Benutzerdefinierte Fertigkeiten wurden in {custom_fertigkeiten_file} gespeichert.")
            except Exception as e:
                Logger.error(f"Fehler beim Speichern der benutzerdefinierten Fertigkeiten: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Fertigkeiten zum Speichern.")

    def load_custom_fertigkeiten(self):
        """
        Lädt die benutzerdefinierten Fertigkeiten aus einer JSON-Datei und fügt sie der Fertigkeiten-Liste hinzu.
        """
        custom_fertigkeiten_file = os.path.join(os.path.dirname(__file__), 'custom_fertigkeiten.json')
        if os.path.exists(custom_fertigkeiten_file):
            try:
                with open(custom_fertigkeiten_file, 'r', encoding='utf-8') as f:
                    custom_fertigkeiten_data = json.load(f)
                attribute_dict = self.get_attribute_dict()  # Methode zur Beschaffung der Attribute
                for name, data in custom_fertigkeiten_data.items():
                    fertigkeit = Fertigkeit.from_dict_static(data, attribute_dict)
                    if fertigkeit:
                        self.fertigkeiten[name] = fertigkeit
                Logger.info(f"Benutzerdefinierte Fertigkeiten wurden aus {custom_fertigkeiten_file} geladen.")
            except Exception as e:
                Logger.error(f"Fehler beim Laden der benutzerdefinierten Fertigkeiten: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Fertigkeiten zum Laden gefunden.")

    def initialisiere_fertigkeiten(self):
        """Initialisiert die Fertigkeiten des Charakters."""

        self.initialisiere_attribute()

        grundfertigkeiten = [
            "Allgemeinwissen",
            "Athletik",
            "Heimlichkeit",
            "Überreden",
            "Wahrnehmung",
        ]
        
        # Erstellen einer Menge der Fertigkeitenamen aus fertigkeiten_daten
        fertigkeiten_namen_in_daten = set(self.fertigkeiten_daten.keys())
        # Erstellen einer Liste der aktuellen Fertigkeitenamen
        fertigkeiten_namen_aktuell = set(self.fertigkeiten.keys())

        # Aktualisieren oder Erstellen von Fertigkeiten
        for fertigkeit_name, attribut_set in self.fertigkeiten_daten.items():
            if isinstance(attribut_set, set) and len(attribut_set) == 1:
                attribut_name = next(iter(attribut_set))
            else:
                Logger.error(f"Fertigkeit '{fertigkeit_name}' hat eine ungültige Attribut-Zuweisung.")
                continue

            attribut_obj = self.attribute.get(attribut_name)
            if attribut_obj is None:
                Logger.error(f"Attribut '{attribut_name}' für Fertigkeit '{fertigkeit_name}' nicht gefunden.")
                continue

            ist_grundfertigkeit = fertigkeit_name in grundfertigkeiten

            if fertigkeit_name in self.fertigkeiten:
                # Bestehende Fertigkeit aktualisieren
                fertigkeit = self.fertigkeiten[fertigkeit_name]
                fertigkeit.attribut = attribut_obj
                fertigkeit.grundfertigkeit = ist_grundfertigkeit
            else:
                # Neue Fertigkeit erstellen
                fertigkeit = Fertigkeit(
                    fertigkeit_name=fertigkeit_name,
                    attribut=attribut_obj,
                    grundfertigkeit=ist_grundfertigkeit,
                )
                fertigkeit.bind(wert=self.on_fertigkeit_wert_change)
                fertigkeit.bind(wert=self.on_fertigkeit_modifier_change)
                self.fertigkeiten[fertigkeit_name] = fertigkeit

        # Entfernen von Fertigkeiten, die nicht mehr in fertigkeiten_daten vorhanden sind
        fertigkeiten_zu_entfernen = fertigkeiten_namen_aktuell - fertigkeiten_namen_in_daten
        for fertigkeit_name in fertigkeiten_zu_entfernen:
            del self.fertigkeiten[fertigkeit_name]
            Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde entfernt, da sie nicht im geladenen Setting vorhanden ist.")

    def on_fertigkeiten_changed(self, instance, value):
        pass
        # Logger.info("Fertigkeiten haben sich geändert, UI wird aktualisiert.")
        # # Hier lösen wir ein Ereignis aus oder informieren den Controller
        # self.dispatch('on_charakter_change')

    def steigere_fertigkeit(self, fertigkeit_name):
        fertigkeit = self.fertigkeiten.get(fertigkeit_name)
        if fertigkeit:
            zugehoeriges_attribut = fertigkeit.attribut
            aktueller_total_value = fertigkeit.wuerfel.value + fertigkeit.wuerfel.modifier
            attribut_total_value = zugehoeriges_attribut.wuerfel.value + zugehoeriges_attribut.wuerfel.modifier

            # Bestimme den neuen Wert und Modifier nach der Steigerung
            if fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == -2:
                neuer_wert = fertigkeit.wuerfel.value
                neuer_modifier = fertigkeit.wuerfel.modifier + 2
            elif fertigkeit.wuerfel.value < 12:
                neuer_wert = fertigkeit.wuerfel.value + 2
                neuer_modifier = fertigkeit.wuerfel.modifier
            elif fertigkeit.wuerfel.value == 12 and fertigkeit.wuerfel.modifier < 2:
                neuer_wert = fertigkeit.wuerfel.value
                neuer_modifier = fertigkeit.wuerfel.modifier + 1
            else:
                Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
                return False

            neuer_total_value = neuer_wert + neuer_modifier

        # Bestimme die Kosten
        if self.char_gen_completed:
            if neuer_total_value > attribut_total_value:
                kosten = 1
            else:
                kosten = 0.5
        else:            
            if neuer_total_value > attribut_total_value:
                kosten = 2
            else:
                kosten = 1

        def steigern():
            erfolg = fertigkeit.wuerfel.increase()
            if erfolg:
                fertigkeit.ausgewaehlt = True
                Logger.debug(f"Fertigkeit '{fertigkeit_name}' gesteigert auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier}")
                self.rang = self.get_rang(self.aufstiege_gesamt)                
                return True                
            else:
                Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
                return False            

        if self.char_gen_completed:
            if self.verbleibende_aufstiege >= kosten:
                self.verbleibende_aufstiege -= kosten
                steigern()
            else:
                Logger.warning("Nicht genügend verbleibende Aufstiege.")
                return False
        else:
            if self.verbleibende_fertigkeitssteigerungen >= kosten:
                self.verbleibende_fertigkeitssteigerungen -= kosten
                steigern()
            else:
                if self.verbleibende_handicap_punkte > 0.5:
                    steigern()
                    self.verbleibende_handicap_punkte -= 1
                    Logger.info("Fertigkeit mit Handicap-Punkten gesteigert.")
                else:
                    Logger.warning("Nicht genügend verbleibende Fertigkeitssteigerungen.")
                    return False

    def senke_fertigkeit(self, fertigkeit_name):
        """
        Senkt eine Fertigkeit um eine Stufe und gibt die entsprechenden Steigerungen zurück.
        Grundfertigkeiten dürfen nicht von W4+0 auf W4-2 gesenkt werden.
        """
        grundfertigkeiten = [
            "Allgemeinwissen",
            "Athletik",
            "Heimlichkeit",
            "Überreden",
            "Wahrnehmung",
        ]

        def senken():
            fertigkeit.wuerfel.decrease()
            Logger.debug(f"Fertigkeit '{fertigkeit_name}' gesenkt auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier}")
            self.update_char_gen_status()  # Aktualisiere den Status
            self.rang = self.get_rang(self.aufstiege_gesamt)

        fertigkeit = self.fertigkeiten.get(fertigkeit_name)
        if fertigkeit:
            # Überprüfung, ob die Fertigkeit eine Grundfertigkeit ist und ob sie bereits den Mindestmodifier hat
            if fertigkeit_name in grundfertigkeiten and fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == 0:
                Logger.warning(f"Grundfertigkeit '{fertigkeit_name}' kann nicht von W4+0 auf W4-2 gesenkt werden.")
                return False

            zugehoeriges_attribut = fertigkeit.attribut

        # Bestimme die Kosten
        if self.char_gen_completed: 
            kosten = 0.5
            if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
                kosten = 1
        else:
            kosten = 1
            if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
                kosten = 2                 

        vorheriger_wert = fertigkeit.wuerfel.value
        vorheriger_modifier = fertigkeit.wuerfel.modifier

        if self.char_gen_completed:
            if self.verbleibende_aufstiege < self.aufstiege_gesamt:
                #Logger.debug(f"Verbleibende Aufstiege vor Gutschrift: {self.verbleibende_aufstiege}")
                self.verbleibende_aufstiege += kosten
                #Logger.debug(f"{kosten} `verbleibende_aufstiege` gutgeschrieben. Neuer Wert: {self.verbleibende_aufstiege}")
                senken()
            else:
                Logger.debug("Maximum Aufstiege erreicht.")
                return False
        else:
            if self.verbleibende_handicap_punkte < self.gesamt_handicap_punkte:
                self.verbleibende_handicap_punkte += kosten
                senken()
            else:
                if self.verbleibende_fertigkeitssteigerungen < self.maximale_fertigkeitssteigerungen:
                    #Logger.debug(f"Verbleibende Fertigkeitssteigerungen vor Gutschrift: {self.verbleibende_fertigkeitssteigerungen}")
                    self.verbleibende_fertigkeitssteigerungen += kosten
                    #Logger.debug(f"{kosten} `Verbleibende Fertigkeitssteigerungen` gutgeschrieben. Neuer Wert: {self.verbleibende_fertigkeitssteigerungen}")
                    senken()
                else:
                    Logger.warning("Maximum Fertigkeitspunkte erreicht.")
                    return False

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

    def create_default_setting(self):
        """Erstellt eine Standard-Einstellung."""
        default_setting = {
            "name": "SWAE",
            "description": "Savage-Worlds Abenteuer Edition.",
            "voelker": {name: volk.to_setting_dict() for name, volk in self.voelker.items()},
            "voelker_selected": self.voelker_selected, 
            'attribute': {name: attribut.to_dict() for name, attribut in self.attribute.items()},
            "fertigkeiten_daten": {name: list(attribut_set) for name, attribut_set in self.fertigkeiten_daten.items()},
            "talente": {name: talent.to_dict() for name, talent in self.talente.items()},
            "handicaps": {f"{item['Name']}_{item['Stufe']}": item for item in handicap_daten},
            "maechte": {name: macht.to_dict() for name, macht in self.maechte.items()},
            "ausruestung": {name: ausruestung.to_setting_dict() for name, ausruestung in self.ausruestung.items()},
            'settingregeln': self.settingregeln.to_dict(),
        }
        return default_setting

    def get_freie_talente(self):
        """
        Gibt eine Liste von Talenten zurück, die als freie Talente ausgewählt werden können.
        Hier können spezifische Kriterien für freie Talente implementiert werden.
        """
        frei_talente = []
        for talent in self.talente.values():
            if not talent.ausgewaehlt and talent.aktiv:
                frei_talente.append(talent.name)
        # Fügen Sie einen Platzhalter hinzu, falls keine freien Talente verfügbar sind
        if not frei_talente:
            frei_talente = ['Keine freien Talente verfügbar']
        return frei_talente

    def add_talent(self, talent):
        """Fügt ein Talent zur aktiven Einstellung hinzu."""
        self.talente[talent.name] = talent
        self.custom_element_manager.update_element('talente', talent.name, talent.to_dict())

    def remove_talent(self, talent_name):
        """Entfernt ein Talent aus der aktiven Einstellung."""
        if talent_name in self.talente:
            del self.talente[talent_name]
            self.custom_element_manager.remove_element('talente', talent_name)

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

    # Methoden für Mächte
    def add_macht(self, macht):
        if macht.name in self.maechte:
            Logger.warning(f"Macht '{macht.name}' existiert bereits.")
            return False
        self.maechte[macht.name] = macht
        Logger.info(f"Macht '{macht.name}' hinzugefügt.")
        self.save_custom_maechte()
        return True

    def remove_macht(self, macht_name):
        if macht_name in self.maechte:
            del self.maechte[macht_name]
            Logger.info(f"Macht '{macht_name}' entfernt.")
            self.save_custom_maechte()
            return True
        Logger.warning(f"Macht '{macht_name}' existiert nicht.")
        return False

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
        """
        Initialisiert die Handicaps des Charakters basierend auf der bereitgestellten Liste.
        """
        self.handicaps = {}
        try:
            for daten in handicap_daten:
                name = daten.get('Name', '')
                stufe = daten.get('Stufe', '').lower()
                beschreibung = daten.get('Beschreibung', 'Keine Beschreibung verfügbar')  # Beschreibung aus den Daten extrahieren

                # Immer ein eindeutiger Schlüssel mit Name und Stufe
                name_key = f"{name} ({stufe})"

                # Initialisiere das Handicap
                handicap = Handicap(
                    name=name,  # Name ohne Stufe
                    stufe=stufe,
                    beschreibung=beschreibung  # Hier die tatsächliche Beschreibung verwenden
                )
                self.handicaps[name_key] = handicap
            Logger.debug("Handicaps erfolgreich initialisiert.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Handicaps: {e}")

    def waehle_handicap(self, handicap_name_key):
        if handicap_name_key in self.handicaps:
            handicap = self.handicaps[handicap_name_key]
            if not handicap.ausgewaehlt:
                neue_gesamtpunkte = self.gesamt_handicap_punkte + handicap.punkte     
                Logger.info(f"neue_gesamtpunkte '{neue_gesamtpunkte} Kosten: {handicap.punkte} Gesamt {self.gesamt_handicap_punkte}")
                if neue_gesamtpunkte <= 4:           
                    handicap.auswaehlen()
                    self.gesamt_handicap_punkte = neue_gesamtpunkte
                    self.verbleibende_handicap_punkte += handicap.punkte  
                    self.verbleibende_handicap_punkte = min(self.verbleibende_handicap_punkte, 4) 
                    self.selected_handicaps.append(handicap_name_key)
                    Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                    Logger.info(f"verbleibend '{self.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {self.gesamt_handicap_punkte}")
                    self.selected_handicaps = self.selected_handicaps  # Neu zuweisen
                else:
                    handicap.auswaehlen()
                    self.selected_handicaps.append(handicap_name_key)
                    if neue_gesamtpunkte == 5:
                        self.gesamt_handicap_punkte = 4
                        self.verbleibende_handicap_punkte += handicap.punkte 
                        self.verbleibende_handicap_punkte = min(self.verbleibende_handicap_punkte, 4)
                        Logger.info(f"verbleibend '{self.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {self.gesamt_handicap_punkte}")
                        self.selected_handicaps = self.selected_handicaps  # Neu zuweisen 
                        Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                        Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                    else:
                        Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                        self.selected_handicaps = self.selected_handicaps  # Neu zuweisen  
                        Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                        self.verbleibende_handicap_punkte = min(self.verbleibende_handicap_punkte, 4)                  
            else:
                Logger.warning(f"Handicap '{handicap_name_key}' ist bereits ausgewählt.")
        else:
            Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")

    def entferne_handicap(self, handicap_name_key):
        if handicap_name_key in self.handicaps:
            handicap = self.handicaps[handicap_name_key]
            if handicap.ausgewaehlt:
                handicap.abwaehlen()
                self.gesamt_handicap_punkte -= handicap.punkte
                self.gesamt_handicap_punkte = max(self.gesamt_handicap_punkte, 0)
                self.verbleibende_handicap_punkte -= handicap.punkte
                self.verbleibende_handicap_punkte = max(self.verbleibende_handicap_punkte, 0)
                Logger.info(f"Handicap '{handicap_name_key}' entfernt.")
                if handicap_name_key in self.selected_handicaps:
                    self.selected_handicaps.remove(handicap_name_key)
                    self.selected_handicaps = self.selected_handicaps  # Neu zuweisen
            else:
                Logger.warning(f"Handicap '{handicap_name_key}' ist nicht ausgewählt.")
        else:
            Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
 
    def aktive_handicaps(self):
        return [handicap for handicap in self.handicaps.values() if handicap.aktiv]

    def ausgewaehlte_handicaps(self):
        return [handicap for handicap in self.handicaps.values() if handicap.ausgewaehlt]

    def initialisiere_talente(self, talent_daten):
        try:
            for kategorie, talente in talent_daten.items():
                for name, daten in talente.items():
                    talent = Talent(
                        name=name,
                        kategorie=kategorie,
                        rang=daten.get('Rang', ''),
                        voraussetzungen=daten.get('Voraussetzungen', []),
                        beschreibung=daten.get('Beschreibung', ''),
                        neue_maechte=daten.get('neue_maechte', 0),
                        machtpunkte=daten.get('machtpunkte', 0)
                    )
                    self.talente[name] = talent
            #Logger.debug(f"Talente erfolgreich initialisiert für Charakter.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Talente: {e}")

    def ausgewaehlte_talente(self):
        return [talent for talent in self.talente.values() if talent.ausgewaehlt]
    
    def talent_auswaehlen(self, talent_name_key):
        talent = self.talente.get(talent_name_key)
        if talent:
            if not talent.ausgewaehlt:
                if talent.voraussetzungen_erfuellt(self):
                    talent.auswaehlen(self)
                    self.verfuegbare_maechte += talent.neue_maechte
                    self.erhoehe_machtpunkte(talent.machtpunkte)
                    self.selected_talente.append(talent_name_key)
                    Logger.info(f"Talent '{talent_name_key}' ausgewählt.")
                else:
                    Logger.warning(f"Voraussetzungen für Talent '{talent_name_key}' nicht erfüllt.")
            else:
                Logger.warning(f"Talent '{talent_name_key}' ist bereits ausgewählt.")
        else:
            Logger.error(f"Talent '{talent_name_key}' existiert nicht.")

    def waehle_talent(self, talent_name_key):

        if self.verbleibende_handicap_punkte > 1.5:
            self.talent_auswaehlen(talent_name_key)
            self.verbleibende_handicap_punkte -= 2
        else:
            if self.verbleibende_aufstiege > 0:
                self.talent_auswaehlen(talent_name_key)
                self.verbleibende_aufstiege -= 1
                self.update_char_gen_status()
            else:    
                Logger.warning(f"Keine verbleibenden Aufstiege übrig.")

    def entferne_talent(self, talent_name_key):
        def talent_abwaehlen():
            talent.abwaehlen(self)
            self.verfuegbare_maechte -= talent.neue_maechte
            self.verfuegbare_maechte = max(self.verfuegbare_maechte, 0)  # Nicht negativ
            self.senke_machtpunkte(talent.machtpunkte)
            if talent_name_key in self.selected_talente:
                self.selected_talente.remove(talent_name_key)
            Logger.debug(f"Talent '{talent_name_key}' entfernt.")

        talent = self.talente.get(talent_name_key)
        if talent_name_key in self.talente:
            talent = self.talente[talent_name_key]
            Logger.info(f"talent ausgewaehlt {talent.ausgewaehlt}")
            if talent.ausgewaehlt:
                if self.char_gen_completed:
                    talent_abwaehlen()
                    self.verbleibende_aufstiege += 1  # Rückerstattung der Aufstiegs-Punkte                    
                    self.update_char_gen_status()  # Aktualisiere den Status
                else:
                    talent_abwaehlen() 
                    self.verbleibende_handicap_punkte += 2
                    #Logger.info(f"verbleibende_handicap_punkte '{self.verbleibende_handicap_punkte}")
                    self.verbleibende_handicap_punkte = min(self.verbleibende_handicap_punkte, 4)  # Nicht mehr als 4                                   
            else:
                Logger.warning(f"Talent '{talent_name_key}' ist nicht ausgewählt.")
        else:
            Logger.error(f"Talent '{talent_name_key}' existiert nicht.")                

    def ausgewaehlte_talente(self):
        """
        Gibt eine Liste aller ausgewählten Talente zurück.
        """
        return [talent for talent in self.talente.values() if talent.ausgewaehlt]

    def aktive_talente(self):
        """
        Gibt eine Liste aller aktiven Talente zurück.
        """
        return [talent for talent in self.talente.values() if talent.aktiv]

    def erfuellt_voraussetzung(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für das Talent erfüllt.
        Da wir die Voraussetzungen vorerst ignorieren, geben wir immer True zurück.
        """
        return True

    def initialisiere_maechte(self, maechte_daten):
        self.maechte = {}
        try:
            for name, daten in maechte_daten.items():
                if not all(key in daten for key in ['Rang', 'Machtpunkte', 'Reichweite', 'Dauer']):
                    Logger.warning(f"Ungültige oder fehlende Daten für Macht '{name}': {daten}")
                    continue
                macht = Macht(
                    name=name,
                    rang=daten.get('Rang', ''),
                    machtpunkte=daten.get('Machtpunkte', 0),
                    reichweite=daten.get('Reichweite', ''),
                    dauer=daten.get('Dauer', ''),
                    effekt=daten.get('Effekt', ''),
                    beschreibung=daten.get('Beschreibung', ''),
                    voraussetzungen=daten.get('Voraussetzungen', [])
                )
                self.maechte[name] = macht
            #Logger.debug(f"Mächte erfolgreich initialisiert für Charakter.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Mächte: {e}")

    def waehle_macht(self, macht_name_key):
        if self.verfuegbare_maechte > 0:
            if macht_name_key in self.maechte:
                macht = self.maechte[macht_name_key]
                if not macht.ausgewaehlt:
                    if macht.voraussetzungen_erfuellt(self):
                        macht.auswaehlen()
                        self.verfuegbare_maechte -= 1
                        self.selected_maechte.append(macht_name_key)
                        self.selected_maechte = self.selected_maechte  # Neu zuweisen, um Kivy zu informieren
                        Logger.debug(f"Macht '{macht_name_key}' wurde ausgewählt.")
                        return True
                    else:
                        Logger.warning(f"Voraussetzungen für Macht '{macht_name_key}' nicht erfüllt.")
                else:
                    Logger.warning(f"Macht '{macht_name_key}' ist bereits ausgewählt.")
            else:
                Logger.error(f"Macht '{macht_name_key}' existiert nicht.")
        else:
            Logger.warning("Keine verfügbaren Mächte mehr zum Auswählen.")
        return False

    def entferne_macht(self, macht_name_key):
        if macht_name_key in self.maechte:
            macht = self.maechte[macht_name_key]
            if macht.ausgewaehlt:
                macht.abwaehlen()
                self.verfuegbare_maechte += 1
                if macht_name_key in self.selected_maechte:
                    self.selected_maechte.remove(macht_name_key)
                    self.selected_maechte = self.selected_maechte  # Neu zuweisen
                Logger.debug(f"Macht '{macht_name_key}' wurde entfernt.")
                return True
            else:
                Logger.warning(f"Macht '{macht_name_key}' ist nicht ausgewählt.")
        else:
            Logger.error(f"Macht '{macht_name_key}' existiert nicht.")
        return False

    def erhoehe_machtpunkte(self, punkte):
        """
        Erhöht die Machtpunkte des Charakters.
        """
        self.machtpunkte += punkte

    def senke_machtpunkte(self, punkte):
        """
        Verringert die Machtpunkte des Charakters.
        """
        self.machtpunkte -= punkte

    def aktive_maechte(self):
        """
        Gibt eine Liste aller aktiven Mächte zurück.
        """
        return [macht for macht in self.maechte.values() if macht.aktiv]

    def ausgewaehlte_maechte(self):
        """
        Gibt eine Liste aller ausgewählten Mächte zurück.
        """
        return [macht for macht in self.maechte.values() if macht.ausgewaehlt]

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



    def save_custom_talents(self):
        """
        Speichert die benutzerdefinierten Talente in einer JSON-Datei.
        """
        # Finde die benutzerdefinierten Talente
        custom_talente = {name: talent.to_dict() for name, talent in self.talente.items() if getattr(talent, 'custom', False)}
        if custom_talente:
            custom_talente_file = os.path.join(os.path.dirname(__file__), 'custom_talente.json')
            try:
                with open(custom_talente_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_talente, f, ensure_ascii=False, indent=4)
                Logger.info(f"Benutzerdefinierte Talente wurden in {custom_talente_file} gespeichert.")
            except Exception as e:
                Logger.error(f"Fehler beim Speichern der benutzerdefinierten Talente: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Talente zum Speichern.")

    def load_custom_talents(self):
        """
        Lädt die benutzerdefinierten Talente aus einer JSON-Datei und fügt sie der Talentliste hinzu.
        """
        custom_talente_file = os.path.join(os.path.dirname(__file__), 'custom_talente.json')
        if os.path.exists(custom_talente_file):
            try:
                with open(custom_talente_file, 'r', encoding='utf-8') as f:
                    custom_talents_data = json.load(f)
                for name, data in custom_talents_data.items():
                    talent = Talent.from_dict_static(data)
                    self.talente[name] = talent
                Logger.info(f"Benutzerdefinierte Talente wurden aus {custom_talente_file} geladen.")
            except Exception as e:
                Logger.error(f"Fehler beim Laden der benutzerdefinierten Talente: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Talente zum Laden gefunden.")

    def save_custom_maechte(self):
        """
        Speichert die benutzerdefinierten Mächte in einer JSON-Datei.
        """
        # Finde die benutzerdefinierten Mächte
        custom_maechte = {name: macht.to_dict() for name, macht in self.maechte.items() if getattr(macht, 'custom', False)}
        if custom_maechte:
            custom_maechte_file = os.path.join(os.path.dirname(__file__), 'custom_maechte.json')
            try:
                with open(custom_maechte_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_maechte, f, ensure_ascii=False, indent=4)
                Logger.info(f"Benutzerdefinierte Mächte wurden in {custom_maechte_file} gespeichert.")
            except Exception as e:
                Logger.error(f"Fehler beim Speichern der benutzerdefinierten Mächte: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Mächte zum Speichern.")

    def load_custom_maechte(self):
        """
        Lädt die benutzerdefinierten Mächte aus einer JSON-Datei und fügt sie der Mächte-Liste hinzu.
        """
        custom_maechte_file = os.path.join(os.path.dirname(__file__), 'custom_maechte.json')
        if os.path.exists(custom_maechte_file):
            try:
                with open(custom_maechte_file, 'r', encoding='utf-8') as f:
                    custom_maechte_data = json.load(f)
                for name, data in custom_maechte_data.items():
                    macht = Macht.from_dict_static(data)
                    self.maechte[name] = macht
                Logger.info(f"Benutzerdefinierte Mächte wurden aus {custom_maechte_file} geladen.")
            except Exception as e:
                Logger.error(f"Fehler beim Laden der benutzerdefinierten Mächte: {e}")
        else:
            Logger.info("Keine benutzerdefinierten Mächte zum Laden gefunden.")


def get_application_root():
    """Ermittelt das Hauptverzeichnis der Anwendung."""
    if getattr(sys, 'frozen', False):
        # Wenn die Anwendung gepackt ist (z.B. mit cx_Freeze), verwende das Verzeichnis der ausführbaren Datei
        app_root = Path(sys.executable).parent
    else:
        # Bei normalem Python-Skript verwende das Verzeichnis der Skriptdatei
        app_root = Path(__file__).parent.resolve()
    
    #Logger.debug(f"Anwendungs-Hauptverzeichnis erkannt: {app_root}")
    return app_root

class CustomElementManager:
    def __init__(self, charakter, settings_dir=None, setting_name='SWAE'):
        self.charakter = charakter
        if settings_dir is None:
            app_root = get_application_root()
            settings_dir = app_root / 'settings'
        else:
            settings_dir = Path(settings_dir)

        self.settings_dir = settings_dir
        self.settings = {}
        self.active_setting = None

        # Laden der Einstellungen
        self.load_all_settings()

        # Setzen des aktiven Setting-Namens nach dem Laden der Settings
        self.active_setting_name = setting_name
        self.set_active_setting(self.active_setting_name)
        
    def load_all_settings(self):
        """Lädt alle Einstellungen aus dem settings-Verzeichnis."""
        if not self.settings_dir.exists():
            try:
                self.settings_dir.mkdir(parents=True, exist_ok=True)
                Logger.info(f"Settingverzeichnis erstellt: {self.settings_dir}")
            except OSError as e:
                Logger.error(f"Fehler beim Erstellen des Settingsverzeichnisses '{self.settings_dir}': {e}")
                return
        
        for filename in self.settings_dir.iterdir():
            if filename.suffix == '.json':
                try:
                    with filename.open('r', encoding='utf-8') as f:
                        setting_data = json.load(f)
                    
                    # Konvertiere 'fertigkeiten_daten' von Listen zurück zu Sets
                    if 'fertigkeiten_daten' in setting_data:
                        fertigkeiten_daten_loaded = setting_data['fertigkeiten_daten']
                        if isinstance(fertigkeiten_daten_loaded, dict):
                            for fertigkeit, attribut_list in fertigkeiten_daten_loaded.items():
                                if isinstance(attribut_list, list):
                                    setting_data['fertigkeiten_daten'][fertigkeit] = set(attribut_list)
                    
                    setting_name = setting_data.get('name', filename.stem)
                    self.settings[setting_name] = setting_data
                    Logger.info(f"Einstellung '{setting_name}' aus {filename.name} geladen.")
                except Exception as e:
                    Logger.error(f"Fehler beim Laden des Settings '{filename.name}': {e}")

    def get_all_settings(self):
        """Gibt eine Liste aller verfügbaren Settings zurück."""
        return list(self.settings.keys())
    
    def get_active_setting(self):
        """Gibt das aktive Setting zurück."""
        return self.active_setting
    
    def set_active_setting(self, setting_name):
        """Setzt das aktive Setting."""
        if setting_name in self.settings:
            self.active_setting = self.settings[setting_name]
            self.active_setting_name = setting_name
            Logger.info(f"Aktives Setting auf '{setting_name}' gesetzt.")
            return True
        else:
            Logger.warning(f"Setting '{setting_name}' existiert nicht.")
            return False
    
    def add_setting(self, name, setting_data, overwrite=False):
        settings_path = self.settings_dir / f"{name}.json"
        if settings_path.exists() and not overwrite:
            Logger.warning(f"Setting '{name}' existiert bereits und wird nicht überschrieben.")
            return False
        try:
            with settings_path.open('w', encoding='utf-8') as f:
                json.dump(setting_data, f, ensure_ascii=False, indent=4)
            self.settings[name] = setting_data
            Logger.info(f"Setting '{name}' erfolgreich gespeichert.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Settings '{name}': {e}")
            return False
    
    def save_setting(self, setting_name):
        """Speichert das aktuelle Setting unter dem angegebenen Namen."""
        if self.active_setting is None:
            Logger.error("Keine aktives Setting zum Speichern.")
            return
        
        setting_data = self.active_setting.copy()
        
        # Konvertiere 'fertigkeiten_daten' von Sets zu Listen
        if 'fertigkeiten_daten' in setting_data:
            fertigkeiten_daten = setting_data['fertigkeiten_daten']
            if isinstance(fertigkeiten_daten, dict):
                setting_data['fertigkeiten_daten'] = {k: list(v) for k, v in fertigkeiten_daten.items()}

        # Füge 'fertigkeiten' hinzu, indem du auf self.charakter.fertigkeiten zugreifst
        setting_data['fertigkeiten'] = {
            name: fertigkeit.to_dict_with_reset_wuerfel()
            for name, fertigkeit in self.charakter.fertigkeiten.items()
        }

        # Speichere die Daten
        filename = f"{setting_name}.json"
        filepath = self.settings_dir / filename
        try:
            with filepath.open('w', encoding='utf-8') as f:
                json.dump(setting_data, f, cls=SetEncoder, ensure_ascii=False, indent=4)
            self.settings[setting_name] = setting_data
            Logger.info(f"Einstellung '{setting_name}' in {filename} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Einstellung '{setting_name}': {e}")
    
    def delete_setting(self, setting_name):
        """Löscht eine Einstellung."""
        if setting_name not in self.settings:
            Logger.warning(f"Einstellung '{setting_name}' existiert nicht.")
            return False
        filename = f"{setting_name}.json"
        filepath = self.settings_dir / filename
        try:
            filepath.unlink()
            del self.settings[setting_name]
            Logger.info(f"Einstellung '{setting_name}' aus {filename} gelöscht.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Einstellung '{setting_name}': {e}")
            return False
    
    def update_element(self, element_type, element_name, element_data):
        """Aktualisiert oder fügt ein Element zur aktiven Einstellung hinzu."""
        if self.active_setting is None:
            Logger.error("Keine aktive Einstellung zum Aktualisieren.")
            return False
        if element_type not in self.active_setting:
            self.active_setting[element_type] = {}
        self.active_setting[element_type][element_name] = element_data
        Logger.info(f"Element '{element_name}' zum Typ '{element_type}' hinzugefügt/aktualisiert.")
        return True
    
    def remove_element(self, element_type, element_name):
        """Entfernt ein Element aus der aktiven Einstellung."""
        if self.active_setting is None:
            Logger.error("Keine aktive Einstellung zum Entfernen von Elementen.")
            return False
        if element_type in self.active_setting and element_name in self.active_setting[element_type]:
            del self.active_setting[element_type][element_name]
            Logger.info(f"Element '{element_name}' vom Typ '{element_type}' entfernt.")
            return True
        else:
            Logger.warning(f"Element '{element_name}' vom Typ '{element_type}' existiert nicht.")
            return False


