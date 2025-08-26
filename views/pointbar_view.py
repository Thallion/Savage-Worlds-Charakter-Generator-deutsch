# views/pointbar_view.py
# Änderungen:
# - Theme-adaptive Farben für bessere Integration
# - Flexible Skalierung mit relativen Größen
# - Responsive Design für verschiedene Bildschirmgrößen
# - Moderne KivyMD 2.0.1 Komponenten
# - Bessere visuelle Hierarchie mit Cards
# - Adaptive Textgrößen und Spacing
# - KORREKTUR: Robustheit-Anzeige in Pointbar

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp

# KivyMD-Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.theming import ThemableBehavior

# Path utilities import
from utils.path_utils import get_assets_path

class LabelValuePair(MDBoxLayout):
    """Theme-adaptive Label-Wert-Paar mit flexibler Skalierung."""
    key_text = StringProperty("")
    value_text = StringProperty("")
    key_width_ratio = NumericProperty(0.6)  # Anteil für den Schlüssel

kv = '''
<LabelValuePair>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(24)
    spacing: dp(8)
    adaptive_height: True

    MDLabel:
        text: root.key_text
        theme_text_color: "Primary"
        halign: 'left'
        valign: 'center'
        size_hint_x: root.key_width_ratio
        font_size: dp(11)
        shorten: True
        shorten_from: 'right'
        text_size: self.size

    MDLabel:
        text: root.value_text
        theme_text_color: "Secondary" 
        halign: 'left'
        valign: 'center'
        size_hint_x: 1 - root.key_width_ratio
        font_size: dp(11)
        bold: True
        shorten: True
        shorten_from: 'right'
        text_size: self.size

<GenerationPointsBar>:
    orientation: 'horizontal'
    spacing: dp(12)
    size_hint_y: None
    height: dp(100)
    padding: [dp(12), dp(8), dp(12), dp(8)]
    md_bg_color: app.theme_cls.backgroundColor

    # Logo-Container
    MDCard:
        style: "elevated"
        size_hint_x: None
        width: dp(130)
        size_hint_y: None
        height: dp(116)  # Etwas höher als die anderen Cards
        md_bg_color: app.theme_cls.surfaceColor
        elevation: 1
        radius: [dp(6)]
        padding: dp(4)
        
        Image:
            source: root.get_logo_path()
            size_hint: 1, 1
            allow_stretch: True
            keep_ratio: True
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

    # Hauptinformations-Container
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_x: 1

        # Erste Spalte: Charakterdaten
        MDCard:
            style: "elevated"
            padding: dp(8)
            spacing: dp(2)
            size_hint_x: 0.28
            size_hint_y: None
            height: self.minimum_height
            md_bg_color: app.theme_cls.surfaceColor
            elevation: 1
            radius: [dp(6)]

            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(1)
                adaptive_height: True
            
                LabelValuePair:
                    key_text: "Name:"
                    value_text: root.char_name_text
                    key_width_ratio: 0.32
                
                LabelValuePair:
                    key_text: "Setting:"
                    value_text: root.active_setting_name_text
                    key_width_ratio: 0.32
                
                LabelValuePair:
                    key_text: "Rang:"
                    value_text: root.rang_text
                    key_width_ratio: 0.32
                    
                LabelValuePair:
                    key_text: "Aufstiege:"
                    value_text: root.aufstiege_text
                    key_width_ratio: 0.32

        # Zweite Spalte: Generierungspunkte
        MDCard:
            style: "elevated"
            padding: dp(8)
            spacing: dp(2)
            size_hint_x: 0.36
            size_hint_y: None
            height: self.minimum_height
            md_bg_color: app.theme_cls.surfaceColor
            elevation: 1
            radius: [dp(6)]

            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(1)
                adaptive_height: True
            
                LabelValuePair:
                    key_text: "Attribute-Punkte:"
                    value_text: root.attribut_text
                    key_width_ratio: 0.65
                
                LabelValuePair:
                    key_text: "Fähigkeiten-Punkte:"
                    value_text: root.faehigkeiten_text
                    key_width_ratio: 0.65
                
                LabelValuePair:
                    key_text: "Handicap-Punkte:"
                    value_text: root.handicaps_text
                    key_width_ratio: 0.65
                    
                LabelValuePair:
                    key_text: "Anzahl Mächte:"
                    value_text: root.maechte_text
                    key_width_ratio: 0.65

        # Dritte Spalte: Ressourcen
        MDCard:
            style: "elevated"
            padding: dp(8)
            spacing: dp(2)
            size_hint_x: 0.36
            size_hint_y: None
            height: self.minimum_height
            md_bg_color: app.theme_cls.surfaceColor
            elevation: 1
            radius: [dp(6)]

            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(1)
                adaptive_height: True
            
                LabelValuePair:
                    key_text: "Machtpunkte:"
                    value_text: root.machtpunkte_text
                    key_width_ratio: 0.55

                LabelValuePair:
                    key_text: "Parade / Robustheit:"
                    value_text: root.parade_robustheit_text
                    key_width_ratio: 0.55
                
                LabelValuePair:
                    key_text: "Gewicht / Traglast:"
                    value_text: root.gewicht_text
                    key_width_ratio: 0.55
                
                LabelValuePair:
                    key_text: "Vermögen:"
                    value_text: root.vermoegen_text
                    key_width_ratio: 0.55
'''

