# schild-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.schild import Schild

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
import os
import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'schild_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'schild_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"schild_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

# SchildDialogContent
class SchildDialogContent(MDBoxLayout):
    def __init__(self, schild_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Schild-Daten übergeben wurden, befülle die Felder
        if schild_data:
            self.edit_mode = True
            self.original_name = schild_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(schild_data), 0.1)
    
    def _fill_fields(self, schild_data):
        """Befüllt die Felder mit den Schild-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = schild_data.get('name', '')
        
        if hasattr(self.ids, 'parade_input'):
            self.ids.parade_input.text = str(schild_data.get('parade', 0))
        
        if hasattr(self.ids, 'deckung_input'):
            self.ids.deckung_input.text = str(schild_data.get('deckung', 0))
        
        if hasattr(self.ids, 'mindeststaerke_input'):
            self.ids.mindeststaerke_input.text = schild_data.get('mindeststaerke', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(schild_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(schild_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = schild_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = schild_data.get('beschreibung', '')

class DeleteSchildDialogContent(MDBoxLayout):
    def __init__(self, schilde_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.schilde_callback = schilde_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.schilde_callback:
            return
            
        schilde = self.schilde_callback()
        if not schilde:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in schilde
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'schild_dropdown'):
            self.ids.schild_dropdown.text = text_item

class SchildDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_schild = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen eines neuen Schildes"""
        dialog_content = SchildDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neues Schild hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_schild,
        )

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Schilden."""
        import time
        from kivy.metrics import dp

        schilde = self.get_all_schilde()
        if not schilde:
            self.show_error("Keine Schilde zum Löschen verfügbar.")
            return

        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        self._schild_checkboxes = {}
        self._schild_last_cb_times = {}

        content = MDList(size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        def create_checkbox(item_name):
            item = MDListItem(size_hint_y=None, height=dp(48))
            item.add_widget(MDListItemSupportingText(text=item_name))

            checkbox = MDListItemTrailingCheckbox()
            cb = checkbox

            def on_release_checkbox(inst, cb=cb, name=item_name):
                now = time.monotonic()
                key = f"cb_{name}"
                if key in self._schild_last_cb_times and (now - self._schild_last_cb_times[key]) < 0.5:
                    return
                self._schild_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._schild_checkboxes[item_name] = checkbox

        for schild_name in sorted(schilde):
            create_checkbox(schild_name)

        scroll_height = min(len(schilde) * dp(48), dp(250))
        scroll = MDScrollView(
            size_hint=(1, None),
            height=scroll_height,
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(15),
            bar_margin=dp(4),
        )
        scroll.add_widget(content)

        main_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(16),
            height=scroll_height + dp(80),
        )

        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            hint_text="Suchen...",
        )
        search_field.add_widget(MDTextFieldHintText(text="Suchen..."))
        main_content.add_widget(search_field)
        main_content.add_widget(scroll)

        def populate_list(search_text):
            content.clear_widgets()
            for schild_name in sorted(schilde):
                if search_text and search_text.lower() not in schild_name.lower():
                    continue
                if schild_name in self._schild_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=schild_name))
                    cb_existing = self._schild_checkboxes[schild_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(schild_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Schild löschen"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text",
                         on_release=lambda x: self._delete_popup.dismiss()),
                MDButton(MDButtonText(text="Weiter"), style="filled",
                         on_release=self._on_delete_action_clicked),
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._delete_popup.open()

    def _on_delete_action_clicked(self, *args):
        """Phase 1: Sammelt ausgewählte Items und zeigt Bestätigungs-Popup."""
        selected = []
        for name, cb in self._schild_checkboxes.items():
            if cb.active:
                selected.append(name)

        if not selected:
            self.show_error("Bitte wähle mindestens ein Schild zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Schild",
            on_confirm=self._confirm_delete_schild
        )

    def _confirm_delete_schild(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for schild_name in selected:
                success = charakter.remove_ausruestung(schild_name)
                if success:
                    Logger.info(f"Schild '{schild_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Schild '{schild_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Schild(er) gelöscht")

            Logger.info(f"{len(selected)} Schild(er) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Schilde: {e}")
            self.show_error("Fehler beim Löschen der Schilde")

    def _show_delete_confirmation_popup(self, selected_items, item_type, on_confirm):
        """Zeigt separates Bestätigungs-Popup OHNE Checkboxen (Two-Phase Pattern)."""
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp
        from kivy.clock import Clock

        content = MDList(size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        for item_name in selected_items:
            list_item = MDListItem(size_hint_y=None, height=dp(48))
            list_item.add_widget(MDListItemSupportingText(text=item_name))
            content.add_widget(list_item)

        scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(15))
        scroll.add_widget(content)

        list_height = min(dp(48) * len(selected_items), dp(200))
        content.size_hint_y = None
        content.height = list_height

        main_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(80) + list_height,
            padding=dp(16)
        )
        main_content.add_widget(scroll)

        def _dismiss_confirm_popup(*_):
            """Schließt das Bestätigungs-Popup robust (doppelter Versuch)."""
            popup = getattr(self, '_delete_confirm_popup', None)
            if popup is None:
                return
            try:
                popup.dismiss()
            except Exception as e:
                Logger.warning(f"Fehler beim Schließen des Lösch-Dialogs: {e}")

        def _on_cancel(x):
            _dismiss_confirm_popup()
            Clock.schedule_once(_dismiss_confirm_popup, 0.15)

        def _on_confirm_release(x):
            # Dialog zuerst schließen, dann die eigentliche Aktion verzögert
            # ausführen. Auf Android kann das synchrone Aufrufen von
            # on_confirm() (mit UI-Refresh) die Dismiss-Animation unterbrechen
            # und den Dialog in einem inkonsistenten Zustand hinterlassen.
            _dismiss_confirm_popup()
            Clock.schedule_once(_dismiss_confirm_popup, 0.15)
            Clock.schedule_once(lambda dt: on_confirm(), 0.2)

        self._delete_confirm_popup = MDDialog(
            MDDialogHeadlineText(text=f"{item_type} löschen?"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=_on_cancel,
                ),
                MDButton(
                    MDButtonText(text="Löschen"),
                    style="filled",
                    on_release=_on_confirm_release,
                ),
            ),
            size_hint=(0.85, None),
        )
        self._delete_confirm_popup.open()

    def show_edit_dialog(self, schild_name):
        """Zeigt das Overlay zum Bearbeiten eines bestehenden Schildes"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            schild = charakter.ausruestung.get(schild_name)
            if not schild:
                self.show_error(f"Schild '{schild_name}' nicht gefunden.")
                return

            schild_data = {
                'name': schild.name,
                'parade': schild.parade,
                'deckung': schild.deckung,
                'mindeststaerke': schild.mindeststaerke,
                'gewicht': schild.gewicht,
                'kosten': schild.kosten,
                'setting': schild.setting,
                'beschreibung': schild.beschreibung
            }

            dialog_content = SchildDialogContent(schild_data=schild_data)
            self.dialog_content = dialog_content
            self.selected_schild = schild_name

            overlay = self._get_overlay()
            overlay.open(
                title="Schild bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_schild,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_schild(self, *args):
        """Aktualisiert ein bestehendes Schild"""
        if not self.dialog_content or not self.selected_schild:
            Logger.error("Dialog-Content oder ausgewähltes Schild nicht gefunden")
            return
            
        name = self.dialog_content.ids.name_input.text.strip()
        
        if not name:
            self.show_error("Der Name des Schildes darf nicht leer sein.")
            return

        # Validierung der Eingaben
        parade_text = self.dialog_content.ids.parade_input.text.strip()
        deckung_text = self.dialog_content.ids.deckung_input.text.strip()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierung der Eingaben
        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return
            
        try:
            parade = int(parade_text)
            deckung = int(deckung_text)
            gewicht = float(gewicht_text)
            kosten = float(kosten_text)
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Parade, Deckung, Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Hole das bestehende Schild
            schild = charakter.ausruestung.get(self.selected_schild)
            if not schild:
                self.show_error(f"Schild '{self.selected_schild}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != schild.name and name in charakter.ausruestung:
                self.show_error(f"Schild mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere das Schild
            old_name = schild.name
            schild.name = name
            schild.parade = parade
            schild.deckung = deckung
            schild.mindeststaerke = mindeststaerke
            schild.gewicht = gewicht
            schild.kosten = kosten
            schild.setting = setting
            schild.beschreibung = beschreibung
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                charakter.ausruestung[name] = schild
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Schild '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Schilds: {e}")
            self.show_error("Fehler beim Aktualisieren des Schilds")

    def save_schild(self, *args):
        """Speichert ein neues Schild"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        name = self.dialog_content.ids.name_input.text.strip()
        
        if not name:
            self.show_error("Der Name des Schildes darf nicht leer sein.")
            return

        # Validierung der Eingaben
        parade_text = self.dialog_content.ids.parade_input.text.strip()
        deckung_text = self.dialog_content.ids.deckung_input.text.strip()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierung der Eingaben
        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return
            
        try:
            parade = int(parade_text)
            deckung = int(deckung_text)
            gewicht = float(gewicht_text)
            kosten = float(kosten_text)
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Parade, Deckung, Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Prüfen ob das Schild bereits existiert
            if name in charakter.ausruestung:
                self.show_error(f"Schild '{name}' existiert bereits.")
                return

            new_schild = Schild(
                name=name,
                gewicht=gewicht,
                kosten=kosten,
                setting=setting,
                parade=parade,
                deckung=deckung,
                mindeststaerke=mindeststaerke,
                beschreibung=beschreibung,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                kategorie='Schild',
                custom=True
            )
            
            success = charakter.add_ausruestung(new_schild)
            
            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                self.dismiss_dialog()
                Logger.info(f"Schild '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Schild '{name}' konnte nicht hinzugefügt werden.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Schilds: {e}")
            self.show_error("Fehler beim Speichern des Schilds")



    def on_schild_select(self, schild_name):
        """Callback wenn ein Schild ausgewählt wurde"""
        self.selected_schild = schild_name

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_schild = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception:
            pass
        Logger.error(f"Schild-Fehler: {message}")

    def get_all_schilde(self):
        """Gibt eine Liste aller verfügbaren Schilde zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() if isinstance(item, Schild)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Schilde: {e}")
        return []

    def _refresh_ausruestung_view(self):
        """Aktualisiert das Ausrüstung-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.debug(f"Ausrüstung-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass