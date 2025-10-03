#charakter.py
"""
Hauptklasse für die Charakterverwaltung.
Kombiniert alle Teilmodule zu einer vollständigen Charakter-Klasse.
"""
from kivy.event import EventDispatcher
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
import json

# Import der Mixin-Klassen
from models.charakter_properties import CharakterProperties
from models.charakter_persistence import CharakterPersistence
from models.charakter_equipment import CharakterEquipment
from models.charakter_elements import CharakterElements

# Import der Manager und Funktionen
from manager.volk_manager import VolkManager
from models.settingregeln import SettingRegeln
from functions.setting_funktionen import CustomElementManager, SetEncoder
import functions.eigenschaften_funktionen as eigenschaften_funktionen
import functions.character_advancement as character_advancement
import functions.abgeleitete_werte as abgeleitete_werte
import functions.setting_funktionen as setting_funktionen

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


class Charakter(EventDispatcher, CharakterProperties, CharakterPersistence, 
                CharakterEquipment, CharakterElements):
    """
    Klasse zur Darstellung eines Charakters.
    VOLLSTÄNDIG: Mit Setting-Merging und Element-Verwaltung
    """
    __events__ = ('on_charakter_change',)

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

        # Temporäres Attribut für Voraussetzungsfehlermeldungen
        self.temp_voraussetzungs_fehler = []
        self.ignore_voraussetzungen = False

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
        self.anzahl_maechte = 0
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

        self.pathfinder_kostenlose_talente_gewaehlt = 0  # Zähler für kostenlose Pathfinder-Talente
    
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

        # Lade nun alle Elemente aus dem aktiven Setting (für neuen Charakter: replace_mode=True)
        self.load_elements_from_active_setting(replace_mode=True)

        # Fertigkeiten initialisieren (Daten wurden aus dem Setting geladen)
        self.initialisiere_fertigkeiten()
        self.bind(fertigkeiten=self.on_fertigkeiten_changed)

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

    # === SETTING-FUNKTIONEN ===
    def create_default_setting(self):
        return setting_funktionen.create_default_setting(self)

    def load_elements_from_active_setting(self, skip_equipment=False, merge_elements=True, replace_mode=False):
        """
        Lädt alle Elemente aus dem aktiven Setting.
        
        Args:
            skip_equipment (bool): Wenn True, wird die Ausrüstung nicht geladen
            merge_elements (bool): Wenn True, werden Elemente gemerged statt ersetzt
            replace_mode (bool): Wenn True, werden alle Elemente komplett ersetzt
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        return setting_funktionen.load_elements_from_active_setting(
            self, skip_equipment, merge_elements, replace_mode
        )

    def change_active_setting(self, setting_name, merge_elements=True):
        """
        Wechselt das aktive Setting und lädt die entsprechenden Elemente.
        
        Args:
            setting_name (str): Name des neuen Settings
            merge_elements (bool): Wenn True, werden Elemente gemerged statt ersetzt
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            old_setting = self.active_setting_name
            
            # Setting wechseln
            if self.custom_element_manager.set_active_setting(setting_name):
                Logger.info(f"Setting von '{old_setting}' zu '{setting_name}' gewechselt")
                
                # Elemente aus dem neuen Setting laden (mit Merging)
                success = self.load_elements_from_active_setting(merge_elements=merge_elements)
                
                if success:
                    self.active_setting_name = setting_name
                    
                    # Speichere das neue Setting als letztes Setting in der Config
                    self._save_last_setting_to_config(setting_name)
                    
                    # Abgeleitete Werte neu berechnen
                    self.berechne_abgeleitete_werte()
                    # UI aktualisieren
                    self.dispatch('on_charakter_change')
                    Logger.info(f"Setting-Wechsel zu '{setting_name}' erfolgreich abgeschlossen")
                    return True
                else:
                    Logger.error(f"Fehler beim Laden der Elemente für Setting '{setting_name}'")
                    # Zurück zum alten Setting wechseln
                    self.custom_element_manager.set_active_setting(old_setting)
                    return False
            else:
                Logger.error(f"Setting '{setting_name}' konnte nicht aktiviert werden")
                return False
                
        except Exception as e:
            Logger.error(f"Fehler beim Setting-Wechsel zu '{setting_name}': {e}", exc_info=True)
            return False
    
    def _save_last_setting_to_config(self, setting_name):
        """
        Speichert das Setting als letztes verwendetes Setting in der Konfiguration
        
        Args:
            setting_name (str): Name des Settings
        """
        try:
            from services.service_container import service_container
            config_service = service_container.get_config_service()
            
            if config_service:
                config_service.set('last_setting', setting_name)
                Logger.info(f"Letztes Setting in Config gespeichert: {setting_name}")
            else:
                Logger.warning("ConfigService nicht verfügbar - letztes Setting konnte nicht gespeichert werden")
                
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des letzten Settings in Config: {str(e)}")

    # === EIGENSCHAFTEN-FUNKTIONEN ===
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

    # === CHARAKTERENTWICKLUNG ===
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

    # === BERECHNUNGEN ===
    def berechne_abgeleitete_werte(self):
        return abgeleitete_werte.berechne_abgeleitete_werte(self)

    # === EVENT-HANDLER ===
    def on_charakter_change(self, *args):
        self.berechne_abgeleitete_werte()

    def on_attribut_wert_change(self, instance, value):
        Logger.debug(f"Attribut '{instance.attribut_name}' Wert geändert zu {value}.")
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_attribut_modifier_change(self, instance, value):
        Logger.debug(f"Attribut '{instance.attribut_name}' Modifier geändert zu {value}.")
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_fertigkeit_wert_change(self, instance, value):
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_fertigkeit_modifier_change(self, instance, value):
        self.berechne_abgeleitete_werte()
        self.dispatch('on_charakter_change')

    def on_fertigkeiten_changed(self, instance, value):
        pass

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
        else:
            Logger.debug("Charaktergenerierung noch nicht abgeschlossen.")

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