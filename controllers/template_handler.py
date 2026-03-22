# controllers/template_handler.py
"""
Template-Management Handler für EinstellungenWidget
ORIGINAL Implementation aus einstellungen_widget_backup.py - 1:1 repliziert
"""

import os
import json
from pathlib import Path
from utils.path_utils import get_templates_path
from kivy.logger import Logger
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from services.service_container import service_container
from services.event_service import EventTypes


class TemplateHandler:
    """Handler für Template-Management Funktionalitäten - ORIGINAL aus backup 1:1"""
    
    def __init__(self, widget):
        self.widget = widget
        self.app = widget.app
        
        # Template-Variablen initialisieren (ORIGINAL)
        self.available_templates = []
        self.filtered_templates = []
        self.selected_template = None
        self.template_dialog = None
        
        # Templates nach kurzer Verzögerung laden
        Clock.schedule_once(self._load_available_templates, 0.2)
        
    def open_template_selection_dialog(self):
        """Öffnet FileManager zur Auswahl von Templates für Auto Character Generator"""
        try:
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManagerService nicht verfügbar")
                self._show_error_dialog("FileManagerService nicht verfügbar")
                return
            templates_dir = file_service.get_default_directory('templates')
            file_service.template_callback = self._on_template_file_selected
            file_service.show_file_manager(templates_dir, "load_template")
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen der Template-Auswahl: {e}")

    def _on_template_file_selected(self, path):
        """Callback wenn eine Template-Datei im FileManager ausgewählt wurde"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            template_file = Path(path)
            character_name = template_data.get('character_name',
                           template_data.get('name', template_file.stem))
            template_info = {
                'file': template_file,
                'name': character_name,
                'description': template_data.get('description', 'Keine Beschreibung verfügbar')
            }
            self._generate_character_from_template(template_info)
        except json.JSONDecodeError as e:
            Logger.error(f"Ungültige JSON-Datei: {path} - {e}")
            self._show_error_dialog(f"Die Datei ist keine gültige JSON-Datei:\n{os.path.basename(path)}")
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Templates: {e}")
            self._show_error_dialog(f"Fehler beim Laden des Templates: {str(e)}")
    
    def show_template_selection_dialog(self):
        """Zeigt Template-Auswahl Dialog mit Suchfeld (nach Vorbild von voelker_view) - ORIGINAL"""
        if not self.available_templates:
            # Keine Templates verfügbar
            dialog = MDDialog(
                MDLabel(text="Keine Templates verfügbar!\n\nLegen Sie Templates im 'templates/' Ordner ab."),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                auto_dismiss=False,
            )
            dialog.open()
            return

        self._show_template_search_dialog(
            self.available_templates,
            lambda template: self._on_template_selected_from_dialog(template)
        )
    
    def _show_template_search_dialog(self, templates, callback):
        """Template-Auswahl Dialog mit Suchfeld (nach Vorbild von voelker_view._show_search_dialog) - ORIGINAL"""
        from kivymd.uix.dialog import (
            MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, 
            MDDialogContentContainer
        )
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp
        
        try:
            # Hauptcontainer für den Dialog - Feste Höhe
            dialog_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
                height=dp(450)  # Etwas größer für Template-Beschreibungen
            )
            
            # Suchfeld
            search_field = MDTextField(
                mode="outlined",
                size_hint_y=None,
                height=dp(56)
            )
            search_hint = MDTextFieldHintText(text="Template suchen...")
            search_field.add_widget(search_hint)
            
            # Scrollbare Liste
            scroll_view = MDScrollView(
                size_hint_y=None,
                height=dp(350)
            )
            
            templates_list = MDList(
                size_hint_y=None
            )
            # Höhe der Liste berechnen basierend auf Items
            templates_list.bind(minimum_height=templates_list.setter('height'))
            
            # Templates zur Liste hinzufügen
            def update_list(filtered_templates):
                templates_list.clear_widgets()
                for template in sorted(filtered_templates, key=lambda x: x['name']):
                    list_item = MDListItem(
                        MDListItemHeadlineText(text=template['name']),
                        MDListItemSupportingText(text=template['description']),
                        size_hint_y=None,
                        height=dp(72),  # Größer für Beschreibung
                        on_release=lambda x, selected_template=template: self._on_template_dialog_item_selected(callback, selected_template)
                    )
                    templates_list.add_widget(list_item)
            
            # Initial alle Templates anzeigen
            update_list(templates)
            
            # Suchfunktion
            def on_search_text(instance, text):
                if not text:
                    filtered = templates
                else:
                    search_text = text.lower()
                    filtered = [
                        template for template in templates
                        if search_text in template['name'].lower() or 
                           search_text in template['description'].lower()
                    ]
                update_list(filtered)
            
            search_field.bind(text=on_search_text)
            
            # Widgets hinzufügen
            dialog_content.add_widget(search_field)
            scroll_view.add_widget(templates_list)
            dialog_content.add_widget(scroll_view)
            
            # Dialog erstellen
            self.template_dialog = MDDialog(
                MDDialogHeadlineText(text="Template auswählen"),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="Abbrechen"),
                        style="text",
                        on_release=self._dismiss_template_dialog
                    ),
                ),
                auto_dismiss=False,
            )
            
            self.template_dialog.open()
            
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Template-Dialogs: {e}", exc_info=True)
    
    def _on_template_dialog_item_selected(self, callback, template):
        """Callback wenn Template im Dialog ausgewählt wird - ORIGINAL"""
        try:
            self._dismiss_template_dialog()
            if callback:
                callback(template)
        except Exception as e:
            Logger.error(f"Fehler bei Template-Auswahl: {e}")
    
    def _dismiss_template_dialog(self, *args):
        """Schließt den Template-Dialog - ORIGINAL"""
        if hasattr(self, 'template_dialog') and self.template_dialog:
            self.template_dialog.dismiss()
            self.template_dialog = None
    
    def _on_template_selected_from_dialog(self, template):
        """Callback wenn Template aus Dialog ausgewählt wurde - ORIGINAL"""
        try:
            self.selected_template = template
            
            # Button-Text aktualisieren
            if hasattr(self.widget.ids, 'selected_template_text'):
                self.widget.ids.selected_template_text.text = template['name']
            
            # Button-Text auf "Charakter generieren" ändern
            if hasattr(self.widget.ids, 'generate_button_text'):
                self.widget.ids.generate_button_text.text = "Charakter generieren"
            
            Logger.info(f"Template ausgewählt: {template['name']}")
            
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten der Template-Auswahl: {e}")
    
    def generate_character_from_selected_template(self):
        """Generiert Charakter aus dem ausgewählten Template - ORIGINAL"""
        if not self.selected_template:
            dialog = MDDialog(
                MDLabel(text="Bitte wählen Sie zuerst ein Template aus!"),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                auto_dismiss=False,
            )
            dialog.open()
            return
        
        # Verwende die bestehende Generierungslogik
        self._generate_character_from_template(self.selected_template, None)
    
    def _generate_character_from_template(self, template_info, dialog=None):
        """Generiert Charakter aus gewähltem Template - ORIGINAL"""
        try:
            from functions.auto_character_generator import generate_character_from_json
            
            # Dialog nur schließen wenn vorhanden
            if dialog:
                dialog.dismiss()
            
            Logger.info(f"Generiere Charakter aus Template: {template_info['name']}")
            
            # Character Generator ausführen
            output_path = generate_character_from_json(str(template_info['file']))
            
            if output_path and os.path.exists(output_path):
                Logger.info(f"Charakter erfolgreich generiert: {output_path}")
                
                # Generierten Charakter in das Tool laden über CharakterController
                if hasattr(self.app, 'controller') and self.app.controller:
                    # Sicherstellen, dass output_path ein String ist
                    output_path_str = str(output_path) if output_path else ""
                    erfolg = self.app.controller.lade_charakter_von_json(output_path_str)
                    if erfolg:
                        Logger.info("Generierter Charakter erfolgreich geladen")
                        
                        # UI aktualisieren
                        if hasattr(self.app, 'refresh_ui'):
                            self.app.refresh_ui()
                        
                        # Event senden
                        event_service = service_container.get_event_service()
                        if event_service:
                            event_service.publish(EventTypes.CHARACTER_LOADED, {'file': output_path})
                        
                        # Success Dialog
                        success_dialog = MDDialog(
                            MDLabel(text=f"Charakter '{template_info['name']}' wurde erfolgreich generiert und geladen!"),
                            MDButton(
                                MDButtonText(text="OK"),
                                style="text", 
                                on_release=lambda x: success_dialog.dismiss()
                            ),
                            auto_dismiss=False,
                        )
                        success_dialog.open()
                    else:
                        Logger.error("Fehler beim Laden des generierten Charakters")
                        self._show_error_dialog("Fehler beim Laden des generierten Charakters")
                else:
                    Logger.error("Charakter-Controller nicht verfügbar")
                    self._show_error_dialog("Charakter-Controller nicht verfügbar")
            else:
                Logger.error("Charaktergenerierung fehlgeschlagen")
                self._show_error_dialog("Charaktergenerierung fehlgeschlagen")
                
        except Exception as e:
            Logger.error(f"Fehler bei der Charaktergenerierung: {e}")
            self._show_error_dialog(f"Fehler bei der Charaktergenerierung: {str(e)}")
    
    def _show_error_dialog(self, message):
        """Zeigt einen Fehler-Dialog - ORIGINAL"""
        try:
            error_dialog = MDDialog(
                MDLabel(text=f"Fehler:\n{message}"),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: error_dialog.dismiss()
                ),
                auto_dismiss=False,
            )
            error_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des Fehler-Dialogs: {e}")
    
    # ==================== TEMPLATE FUNCTIONALITY ====================
    def _load_available_templates(self, dt):
        """Lädt verfügbare Templates aus dem templates/ Ordner - ORIGINAL"""
        try:
            templates_dir = Path(get_templates_path())
            self.available_templates = []
            
            if templates_dir.exists():
                for template_file in templates_dir.glob('*.json'):
                    # Überspringe schema und example dateien
                    if not any(skip in template_file.name.lower() for skip in ['schema', 'example']):
                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                template_data = json.load(f)
                                # Unterstütze sowohl 'character_name' als auch 'name' Felder
                                character_name = template_data.get('character_name',
                                               template_data.get('name', template_file.stem))
                                self.available_templates.append({
                                    'file': template_file,
                                    'name': character_name,
                                    'description': template_data.get('description', 'Keine Beschreibung verfügbar')
                                })
                        except Exception as e:
                            Logger.warning(f"Template {template_file} konnte nicht geladen werden: {e}")
                            continue
            
            # Alphabetisch sortieren
            self.available_templates.sort(key=lambda x: x['name'])
            self.filtered_templates = self.available_templates.copy()
            
            Logger.info(f"{len(self.available_templates)} Templates geladen")
            
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Templates: {e}")
    
    def _load_templates(self):
        """Lädt Templates neu (für Template-Wizard Integration)"""
        try:
            self._load_available_templates(None)
            Logger.info("Templates erfolgreich neu geladen")
        except Exception as e:
            Logger.error(f"Fehler beim Neuladen der Templates: {e}")
    
    
