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
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp

# KivyMD-Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import RotateBehavior
from kivymd.uix.list import MDListItemTrailingIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard


class TrailingPressedIconButton(ButtonBehavior, RotateBehavior, MDListItemTrailingIcon):
    """Icon-Button mit Rotation für ExpansionPanel-Chevron"""
    pass

# Path utilities import
from utils.path_utils import get_assets_path
from functions.superkraft_funktionen import ist_superkraefte_setting

class LabelValuePair(MDBoxLayout):
    """Theme-adaptive Label-Wert-Paar mit flexibler Skalierung."""
    key_text = StringProperty("")
    value_text = StringProperty("")
    key_width_ratio = NumericProperty(0.6)  # Anteil für den Schlüssel

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei (mit Mobile-Unterstützung)
def load_kv_file():
    from utils.platform_utils import is_mobile_layout

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))

    # Mobile-KV bevorzugen wenn verfügbar
    mobile = is_mobile_layout()
    kv_name = 'pointbar_view_mobile.kv' if mobile else 'pointbar_view.kv'
    kv_path = os.path.join(base_path, 'views', kv_name)

    # Fallback auf Desktop-KV wenn Mobile-KV nicht existiert
    if not os.path.exists(kv_path):
        kv_path = os.path.join(base_path, 'views', 'pointbar_view.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
        Logger.info(f"PointbarView: KV-Datei geladen: {os.path.basename(kv_path)}")
    else:
        Logger.error(f"PointbarView: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

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
    superkraft_punkte_text = StringProperty("")
    machtstufe_text = StringProperty("")
    header_summary_text = StringProperty("")
    char_gen_completed = BooleanProperty(False)
    is_expanded = BooleanProperty(True)
    kann_undo = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        self.controller.bind(charakter=self.on_charakter_changed)
        self.on_charakter_changed(self.controller, self.controller.charakter)

        # Timer für regelmäßige Gewichts-Updates
        self._weight_update_event = Clock.schedule_interval(self._update_weight_periodically, 2.0)

        # Undo-Status initialisieren
        self._update_undo_status()

        # MDExpansionPanel-Status tracken (Mobile)
        Clock.schedule_once(self._bind_expansion_panel, 0)

        Logger.info("GenerationPointsBar initialisiert und an Charakter-Änderungen gebunden.")

    def _bind_expansion_panel(self, dt):
        """Bindet an das MDExpansionPanel, um is_expanded zu synchronisieren."""
        panel = self.ids.get('expansion_panel')
        if panel:
            panel.bind(is_open=self._on_panel_state_changed)

    def _on_panel_state_changed(self, panel, is_open):
        """Callback wenn MDExpansionPanel geöffnet/geschlossen wird."""
        self.is_expanded = is_open
        chevron = self.ids.get('chevron')
        if chevron:
            if is_open:
                panel.set_chevron_up(chevron)
            else:
                panel.set_chevron_down(chevron)

    def on_charakter_changed(self, instance, value):
        if hasattr(self, 'charakter') and self.charakter:
            self.unbind_charakter_properties()
        self.charakter = value
        if self.charakter:
            self.bind_charakter_properties()
            self.update_all_texts()
            # char_gen_completed Status aktualisieren
            self._update_char_gen_status(self.charakter, self.charakter.char_gen_completed)
            # Undo-Status aktualisieren
            self._update_undo_status()

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
            # gesamtgewicht ist ein @property, kein Kivy Property - kein unbind nötig
            # maximale_traglast wird nicht mehr gebunden, daher auch kein unbind
            self.charakter.unbind(rang=self.update_rang_text)
            self.charakter.unbind(char_name=self.update_charakter_name)
            self.charakter.unbind(active_setting_name=self.update_setting_name)
            self.charakter.unbind(superkraft_punkte_gesamt=self.update_superkraft_punkte_text)
            self.charakter.unbind(superkraft_punkte_verbraucht=self.update_superkraft_punkte_text)
            self.charakter.unbind(machtstufe=self.update_machtstufe_text)
            self.charakter.unbind(parade=self.update_parade_robustheit_text)
            self.charakter.unbind(robustheit=self.update_parade_robustheit_text)
            # KORREKTUR: Auch auf robustheit_mit_ruestung binden
            self.charakter.unbind(robustheit_mit_ruestung=self.update_parade_robustheit_text)
            self.charakter.unbind(char_gen_completed=self._update_char_gen_status)
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

            # Superkräfte (SKP)
            self.charakter.bind(superkraft_punkte_gesamt=self.update_superkraft_punkte_text)
            self.charakter.bind(superkraft_punkte_verbraucht=self.update_superkraft_punkte_text)
            self.charakter.bind(machtstufe=self.update_machtstufe_text)
            
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

            # Generierungsstatus
            self.charakter.bind(char_gen_completed=self._update_char_gen_status)

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
            self.update_superkraft_punkte_text(None, None)
            self.update_machtstufe_text(None, None)
            self._update_char_gen_status(None, None)

            self.update_header_summary()

            Logger.debug("Alle Texte erfolgreich aktualisiert")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Texte: {str(e)}")

    def update_header_summary(self):
        """Aktualisiert den kompakten Header-Text für den eingeklappten Zustand"""
        if not self.charakter:
            self.header_summary_text = ""
            return

        name = self.charakter.char_name if self.charakter.char_name else "Unbekannt"
        setting = self.charakter.active_setting_name if self.charakter.active_setting_name else "—"
        attr_verbraucht = self.charakter.maximale_attributsteigerungen - self.charakter.verbleibende_attributsteigerungen
        fert_verbraucht = self.charakter.maximale_fertigkeitssteigerungen - self.charakter.verbleibende_fertigkeitssteigerungen
        attr = f"{attr_verbraucht}/{self.charakter.maximale_attributsteigerungen}"
        fert = f"{fert_verbraucht}/{self.charakter.maximale_fertigkeitssteigerungen}"
        rang = self.charakter.rang if self.charakter.rang else "Anfänger"

        from kivy.core.window import Window
        # Kompaktere Darstellung im Portrait
        if Window.height > Window.width:
            self.header_summary_text = f"{name} | {setting} | A:{attr} | F:{fert}"
        else:
            self.header_summary_text = f"{name} | {setting} | Attr: {attr} | Fert: {fert} | {rang}"

    def toggle_panel(self, *args):
        """Klappt den Detail-Bereich auf oder zu"""
        # MDExpansionPanel-Variante (Mobile)
        panel = self.ids.get('expansion_panel')
        if panel:
            if panel.is_open:
                panel.close()
            else:
                panel.open()
            return

        # Desktop: is_expanded togglen, KV-Bindings erledigen den Rest
        self.is_expanded = not self.is_expanded

    def _get_char_verwaltung(self):
        """Holt das CharakterVerwaltungWidget über die App."""
        app = App.get_running_app()
        if hasattr(app, '_get_charakter_verwaltung_widget'):
            return app._get_charakter_verwaltung_widget()
        if hasattr(app, 'charakter_verwaltung_widget'):
            return app.charakter_verwaltung_widget
        return None

    def on_schnellspeichern(self, *args):
        """Schnellspeichern über die Toolbar"""
        try:
            widget = self._get_char_verwaltung()
            if widget:
                widget.schnellspeichern_charakter()
        except Exception as e:
            Logger.error(f"Schnellspeichern-Fehler: {e}")

    def on_laden(self, *args):
        """Charakter laden über die Toolbar"""
        try:
            widget = self._get_char_verwaltung()
            if widget:
                widget.lade_charakter()
        except Exception as e:
            Logger.error(f"Laden-Fehler: {e}")

    # Undo-Funktionalität
    def _update_undo_status(self, *args):
        """Aktualisiert den Undo-Button-Status."""
        self.kann_undo = self.controller.kann_undo

    def on_undo_pressed(self, *args):
        """Wird beim Klick auf den Undo-Button aufgerufen."""
        beschreibung = self.controller.undo()
        if beschreibung:
            try:
                from services.service_container import service_container
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_success_dialog(f"Rückgängig: {beschreibung}")
            except Exception:
                pass
            self._update_undo_status()

    # Event-Handler für einzelne Eigenschaften
    def update_charakter_name(self, instance, value):
        """Aktualisiert den Charakternamen"""
        self.char_name_text = value if value else "Unbekannt"
        self.update_header_summary()

    def update_setting_name(self, instance, value):
        """Aktualisiert den Setting-Namen und aktualisiert kontextabhängige Anzeigen"""
        self.active_setting_name_text = value if value else "Unbekanntes Setting"
        # Mächte/SKP-Anzeigen bei Setting-Wechsel neu berechnen
        self.update_maechte_text(None, None)
        self.update_machtpunkte_text(None, None)
        self.update_superkraft_punkte_text(None, None)
        self.update_machtstufe_text(None, None)

    def update_attribut_text(self, instance, value):
        """Aktualisiert die Attribut-Anzeige (verbrauchte / maximale)"""
        if self.charakter:
            verbraucht = self.charakter.maximale_attributsteigerungen - self.charakter.verbleibende_attributsteigerungen
            self.attribut_text = f"{verbraucht} / {self.charakter.maximale_attributsteigerungen}"
            self.update_header_summary()

    def update_handicaps_text(self, instance, value):
        """Aktualisiert die Handicap-Anzeige (verbrauchte / maximale)"""
        if self.charakter:
            verbraucht = self.charakter.gesamt_handicap_punkte - self.charakter.verbleibende_handicap_punkte
            self.handicaps_text = f"{verbraucht} / {self.charakter.gesamt_handicap_punkte}"

    def update_faehigkeiten_text(self, instance, value):
        """Aktualisiert die Fertigkeits-Anzeige (verbrauchte / maximale)"""
        if self.charakter:
            verbraucht = self.charakter.maximale_fertigkeitssteigerungen - self.charakter.verbleibende_fertigkeitssteigerungen
            self.faehigkeiten_text = f"{verbraucht} / {self.charakter.maximale_fertigkeitssteigerungen}"
            self.update_header_summary()

    def update_aufstiege_text(self, instance, value):
        """Aktualisiert die Aufstiegs-Anzeige (verbrauchte / maximale)"""
        if self.charakter:
            verbraucht = self.charakter.aufstiege_gesamt - self.charakter.verbleibende_aufstiege
            self.aufstiege_text = f"{verbraucht} / {self.charakter.aufstiege_gesamt}"

    def update_maechte_text(self, instance, value):
        """Aktualisiert die Mächte-Anzeige (gewählte / maximale)"""
        if self.charakter:
            gewaehlt = self.charakter.anzahl_maechte - self.charakter.verfuegbare_maechte
            self.maechte_text = f"{gewaehlt} / {self.charakter.anzahl_maechte}"

    def update_machtpunkte_text(self, instance, value):
        """Aktualisiert die Machtpunkte-Anzeige"""
        if self.charakter:
            self.machtpunkte_text = f"{self.charakter.machtpunkte}"

    def update_superkraft_punkte_text(self, instance, value):
        """Aktualisiert die SKP-Anzeige (verbrauchte / maximale, leer bei Nicht-Superkräfte-Settings)"""
        if self.charakter:
            if ist_superkraefte_setting(self.charakter.active_setting_name):
                verbraucht = self.charakter.superkraft_punkte_verbraucht
                gesamt = self.charakter.superkraft_punkte_gesamt
                self.superkraft_punkte_text = f"{verbraucht} / {gesamt} (OG: {self.charakter.kraftobergrenze})"
            else:
                self.superkraft_punkte_text = ""

    def update_machtstufe_text(self, instance, value):
        """Aktualisiert die Machtstufe-Anzeige (leer bei Nicht-Superkräfte-Settings)"""
        if self.charakter:
            if ist_superkraefte_setting(self.charakter.active_setting_name):
                self.machtstufe_text = f"{self.charakter.machtstufe}"
            else:
                self.machtstufe_text = ""

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
            self.update_header_summary()
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

    def toggle_char_gen_completed(self, *args):
        """Umschaltet den Charakter-Generierungsstatus über die Pointbar"""
        if self.charakter:
            new_value = not self.charakter.char_gen_completed
            self.charakter.char_gen_completed = new_value
            self.char_gen_completed = new_value
            Logger.info(f"Charakter-Generierungsstatus über Pointbar geändert: {new_value}")

    def _update_char_gen_status(self, instance, value):
        """Aktualisiert den lokalen char_gen_completed-Status aus dem Charakter-Modell"""
        if self.charakter:
            self.char_gen_completed = self.charakter.char_gen_completed

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