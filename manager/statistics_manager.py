# views/statistics_manager.py
"""
Statistics Manager für Einstellungen-Widget
Kapselt alle Statistik-bezogenen Funktionalitäten
"""

from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from services.service_container import service_container


class StatisticsManager:
    """Manager für Statistik-bezogene Funktionalitäten"""
    
    def __init__(self, widget):
        self.widget = widget
        self.dialog_service = service_container.get_dialog_service()
        
    def show_element_statistics(self):
        """Zeigt Element-Statistiken in einem Dialog an"""
        try:
            Logger.info("Element-Statistiken angefordert")
            
            # Prüfe verfügbare Services
            if not self.dialog_service:
                Logger.error("Dialog-Service nicht verfügbar")
                self._show_fallback_error("Dialog-Service nicht verfügbar.")
                return
            
            # Prüfe Controller über App
            controller = getattr(self.widget.app, 'controller', None)
            if not controller:
                Logger.error("CharakterController nicht verfügbar")
                self.dialog_service.show_error_dialog("CharakterController nicht verfügbar.")
                return
            
            # Prüfe Charakter
            if not hasattr(controller, 'charakter') or not controller.charakter:
                Logger.error("Charakter nicht verfügbar")
                self.dialog_service.show_error_dialog("Kein Charakter geladen. Bitte erstelle oder lade einen Charakter.")
                return
            
            # Debug-Informationen ausgeben
            char = controller.charakter
            Logger.info(f"Zeige Element-Statistiken für Charakter: {getattr(char, 'char_name', 'Unbenannt')}")
            
            # Dialog anzeigen
            self.dialog_service.show_element_statistics_dialog()
            
        except Exception as e:
            Logger.error(f"Unerwarteter Fehler bei Element-Statistiken: {str(e)}", exc_info=True)
            self._show_fallback_error(f"Fehler beim Anzeigen der Element-Statistiken: {str(e)}")
    
    def show_statblock(self):
        """Zeigt den Charakterstatblock in einem Dialog an"""
        if self.dialog_service:
            self.dialog_service.show_statblock_dialog()
        else:
            Logger.error("Dialog-Service nicht verfügbar")
    
    def get_element_counts(self):
        """Hilfsmethode zur Ermittlung der Element-Statistiken"""
        try:
            controller = getattr(self.widget.app, 'controller', None)
            if not controller or not controller.charakter:
                Logger.warning("Kein Charakter-Controller oder Charakter verfügbar")
                return {}
            
            char = controller.charakter
            Logger.debug(f"Ermittle Element-Counts für Charakter: {getattr(char, 'char_name', 'Unbenannt')}")
            
            # Sichere Attributzugriffe mit Fallbacks
            counts = {}
            
            try:
                # Handicaps
                handicaps = getattr(char, 'handicaps', {})
                selected_handicaps = getattr(char, 'selected_handicaps', [])
                counts['handicaps_total'] = len(handicaps)
                counts['handicaps_selected'] = len(selected_handicaps)
                Logger.debug(f"Handicaps: {counts['handicaps_total']} total, {counts['handicaps_selected']} selected")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen der Handicap-Daten: {str(e)}")
                counts['handicaps_total'] = 0
                counts['handicaps_selected'] = 0
            
            try:
                # Talente
                talente = getattr(char, 'talente', {})
                selected_talente = getattr(char, 'selected_talente', [])
                counts['talente_total'] = len(talente)
                counts['talente_selected'] = len(selected_talente)
                Logger.debug(f"Talente: {counts['talente_total']} total, {counts['talente_selected']} selected")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen der Talent-Daten: {str(e)}")
                counts['talente_total'] = 0
                counts['talente_selected'] = 0
            
            try:
                # Mächte
                maechte = getattr(char, 'maechte', {})
                selected_maechte = getattr(char, 'selected_maechte', [])
                counts['maechte_total'] = len(maechte)
                counts['maechte_selected'] = len(selected_maechte)
                Logger.debug(f"Mächte: {counts['maechte_total']} total, {counts['maechte_selected']} selected")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen der Macht-Daten: {str(e)}")
                counts['maechte_total'] = 0
                counts['maechte_selected'] = 0
            
            try:
                # Völker
                voelker = getattr(char, 'voelker', {})
                voelker_selected = getattr(char, 'voelker_selected', {})
                counts['voelker_total'] = len(voelker)
                counts['voelker_selected'] = sum(1 for selected in voelker_selected.values() if selected) if voelker_selected else 0
                Logger.debug(f"Völker: {counts['voelker_total']} total, {counts['voelker_selected']} selected")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen der Völker-Daten: {str(e)}")
                counts['voelker_total'] = 0
                counts['voelker_selected'] = 0
            
            try:
                # Ausrüstung
                ausruestung = getattr(char, 'ausruestung', {})
                counts['ausruestung_total'] = len(ausruestung)
                Logger.debug(f"Ausrüstung: {counts['ausruestung_total']} total")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen der Ausrüstung-Daten: {str(e)}")
                counts['ausruestung_total'] = 0
            
            try:
                # Fertigkeiten
                fertigkeiten = getattr(char, 'fertigkeiten', {})
                counts['fertigkeiten_total'] = len(fertigkeiten)
                Logger.debug(f"Fertigkeiten: {counts['fertigkeiten_total']} total")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen der Fertigkeiten-Daten: {str(e)}")
                counts['fertigkeiten_total'] = 0
            
            try:
                # Aktives Setting
                active_setting = getattr(char, 'active_setting_name', 'Unbekannt')
                counts['active_setting'] = active_setting
                Logger.debug(f"Aktives Setting: {active_setting}")
            except Exception as e:
                Logger.warning(f"Fehler beim Abrufen des aktiven Settings: {str(e)}")
                counts['active_setting'] = 'Unbekannt'
            
            Logger.info(f"Element-Counts erfolgreich ermittelt: {counts}")
            return counts
            
        except Exception as e:
            Logger.error(f"Kritischer Fehler beim Abrufen der Element-Statistiken: {str(e)}", exc_info=True)
            return {}
    
    def update_element_statistics_ui(self):
        """Aktualisiert die Element-Statistiken in der UI"""
        try:
            if not hasattr(self.widget.ids, 'element_stats_box'):
                Logger.debug(f"element_stats_box nicht in {self.widget.__class__.__name__} gefunden - überspringe UI-Update")
                return
            
            stats_box = self.widget.ids.element_stats_box
            stats_box.clear_widgets()
            
            element_counts = self.get_element_counts()
            
            if not element_counts:
                # Wenn keine Daten verfügbar sind, zeige Platzhalter
                placeholder_label = MDLabel(
                    text="Keine Charakterdaten verfügbar",
                    size_hint_y=None,
                    height=dp(30),
                    font_size="12sp",
                    italic=True
                )
                stats_box.add_widget(placeholder_label)
                return
            
            if element_counts and any(element_counts.values()):
                # Kompakte Statistik-Anzeige
                setting_name = element_counts.get('active_setting', 'Unbekannt')
                h_selected = element_counts.get('handicaps_selected', 0)
                h_total = element_counts.get('handicaps_total', 0)
                t_selected = element_counts.get('talente_selected', 0)
                t_total = element_counts.get('talente_total', 0)
                m_selected = element_counts.get('maechte_selected', 0)
                m_total = element_counts.get('maechte_total', 0)
                f_total = element_counts.get('fertigkeiten_total', 0)  # Fertigkeiten hinzugefügt
                
                # Erste Zeile: Setting
                stats_text = f"Setting: {setting_name}"
                stats_label = MDLabel(
                    text=stats_text,
                    size_hint_y=None,
                    height=dp(25),
                    font_size="12sp",
                    bold=True
                )
                stats_box.add_widget(stats_label)
                
                # Zweite Zeile: Kompakte Element-Counts mit Fertigkeiten
                elements_text = f"H: {h_selected}/{h_total} | T: {t_selected}/{t_total} | M: {m_selected}/{m_total} | F: {f_total}"
                elements_label = MDLabel(
                    text=elements_text,
                    size_hint_y=None,
                    height=dp(25),
                    font_size="11sp"
                )
                stats_box.add_widget(elements_label)
                
                Logger.debug(f"Element-Statistiken UI aktualisiert: {stats_text}, {elements_text}")
            else:
                # Keine gültigen Daten
                no_data_label = MDLabel(
                    text="Daten werden geladen...",
                    size_hint_y=None,
                    height=dp(25),
                    font_size="11sp",
                    italic=True
                )
                stats_box.add_widget(no_data_label)
                
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Element-Statistiken UI: {str(e)}", exc_info=True)
            
            # Fehler-Label hinzufügen
            try:
                if hasattr(self.widget.ids, 'element_stats_box'):
                    stats_box = self.widget.ids.element_stats_box
                    stats_box.clear_widgets()
                    error_label = MDLabel(
                        text="Fehler beim Laden der Statistiken",
                        size_hint_y=None,
                        height=dp(25),
                        font_size="11sp",
                        theme_text_color="Error"
                    )
                    stats_box.add_widget(error_label)
            except Exception as e2:
                Logger.error(f"Kritischer Fehler beim Anzeigen der Fehler-UI: {str(e2)}")
    
    def _show_fallback_error(self, message):
        """Fallback-Fehlermeldung wenn Dialog-Service nicht verfügbar ist"""
        try:
            from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton, MDButtonText
            
            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                padding=dp(20),
                size_hint_y=None,
                height=dp(100)
            )
            
            content.add_widget(MDLabel(
                text=message,
                size_hint_y=None,
                height=dp(60),
                halign="center"
            ))
            
            error_dialog = MDDialog(
                MDDialogHeadlineText(text="Fehler"),
                MDDialogContentContainer(content),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="OK"),
                        style="text",
                        on_release=lambda x: error_dialog.dismiss()
                    )
                ),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            
            error_dialog.open()
            
        except Exception as e:
            Logger.error(f"Kritischer Fehler: Kann keine Dialoge anzeigen: {str(e)}")