Builder.load_string(kv)

class GenerationPointsBar(MDBoxLayout):
    charakter = ObjectProperty(None)  
    char_name_text = StringProperty("")
    active_setting_name_text = StringProperty("")
    attribut_text = StringProperty("")  
    faehigkeiten_text = StringProperty("")  
    aufstiege_text = StringProperty("")  
    maechte_text = StringProperty("")  
    machtpunkte_text = StringProperty("")  
    vermoegen_text = StringProperty("")  
    handicaps_text = StringProperty("")  
    gewicht_text = StringProperty("")  
    rang_text = StringProperty("")  
    parade_robustheit_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        self.controller.bind(charakter=self.on_charakter_changed)
        self.on_charakter_changed(self.controller, self.controller.charakter)
        
        # Timer für regelmäßige Gewichts-Updates
        self._weight_update_event = Clock.schedule_interval(self._update_weight_periodically, 2.0)
        
        Logger.info("GenerationPointsBar initialisiert und an Charakter-Änderungen gebunden.")

    def on_charakter_changed(self, instance, value):
        if hasattr(self, 'charakter') and self.charakter:
            self.unbind_charakter_properties()
        self.charakter = value
        if self.charakter:
            self.bind_charakter_properties()
            self.update_all_texts()

    def unbind_charakter_properties(self):
        """Entfernt alle Charakter-Property-Bindings"""
        if not self.charakter:
            return
            
        try:
            self.charakter.unbind(verbleibende_attributsteigerungen=self.update_attribut_text)
            self.charakter.unbind(maximale_attributsteigerungen=self.update_attribut_text)
            self.charakter.unbind(verbleibende_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            self.charakter.unbind(maximale_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            self.charakter.unbind(verbleibende_aufstiege=self.update_aufstiege_text)
            self.charakter.unbind(aufstiege_gesamt=self.update_aufstiege_text)
            self.charakter.unbind(verfuegbare_maechte=self.update_maechte_text)
            self.charakter.unbind(anzahl_maechte=self.update_maechte_text)
            self.charakter.unbind(machtpunkte=self.update_machtpunkte_text)
            self.charakter.unbind(vermoegen=self.update_vermoegen_text)
            self.charakter.unbind(waehrungseinheit=self.update_vermoegen_text)
            self.charakter.unbind(verbleibende_handicap_punkte=self.update_handicaps_text)
            self.charakter.unbind(gesamt_handicap_punkte=self.update_handicaps_text)
            self.charakter.unbind(gesamtgewicht=self.update_gewicht_text)
            self.charakter.unbind(maximale_traglast=self.update_gewicht_text)
            self.charakter.unbind(rang=self.update_rang_text)
            self.charakter.unbind(char_name=self.update_charakter_name)
            self.charakter.unbind(active_setting_name=self.update_setting_name)
            self.charakter.unbind(parade=self.update_parade_robustheit_text)
            self.charakter.unbind(robustheit=self.update_parade_robustheit_text)
            # KORREKTUR: Auch auf robustheit_mit_ruestung binden
            self.charakter.unbind(robustheit_mit_ruestung=self.update_parade_robustheit_text)
            Logger.debug("Charakter-Bindings erfolgreich entfernt")
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen der Charakter-Bindings: {str(e)}")

    def bind_charakter_properties(self):
        """Erstellt alle Charakter-Property-Bindings"""
        if not self.charakter:
            Logger.warning("Kein Charakter zum Binden verfügbar")
            return
            
        try:
            Logger.debug(f"GenerationPointsBar bindet an Charakter-Objekt mit ID {id(self.charakter)}")
            
            # Attribute und Fertigkeiten
            self.charakter.bind(verbleibende_attributsteigerungen=self.update_attribut_text)
            self.charakter.bind(maximale_attributsteigerungen=self.update_attribut_text)
            self.charakter.bind(verbleibende_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            self.charakter.bind(maximale_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            
            # Aufstiege und Fortschritt
            self.charakter.bind(verbleibende_aufstiege=self.update_aufstiege_text)
            self.charakter.bind(aufstiege_gesamt=self.update_aufstiege_text)
            self.charakter.bind(rang=self.update_rang_text)
            
            # Mächte und Machtpunkte
            self.charakter.bind(verfuegbare_maechte=self.update_maechte_text)
            self.charakter.bind(anzahl_maechte=self.update_maechte_text)
            self.charakter.bind(machtpunkte=self.update_machtpunkte_text)
            
            # Vermögen und Währung
            self.charakter.bind(vermoegen=self.update_vermoegen_text)
            self.charakter.bind(waehrungseinheit=self.update_vermoegen_text)
            
            # Handicaps
            self.charakter.bind(verbleibende_handicap_punkte=self.update_handicaps_text)
            self.charakter.bind(gesamt_handicap_punkte=self.update_handicaps_text)
            
            # Gewicht und Traglast - keine direkten Property-Bindings mehr
            # Stattdessen auf Events hören, die Gewichtsänderungen verursachen können
            
            # Charakterdaten
            self.charakter.bind(char_name=self.update_charakter_name)
            self.charakter.bind(active_setting_name=self.update_setting_name)

            # Parade & Robustheit - KORREKTUR: Auch auf robustheit_mit_ruestung binden
            self.charakter.bind(parade=self.update_parade_robustheit_text)
            self.charakter.bind(robustheit=self.update_parade_robustheit_text)
            self.charakter.bind(robustheit_mit_ruestung=self.update_parade_robustheit_text)
            
            Logger.info("GenerationPointsBar erfolgreich mit Charakter-Properties verbunden")
        except Exception as e:
            Logger.error(f"Fehler beim Binden der Charakter-Properties: {str(e)}")

    def update_all_texts(self):
        """Aktualisiert alle angezeigten Texte"""
        if not self.charakter:
            Logger.warning("Kein Charakter für Text-Update verfügbar")
            return
            
        try:
            # Grunddaten
            self.char_name_text = self.charakter.char_name if self.charakter.char_name else "Unbekannt"
            self.active_setting_name_text = self.charakter.active_setting_name if self.charakter.active_setting_name else "Unbekanntes Setting"

            # Alle spezifischen Updates aufrufen
            self.update_attribut_text(None, None)
            self.update_faehigkeiten_text(None, None)
            self.update_aufstiege_text(None, None)
            self.update_maechte_text(None, None)
            self.update_machtpunkte_text(None, None)
            self.update_vermoegen_text(None, None)
            self.update_handicaps_text(None, None)
            self.update_gewicht_text(None, None)
            self.update_rang_text(None, None)
            self.update_parade_robustheit_text(None, None)     
            
            Logger.debug("Alle Texte erfolgreich aktualisiert")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Texte: {str(e)}")

    # Event-Handler für einzelne Eigenschaften
    def update_charakter_name(self, instance, value):
        """Aktualisiert den Charakternamen"""
        self.char_name_text = value if value else "Unbekannt"

    def update_setting_name(self, instance, value):
        """Aktualisiert den Setting-Namen"""
        self.active_setting_name_text = value if value else "Unbekanntes Setting"

    def update_attribut_text(self, instance, value):
        """Aktualisiert die Attribut-Anzeige"""
        if self.charakter:
            self.attribut_text = f"{self.charakter.verbleibende_attributsteigerungen} / {self.charakter.maximale_attributsteigerungen}"

    def update_handicaps_text(self, instance, value):
        """Aktualisiert die Handicap-Anzeige"""
        if self.charakter:
            self.handicaps_text = f"{self.charakter.verbleibende_handicap_punkte} / {self.charakter.gesamt_handicap_punkte}"

    def update_faehigkeiten_text(self, instance, value):
        """Aktualisiert die Fertigkeits-Anzeige"""
        if self.charakter:
            self.faehigkeiten_text = f"{self.charakter.verbleibende_fertigkeitssteigerungen} / {self.charakter.maximale_fertigkeitssteigerungen}"

    def update_aufstiege_text(self, instance, value):
        """Aktualisiert die Aufstiegs-Anzeige"""
        if self.charakter:
            self.aufstiege_text = f"{self.charakter.verbleibende_aufstiege} / {self.charakter.aufstiege_gesamt}"

    def update_maechte_text(self, instance, value):
        """Aktualisiert die Mächte-Anzeige"""
        if self.charakter:
            self.maechte_text = f"{self.charakter.verfuegbare_maechte} / {self.charakter.anzahl_maechte}"

    def update_machtpunkte_text(self, instance, value):
        """Aktualisiert die Machtpunkte-Anzeige"""
        if self.charakter:
            self.machtpunkte_text = f"{self.charakter.machtpunkte}"

    def update_vermoegen_text(self, instance, value):
        """Aktualisiert die Vermögens-Anzeige"""
        if self.charakter:
            self.vermoegen_text = f"{self.charakter.vermoegen} {self.charakter.waehrungseinheit}"

    def update_gewicht_text(self, instance, value):
        """Aktualisiert die Gewichts-Anzeige"""
        if self.charakter:
            gewicht = self.charakter.berechne_gesamtgewicht()
            traglast = self.charakter.maximale_traglast
            self.gewicht_text = f"{gewicht} / {traglast} kg"

    def update_rang_text(self, instance, value):
        """Aktualisiert die Rang-Anzeige"""
        if self.charakter:
            self.rang_text = f"{self.charakter.rang}"
            Logger.debug(f"Rang aktualisiert: {self.rang_text}")

    def update_parade_robustheit_text(self, instance, value):
        """Aktualisiert die Parade-Robustheit-Anzeige - KORRIGIERT"""
        if self.charakter:
            # KORREKTUR: Prüfe zuerst robustheit_mit_ruestung (enthält formatierte Rüstungsinfo)
            robustheit_text = getattr(self.charakter, 'robustheit_mit_ruestung', '')
            
            # Wenn robustheit_mit_ruestung leer oder nicht verfügbar ist, verwende robustheit als Fallback
            if not robustheit_text:
                robustheit_wert = getattr(self.charakter, 'robustheit', 2)
                robustheit_text = str(robustheit_wert)
                Logger.debug(f"Fallback auf robustheit: {robustheit_text}")
            else:
                Logger.debug(f"Verwende robustheit_mit_ruestung: {robustheit_text}")

            parade_wert = getattr(self.charakter, 'parade', 2)
            self.parade_robustheit_text = f"{parade_wert} / {robustheit_text}"
            
            Logger.debug(f"Parade/Robustheit aktualisiert: {self.parade_robustheit_text}")

    def _update_weight_periodically(self, dt):
        """Timer-Callback für regelmäßige Gewichts-Updates"""
        if self.charakter:
            self.update_gewicht_text(None, None)
        return True  # Timer weiterlaufen lassen

    def get_logo_path(self):
        """Gibt den korrekten Pfad zum Logo zurück (PyInstaller-kompatibel)"""
        return get_assets_path("Savage-Worlds-Fanprodukt-Logo.png")

    def cleanup(self):
        """Bereinigt die Pointbar beim Herunterfahren"""
        try:
            # Timer stoppen
            if hasattr(self, '_weight_update_event'):
                Clock.unschedule(self._weight_update_event)
                
            if self.charakter:
                self.unbind_charakter_properties()
            if self.controller:
                self.controller.unbind(charakter=self.on_charakter_changed)
            Logger.info("GenerationPointsBar erfolgreich bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen der GenerationPointsBar: {str(e)}")