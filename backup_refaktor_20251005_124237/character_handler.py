# controllers/character_handler.py
"""
Character-Management Handler für EinstellungenWidget
Ausgegliedert für bessere Code-Organisation
"""

from kivy.logger import Logger
from pathlib import Path
import os
from functions.character_advancement import increase_aufstiege, decrease_aufstiege
from services.service_container import service_container


class CharacterHandler:
    """
    UI-Adapter für Character-Management im EinstellungenWidget.
    Stellt Widget-spezifische Operationen bereit und delegiert an CharakterController.
    """
    
    def __init__(self, widget):
        self.widget = widget
        self.app = widget.app
        # Direkte Controller-Referenz für bessere Performance
        self.controller = self.app.controller if hasattr(self.app, 'controller') else None
        
    def get_charakter_value(self, attribute, default_value=''):
        """Hilfsmethode zum sicheren Abrufen von Charakter-Attributen"""
        try:
            if self.controller and self.controller.charakter:
                return str(getattr(self.controller.charakter, attribute, default_value))
            return default_value
        except Exception as e:
            Logger.warning(f"Fehler beim Abrufen von {attribute}: {e}")
            return default_value

    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen"""
        try:
            if not self.controller:
                Logger.warning("Controller nicht verfügbar für Attributsteigerungen-Update")
                return
                
            field_value = self.widget.ids.attributsteigerungen_field.text
            try:
                new_value = int(field_value)
                self.controller.charakter.maximale_attributsteigerungen = new_value
                Logger.info(f"Maximale Attributsteigerungen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Attributsteigerungen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Attributsteigerungen: {e}")

    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen"""
        try:
            if not self.controller:
                Logger.warning("Controller nicht verfügbar für Fertigkeitssteigerungen-Update")
                return
                
            field_value = self.widget.ids.fertigkeitssteigerungen_field.text
            try:
                new_value = int(field_value)
                self.controller.charakter.maximale_fertigkeitssteigerungen = new_value
                Logger.info(f"Maximale Fertigkeitssteigerungen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Fertigkeitssteigerungen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Fertigkeitssteigerungen: {e}")

    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        try:
            if not self.controller:
                Logger.warning("Controller nicht verfügbar für Vermögen-Update")
                return
                
            field_value = self.widget.ids.vermoegen_field.text
            try:
                new_value = int(field_value)
                self.controller.charakter.vermoegen = new_value
                Logger.info(f"Vermögen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Vermögen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Vermögens: {e}")

    def update_waehrung(self):
        """Aktualisiert die Währungseinheit"""
        try:
            if not self.controller:
                Logger.warning("Controller nicht verfügbar für Währung-Update")
                return
                
            new_value = self.widget.ids.waehrung_field.text
            self.controller.charakter.waehrungseinheit = new_value
            Logger.info(f"Währungseinheit aktualisiert auf: {new_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Währung: {e}")

    def erhoehe_startkapital(self):
        """Erhöht das Startkapital mit Handicap-Punkten"""
        try:
            if not self.controller:
                Logger.warning("Controller nicht verfügbar für Startkapital-Erhöhung")
                return
                
            self.controller.erhoehe_startkapital_mit_handicap()
            self._update_ui_fields()
            Logger.info("Startkapital mit Handicap-Punkten erhöht")
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Startkapitals: {e}")

    def erhoehe_aufstieg(self):
        """Erhöht die Aufstiege"""
        try:
            if not (self.controller and self.controller.charakter):
                Logger.warning("Controller oder Charakter nicht verfügbar für Aufstieg-Erhöhung")
                return
                
            # Verwende die character_advancement Funktion direkt
            increase_aufstiege(self.controller.charakter)
            self._update_ui_fields()
            Logger.info("Aufstieg erhöht")
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Aufstiegs: {e}")

    def senke_aufstieg(self):
        """Senkt die Aufstiege"""
        try:
            if not (self.controller and self.controller.charakter):
                Logger.warning("Controller oder Charakter nicht verfügbar für Aufstieg-Senkung")
                return
                
            # Verwende die character_advancement Funktion direkt
            decrease_aufstiege(self.controller.charakter)
            self._update_ui_fields()
            Logger.info("Aufstieg gesenkt")
        except Exception as e:
            Logger.error(f"Fehler beim Senken des Aufstiegs: {e}")

    def create_new_character(self):
        """Erstellt einen neuen Charakter"""
        try:
            if not self.controller:
                Logger.warning("Controller nicht verfügbar für neuen Charakter")
                return
                
            self.controller.neuer_charakter()
            self._update_ui_fields()
            Logger.info("Neuer Charakter erstellt")
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen eines neuen Charakters: {e}")

    def schnellspeichern_charakter(self):
        """Schnellspeicherung mit UI-Feedback"""
        try:
            if not (self.controller and self.controller.charakter):
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog("Kein Charakter verfügbar zum Speichern.")
                return
            
            # Prüfen ob der Charakter bereits einen Dateipfad hat
            if (hasattr(self.controller, 'current_character_file_path') and 
                self.controller.current_character_file_path and
                os.path.exists(self.controller.current_character_file_path)):
                
                # Direkt in die aktuelle Datei speichern
                file_path = self.controller.current_character_file_path
                success = self.controller.speichere_charakter_als_json(file_path)
                
                dialog_service = service_container.get_dialog_service()
                if success and dialog_service:
                    dialog_service.show_success_dialog(
                        f"Charakter wurde schnell gespeichert:\n{os.path.basename(file_path)}",
                        "Schnellspeichern erfolgreich"
                    )
                    Logger.info(f"Charakter schnell gespeichert: {file_path}")
                elif dialog_service:
                    dialog_service.show_error_dialog("Fehler beim Schnellspeichern des Charakters.")
            else:
                # Keine aktuelle Datei - normalen Speichern-Dialog verwenden
                Logger.info("Keine aktuelle Datei gefunden, verwende normalen Speichern-Dialog")
                self.speichere_charakter()
                
        except Exception as e:
            Logger.error(f"Fehler beim Schnellspeichern: {str(e)}", exc_info=True)
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(f"Fehler beim Schnellspeichern: {str(e)}")

    def speichere_charakter(self):
        """Speichern-Dialog mit FileManager-Integration"""
        try:
            if not (self.controller and self.controller.charakter):
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog("Kein Charakter verfügbar zum Speichern.")
                return
            
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManager-Service nicht verfügbar")
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog("FileManager-Service nicht verfügbar.")
                return
            
            # Prüfen ob bereits eine Datei für diesen Charakter existiert
            existing_file_info = self._check_existing_character_file()
            
            if existing_file_info['exists']:
                # Bestehende Datei gefunden - Überschreiben/Neu-Dialog anzeigen
                self._show_save_options_dialog(existing_file_info)
            else:
                # Keine bestehende Datei - direkt Dateiname-Dialog anzeigen
                self._show_save_filename_dialog()
            
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren des Speichervorgangs: {str(e)}", exc_info=True)
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(f"Fehler beim Speichern: {str(e)}")

    def lade_charakter(self):
        """Laden-Dialog: Original-Implementation from backup"""
        try:
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManager-Service nicht verfügbar")
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog("FileManager-Service nicht verfügbar.")
                return
            
            # Bestehende temp Settings löschen (falls vorhanden)
            self._clear_temp_settings()
            
            # FileManager öffnen
            default_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(default_dir, "load")
            
            Logger.info("Charakter-Laden-Dialog geöffnet")
            
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Laden-Dialogs: {str(e)}", exc_info=True)
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(f"Fehler beim Laden: {str(e)}")

    def erzeuge_charakterbogen_pdf(self):
        """Delegiert an PDFManager oder zeigt Überschreiben/Neu-Dialog - ORIGINAL aus backup"""
        # Check for manager availability
        MANAGERS_AVAILABLE = hasattr(self.widget, 'pdf_manager') and self.widget.pdf_manager is not None
        
        if MANAGERS_AVAILABLE:
            self.widget.pdf_manager.create_character_pdf()
        else:
            # Vereinfachte PDF-Erstellung mit Überschreiben/Neu-Dialog
            try:
                if not (hasattr(self.app, 'controller') and self.app.controller and self.app.controller.charakter):
                    dialog_service = service_container.get_dialog_service()
                    if dialog_service:
                        dialog_service.show_error_dialog("Kein Charakter verfügbar für PDF-Erstellung.")
                    return
                
                # Prüfen ob bereits eine PDF für diesen Charakter existiert
                existing_pdf_info = self._check_existing_pdf_file()
                
                if existing_pdf_info['exists']:
                    # Bestehende PDF gefunden - Überschreiben/Neu-Dialog anzeigen
                    self._show_pdf_save_options_dialog(existing_pdf_info)
                else:
                    # Keine bestehende PDF - direkt Dateiname-Dialog anzeigen
                    self._show_pdf_filename_dialog()
                    
            except Exception as e:
                Logger.error(f"Fehler bei PDF-Erstellung: {str(e)}", exc_info=True)

    def zeige_statblock(self):
        """Delegiert an StatisticsManager - ORIGINAL aus backup"""
        MANAGERS_AVAILABLE = hasattr(self.widget, 'statistics_manager') and self.widget.statistics_manager is not None
        
        if MANAGERS_AVAILABLE:
            self.widget.statistics_manager.show_statblock()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_statblock_dialog()
            else:
                Logger.info("Statblock anzeigen - Manager und Service nicht verfügbar")

    def zeige_element_statistiken(self):
        """Zeigt Element-Statistiken an"""
        try:
            # Prüfe ob statistics_manager verfügbar ist
            MANAGERS_AVAILABLE = hasattr(self.widget, 'statistics_manager') and self.widget.statistics_manager is not None
            
            if MANAGERS_AVAILABLE:
                self.widget.statistics_manager.show_element_statistics()
                Logger.info("Element-Statistiken angezeigt")
            else:
                Logger.warning("Statistics Manager nicht verfügbar")
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen der Element-Statistiken: {e}")

    def on_character_created(self, data):
        """Event-Handler für Character-Creation"""
        try:
            Logger.info(f"Charakter erstellt: {data}")
            self._update_ui_fields()
        except Exception as e:
            Logger.error(f"Fehler bei Character-Created-Event: {e}")

    def on_character_loaded(self, data):
        """Event-Handler für Character-Loading"""
        try:
            Logger.info(f"Charakter geladen: {data}")
            self._update_ui_fields()
            
            # Prüfe ob statistics_manager verfügbar ist
            MANAGERS_AVAILABLE = hasattr(self.widget, 'statistics_manager') and self.widget.statistics_manager is not None
            
            if MANAGERS_AVAILABLE:
                self.widget.statistics_manager.update_element_statistics_ui()
        except Exception as e:
            Logger.error(f"Fehler bei Character-Loaded-Event: {e}")

    def _update_ui_fields(self):
        """Aktualisiert die UI-Felder mit aktuellen Charakter-Werten"""
        try:
            # Update nur wenn IDs verfügbar sind
            if hasattr(self.widget, 'ids'):
                if hasattr(self.widget.ids, 'attributsteigerungen_field'):
                    self.widget.ids.attributsteigerungen_field.text = self.get_charakter_value('maximale_attributsteigerungen', '5')
                
                if hasattr(self.widget.ids, 'fertigkeitssteigerungen_field'):
                    self.widget.ids.fertigkeitssteigerungen_field.text = self.get_charakter_value('maximale_fertigkeitssteigerungen', '12')
                
                if hasattr(self.widget.ids, 'vermoegen_field'):
                    self.widget.ids.vermoegen_field.text = self.get_charakter_value('vermoegen', '500')
                
                if hasattr(self.widget.ids, 'waehrung_field'):
                    self.widget.ids.waehrung_field.text = self.get_charakter_value('waehrungseinheit', 'Gold')
                
                Logger.debug("UI-Felder aktualisiert")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der UI-Felder: {e}")
    
    # ==================== HELPER METHODS FROM BACKUP ====================
    
    def _check_existing_character_file(self):
        """Prüft ob bereits eine Charakterdatei existiert"""
        try:
            controller = self.app.controller
            # Erst prüfen ob der Charakter bereits einen Dateipfad hat
            if (hasattr(controller, 'current_character_file_path') and 
                controller.current_character_file_path and
                os.path.exists(controller.current_character_file_path)):
                
                file_path = controller.current_character_file_path
                return {
                    'exists': True,
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'directory': os.path.dirname(file_path)
                }
            
            # Andernfalls prüfen ob eine Datei mit dem Charakternamen existiert
            file_service = service_container.get_file_manager_service()
            if file_service:
                chars_dir = file_service.get_default_directory('chars')
                char_name = getattr(controller.charakter, 'char_name', '')
                
                if char_name:
                    # Sichere Dateiname-Varianten prüfen
                    safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    
                    potential_filename = f"{safe_name}.json"
                    potential_path = os.path.join(chars_dir, potential_filename)
                    
                    if os.path.exists(potential_path):
                        return {
                            'exists': True,
                            'path': potential_path,
                            'name': potential_filename,
                            'directory': chars_dir
                        }
            
            return {'exists': False, 'path': '', 'name': '', 'directory': ''}
            
        except Exception as e:
            Logger.error(f"Fehler beim Prüfen der existierenden Datei: {str(e)}")
            return {'exists': False, 'path': '', 'name': '', 'directory': ''}
    
    def _show_save_options_dialog(self, existing_file_info):
        """Zeigt Dialog mit Optionen zum Überschreiben oder Neu-Speichern - ORIGINAL aus backup"""
        try:
            dialog_service = service_container.get_dialog_service()
            if not dialog_service:
                Logger.error("Dialog-Service nicht verfügbar")
                return
            
            message = f"Bestehende Datei gefunden: {existing_file_info['name']}"
            choices = [
                ("Bestehende Datei überschreiben", "overwrite"),
                ("Als neue Datei speichern...", "save_new")
            ]
            
            def handle_save_choice(choice):
                if choice == "overwrite":
                    self._save_to_existing_file(existing_file_info)
                elif choice == "save_new":
                    self._show_save_filename_dialog()
            
            dialog_service.show_choice_dialog(
                message=message,
                title="Charakter speichern",
                choices=choices,
                on_choice=handle_save_choice
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des Speicheroptionen-Dialogs: {str(e)}")
    
    def _show_save_filename_dialog(self):
        """Zeigt Dialog zur Eingabe eines Dateinamens"""
        try:
            dialog_service = service_container.get_dialog_service()
            if not dialog_service:
                Logger.error("Dialog-Service nicht verfügbar")
                return
            
            # Vorgeschlagenen Dateinamen generieren
            suggested_name = self._generate_suggested_filename()
            
            dialog_service.show_input_dialog(
                "Dateiname eingeben:",
                "Charakter speichern",
                suggested_name,
                self._on_filename_entered
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des Dateiname-Dialogs: {str(e)}")
    
    def _generate_suggested_filename(self):
        """Generiert einen vorgeschlagenen Dateinamen"""
        try:
            controller = self.app.controller
            if controller and controller.charakter:
                char_name = getattr(controller.charakter, 'char_name', '')
                if char_name:
                    # Sichere Dateiname-Erstellung
                    safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    return f"{safe_name}.json"
            
            # Fallback: Zeitstempel-basierter Name
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Charakter_{timestamp}.json"
            
        except Exception as e:
            Logger.error(f"Fehler beim Generieren des Dateinamens: {str(e)}")
            return "Charakter.json"
    
    def _save_to_existing_file(self, existing_file_info):
        """Speichert in die existierende Datei"""
        try:
            controller = self.app.controller
            success = controller.speichere_charakter_als_json(existing_file_info['path'])
            
            dialog_service = service_container.get_dialog_service()
            if success and dialog_service:
                dialog_service.show_success_dialog(
                    f"Charakter wurde gespeichert:\n{existing_file_info['name']}",
                    "Speichern erfolgreich"
                )
                Logger.info(f"Charakter in existierende Datei gespeichert: {existing_file_info['path']}")
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Speichern des Charakters.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Speichern in existierende Datei: {str(e)}")
    
    def _on_filename_entered(self, filename):
        """Callback wenn Dateiname eingegeben wurde"""
        try:
            if not filename or not filename.strip():
                return
            
            # .json Extension hinzufügen falls nicht vorhanden
            if not filename.lower().endswith('.json'):
                filename = f"{filename}.json"
            
            # Vollständigen Pfad erstellen
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManager-Service nicht verfügbar")
                return
            
            chars_dir = file_service.get_default_directory('chars')
            full_path = os.path.join(chars_dir, filename)
            
            # Speichern
            controller = self.app.controller
            success = controller.speichere_charakter_als_json(full_path)
            
            dialog_service = service_container.get_dialog_service()
            if success and dialog_service:
                dialog_service.show_success_dialog(
                    f"Charakter wurde gespeichert:\n{filename}",
                    "Speichern erfolgreich"
                )
                Logger.info(f"Charakter unter neuem Namen gespeichert: {full_path}")
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Speichern des Charakters.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Speichern unter neuem Dateinamen: {str(e)}")
    
    def _clear_temp_settings(self):
        """Löscht temporäre Einstellungen"""
        try:
            # Implementierung falls nötig - hier nur Platzhalter
            Logger.debug("Temporäre Einstellungen geleert")
        except Exception as e:
            Logger.error(f"Fehler beim Löschen temporärer Einstellungen: {str(e)}")
    
    # ==================== PDF METHODS FROM BACKUP ====================
    
    def _check_existing_pdf_file(self):
        """Prüft ob bereits eine PDF für den Charakter existiert - ORIGINAL aus backup"""
        try:
            controller = self.app.controller
            
            # Erst prüfen ob der Charakter bereits einen PDF-Pfad hat
            if (hasattr(controller, 'current_pdf_file_path') and 
                controller.current_pdf_file_path and
                os.path.exists(controller.current_pdf_file_path)):
                
                file_path = controller.current_pdf_file_path
                return {
                    'exists': True,
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'directory': os.path.dirname(file_path)
                }
            
            # Andernfalls prüfen ob eine PDF mit dem Charakternamen existiert
            file_service = service_container.get_file_manager_service()
            if file_service:
                pdfs_dir = file_service.get_default_directory('pdfs')
                char_name = getattr(controller.charakter, 'char_name', '')
                
                if char_name:
                    # Sichere Dateiname-Varianten prüfen
                    safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    
                    potential_filename = f"{safe_name}.pdf"
                    potential_path = os.path.join(pdfs_dir, potential_filename)
                    
                    if os.path.exists(potential_path):
                        return {
                            'exists': True,
                            'path': potential_path,
                            'name': potential_filename,
                            'directory': pdfs_dir
                        }
            
            return {'exists': False, 'path': '', 'name': '', 'directory': ''}
            
        except Exception as e:
            Logger.error(f"Fehler beim Prüfen der existierenden PDF: {str(e)}")
            return {'exists': False, 'path': '', 'name': '', 'directory': ''}
    
    def _show_pdf_save_options_dialog(self, existing_pdf_info):
        """Zeigt Dialog mit Optionen zum Überschreiben oder Neu-PDF-Erstellen - ORIGINAL aus backup"""
        try:
            dialog_service = service_container.get_dialog_service()
            if not dialog_service:
                Logger.error("Dialog-Service nicht verfügbar")
                return
            
            message = f"Bestehende PDF gefunden: {existing_pdf_info['name']}"
            choices = [
                ("Bestehende PDF überschreiben", "overwrite"),
                ("Als neue PDF erstellen...", "save_new")
            ]
            
            def handle_pdf_save_choice(choice):
                if choice == "overwrite":
                    self._create_pdf_to_existing_file(existing_pdf_info)
                elif choice == "save_new":
                    self._show_pdf_filename_dialog()
            
            dialog_service.show_choice_dialog(
                message=message,
                title="PDF erstellen",
                choices=choices,
                on_choice=handle_pdf_save_choice
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des PDF-Speicheroptionen-Dialogs: {str(e)}")
    
    def _show_pdf_filename_dialog(self):
        """Zeigt Dialog zur Eingabe eines PDF-Dateinamens - ORIGINAL aus backup"""
        try:
            dialog_service = service_container.get_dialog_service()
            if not dialog_service:
                Logger.error("Dialog-Service nicht verfügbar")
                return
            
            # Vorgeschlagenen PDF-Dateinamen generieren
            suggested_name = self._generate_suggested_pdf_filename()
            
            dialog_service.show_input_dialog(
                "PDF-Dateiname eingeben:",
                "PDF erstellen",
                suggested_name,
                self._on_pdf_filename_entered
            )
            
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des PDF-Dateiname-Dialogs: {str(e)}")
    
    def _generate_suggested_pdf_filename(self):
        """Generiert einen vorgeschlagenen PDF-Dateinamen - ORIGINAL aus backup"""
        try:
            controller = self.app.controller
            if controller and controller.charakter:
                char_name = getattr(controller.charakter, 'char_name', '')
                if char_name:
                    # Sichere Dateiname-Erstellung
                    safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    return f"{safe_name}.pdf"
            
            # Fallback: Zeitstempel-basierter Name
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Charakter_{timestamp}.pdf"
            
        except Exception as e:
            Logger.error(f"Fehler beim Generieren des PDF-Dateinamens: {str(e)}")
            return "Charakter.pdf"
    
    def _create_pdf_to_existing_file(self, existing_pdf_info):
        """Erstellt PDF in die existierende Datei - ORIGINAL aus backup"""
        try:
            # Verwende PDF Manager falls verfügbar
            pdf_service = service_container.get_pdf_service()
            if pdf_service:
                success = pdf_service.create_character_pdf(
                    existing_pdf_info['path'],
                    printer_friendly=False
                )
            else:
                # Fallback: Direkte PDF-Erstellung
                success = self._create_pdf_directly(existing_pdf_info['path'])
            
            dialog_service = service_container.get_dialog_service()
            if success and dialog_service:
                dialog_service.show_success_dialog(
                    f"Charakterbogen-PDF wurde erstellt:\n{existing_pdf_info['name']}",
                    "PDF erfolgreich erstellt"
                )
                Logger.info(f"PDF in existierende Datei erstellt: {existing_pdf_info['path']}")
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Erstellen der PDF.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der PDF in existierende Datei: {str(e)}")
    
    def _on_pdf_filename_entered(self, filename):
        """Callback wenn PDF-Dateiname eingegeben wurde - ORIGINAL aus backup"""
        try:
            if not filename or not filename.strip():
                return
            
            # .pdf Extension hinzufügen falls nicht vorhanden
            if not filename.lower().endswith('.pdf'):
                filename = f"{filename}.pdf"
            
            # Vollständigen Pfad erstellen
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManager-Service nicht verfügbar")
                return
            
            pdfs_dir = file_service.get_default_directory('pdfs')
            full_path = os.path.join(pdfs_dir, filename)
            
            # PDF erstellen
            pdf_service = service_container.get_pdf_service()
            if pdf_manager:
                success = pdf_manager.create_character_sheet_pdf(
                    self.app.controller.charakter,
                    full_path
                )
            else:
                # Fallback: Direkte PDF-Erstellung
                success = self._create_pdf_directly(full_path)
            
            dialog_service = service_container.get_dialog_service()
            if success and dialog_service:
                dialog_service.show_success_dialog(
                    f"Charakterbogen-PDF wurde erstellt:\n{filename}",
                    "PDF erfolgreich erstellt"
                )
                Logger.info(f"PDF unter neuem Namen erstellt: {full_path}")
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Erstellen der PDF.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der PDF unter neuem Dateinamen: {str(e)}")
    
    def _create_pdf_directly(self, file_path):
        """Direkte PDF-Erstellung als Fallback - ORIGINAL aus backup"""
        try:
            # Dies ist eine vereinfachte Fallback-Implementation
            # In der realen Anwendung würde hier die PDF-Generierungs-Logik stehen
            Logger.info(f"Direkte PDF-Erstellung zu: {file_path}")
            
            # TODO: Implementiere direkte PDF-Erstellung
            # Für jetzt nur Platzhalter mit Fehler-Rückgabe
            Logger.warning("Direkte PDF-Erstellung nicht implementiert - benötigt PDF Manager Service")
            return False
            
        except Exception as e:
            Logger.error(f"Fehler bei direkter PDF-Erstellung: {str(e)}")
            return False