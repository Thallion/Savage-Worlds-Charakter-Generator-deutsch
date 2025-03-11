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
import functions.charakter_speicher as charakter_speicher
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

    def speichern_als_json(self, dateipfad):
        """
        Speichert den Charakter als JSON-Datei.
        
        Args:
            dateipfad (str): Der Pfad zur Zieldatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        import functions.charakter_speicher as charakter_speicher
        try:
            charakter_speicher.speichern_als_json(self, dateipfad)
            Logger.info(f"Charakter erfolgreich in {dateipfad} gespeichert.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Charakters: {e}")
            return False


    def laden_von_json(self, dateipfad):
        """
        Lädt einen Charakter aus einer JSON-Datei.
        
        Args:
            dateipfad (str): Der Pfad zur JSON-Datei
            
        Returns:
            bool: True, wenn das Laden erfolgreich war, sonst False
        """
        try:
            with open(dateipfad, 'r', encoding='utf-8') as f:
                daten = json.load(f)
            
            # Wichtige Informationen vorübergehend speichern
            altes_setting = self.active_setting_name
            
            # Backup der aktiven Ausrüstung erstellen
            temp_ausruestung = {}
            for name, item in self.ausruestung.items():
                temp_ausruestung[name] = item
            
            # Backup der ausgewählten Ausrüstung
            temp_selected_waffen = list(self.selected_waffen)
            temp_selected_ruestungen = list(self.selected_ruestungen)
            temp_selected_schilde = list(self.selected_schilde)
            temp_selected_allgemeine_ausruestung = list(self.selected_allgemeine_ausruestung)
            
            # Alle Daten aus der JSON in dieses Charakterobjekt laden (von charakter_speicher.from_dict)
            import functions.charakter_speicher as charakter_speicher
            charakter_speicher.from_dict(self, daten)
            Logger.info(f"Charakter erfolgreich von {dateipfad} geladen.")
            
            # Verhindern, dass load_elements_from_active_setting die Ausrüstung überschreibt
            # Wir laden die Elemente aus dem Setting mit Ausnahme der Ausrüstung
            if "voelker" in daten and "handicaps" in daten and "talente" in daten and "maechte" in daten:
                Logger.info("Ausrüstung aus der gespeicherten Datei verwenden, nicht aus dem Setting")
                # Wir laden KEINE Elemente aus dem Setting, da die Elemente bereits geladen wurden
                # Prüfen, ob das Setting erfolgreich aktiviert werden konnte
                if self.active_setting_name != altes_setting:
                    if not self.custom_element_manager.set_active_setting(self.active_setting_name):
                        Logger.warning(f"Das Setting '{self.active_setting_name}' konnte nicht aktiviert werden.")
                        # Fallback auf Standard-Setting
                        if "SWAE" in self.custom_element_manager.get_all_settings():
                            Logger.warning("Wechsle zurück zum Standard-Setting 'SWAE'.")
                            self.active_setting_name = "SWAE"
                            self.custom_element_manager.set_active_setting(self.active_setting_name)
                        else:
                            # Standard-Setting erstellen, wenn es nicht existiert
                            Logger.warning("Standard-Setting 'SWAE' nicht gefunden. Erstelle es neu.")
                            default_setting = self.create_default_setting()
                            self.custom_element_manager.add_setting("SWAE", default_setting, overwrite=True)
                            self.active_setting_name = "SWAE"
                            self.custom_element_manager.set_active_setting("SWAE")
            else:
                Logger.warning("Unvollständige Charakterdaten, lade Elemente aus dem aktiven Setting")
                # Für den Fall, dass wir unvollständige Daten haben, laden wir die Elemente aus dem Setting
                if "ausruestung" in daten:
                    # Ausrüstung aus den Daten wiederherstellen
                    self.ausruestung = temp_ausruestung
                    self.selected_waffen = temp_selected_waffen
                    self.selected_ruestungen = temp_selected_ruestungen
                    self.selected_schilde = temp_selected_schilde
                    self.selected_allgemeine_ausruestung = temp_selected_allgemeine_ausruestung
                
                # Aktiviere das Setting, ohne die Ausrüstung zu laden
                self.load_elements_from_active_setting()
            
            # Abgeleitete Werte berechnen
            self.berechne_abgeleitete_werte()
            
            # UI aktualisieren
            self.dispatch('on_charakter_change')
            
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Charakters: {e}", exc_info=True)
            return False

    def to_dict(self):
        """
        Konvertiert diesen Charakter in ein Dictionary.
        
        Returns:
            dict: Dictionary mit den Charakterdaten
        """
        import functions.charakter_speicher as charakter_speicher
        return charakter_speicher.to_dict(self)

    def from_dict(self, data):
        """
        Lädt Daten aus einem Dictionary in diesen Charakter.
        
        Args:
            data (dict): Dictionary mit Charakterdaten
        """
        import functions.charakter_speicher as charakter_speicher
        charakter_speicher.from_dict(self, data)

    def create_default_setting(self):
        return setting_funktionen.create_default_setting(self)

    def load_elements_from_active_setting(self):
        return setting_funktionen.load_elements_from_active_setting(self)

    def reload_character_data(self):
        """Aktualisiert den Charakter, um nach dem Laden eines neuen Settings alle Elemente korrekt zu laden."""
        data = self.to_dict()
        self.from_dict(data)

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

    def steigere_fertigkeit(self, fertigkeit_name, confirm_double_cost=False):
        """
        Steigert eine Fertigkeit um eine Stufe.
        
        Args:
            fertigkeit_name: Der Name der zu steigernden Fertigkeit
            confirm_double_cost: Bestätigung für doppelte Kosten, wenn der Fertigkeitswert das Attribut übersteigt
            
        Returns:
            str oder bool: "needs_confirmation" wenn Bestätigung erforderlich ist, True bei Erfolg, False bei Misserfolg
        """
        return eigenschaften_funktionen.steigere_fertigkeit(self, fertigkeit_name, confirm_double_cost)

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
        """
        Überprüft den Status der Charaktergenerierung, löst aber keine automatische Änderung mehr aus.
        Dient jetzt hauptsächlich zu Informationszwecken.
        """
        if (self.verbleibende_attributsteigerungen == 0 and 
            self.verbleibende_fertigkeitssteigerungen == 0 and
            self.verbleibende_handicap_punkte == 0):
            if not self.char_gen_completed:
                Logger.debug("Charaktergenerierung könnte abgeschlossen werden (alle Punkte verbraucht).")
        else:
            if self.char_gen_completed:
                Logger.debug("Hinweis: Charaktergenerierung ist als abgeschlossen markiert, aber es sind noch Punkte übrig.")

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