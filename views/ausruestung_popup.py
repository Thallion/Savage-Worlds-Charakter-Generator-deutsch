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
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.ausruestung import Ausruestung

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'ausruestung_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'ausruestung_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"ausruestung_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class AusruestungDialogContent(MDBoxLayout):
    def __init__(self, ausruestung_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Ausrüstungs-Daten übergeben wurden, befülle die Felder
        if ausruestung_data:
            self.edit_mode = True
            self.original_name = ausruestung_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(ausruestung_data), 0.1)
    
    def _fill_fields(self, ausruestung_data):
        """Befüllt die Felder mit den Ausrüstungs-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = ausruestung_data.get('name', '')
        
        if hasattr(self.ids, 'kategorie_input'):
            self.ids.kategorie_input.text = ausruestung_data.get('kategorie', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(ausruestung_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(ausruestung_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = ausruestung_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = ausruestung_data.get('beschreibung', '')

class DeleteAusruestungDialogContent(MDBoxLayout):
    def __init__(self, ausruestung_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.ausruestung_callback = ausruestung_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.ausruestung_callback:
            return
            
        ausruestung = self.ausruestung_callback()
        if not ausruestung:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in ausruestung
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'ausruestung_dropdown'):
            self.ids.ausruestung_dropdown.text = text_item

class AusruestungDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_ausruestung = None
        self.dialog_content = None

    def _get_overlay(self):
        """Gibt eine gecachte ElementOverlay-Instanz zurück"""
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen einer neuen Ausrüstung"""
        dialog_content = AusruestungDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Ausrüstung hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_ausruestung,
        )

    def show_edit_dialog(self, ausruestung_name):
        """Zeigt das Overlay zum Bearbeiten einer bestehenden Ausrüstung"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            ausruestung = charakter.ausruestung.get(ausruestung_name)
            if not ausruestung:
                self.show_error(f"Ausrüstung '{ausruestung_name}' nicht gefunden.")
                return

            ausruestung_data = {
                'name': ausruestung.name,
                'kategorie': getattr(ausruestung, 'kategorie', 'Allgemein'),
                'gewicht': ausruestung.gewicht,
                'kosten': ausruestung.kosten,
                'setting': ausruestung.setting,
                'beschreibung': ausruestung.beschreibung
            }

            dialog_content = AusruestungDialogContent(ausruestung_data=ausruestung_data)
            self.dialog_content = dialog_content
            self.selected_ausruestung = ausruestung_name

            overlay = self._get_overlay()
            overlay.open(
                title="Ausrüstung bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_ausruestung,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_ausruestung(self, *args):
        """Aktualisiert eine bestehende Ausrüstung"""
        if not self.dialog_content or not self.selected_ausruestung:
            Logger.error("Dialog-Content oder ausgewählte Ausrüstung nicht gefunden")
            return

        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Ausrüstung darf nicht leer sein.")
            return

        if not kategorie:
            self.show_error("Bitte geben Sie eine Kategorie an.")
            return

        try:
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            # Hole die bestehende Ausrüstung
            ausruestung = charakter.ausruestung.get(self.selected_ausruestung)
            if not ausruestung:
                self.show_error(f"Ausrüstung '{self.selected_ausruestung}' nicht mehr gefunden.")
                return

            # Wenn der Name geändert wurde und bereits existiert
            if name != ausruestung.name and name in charakter.ausruestung:
                self.show_error(f"Ausrüstung mit dem Namen '{name}' existiert bereits.")
                return

            # Aktualisiere die Ausrüstung
            old_name = ausruestung.name
            ausruestung.name = name
            ausruestung.kategorie = kategorie
            ausruestung.gewicht = gewicht
            ausruestung.kosten = kosten
            ausruestung.setting = setting
            ausruestung.beschreibung = beschreibung

            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                charakter.ausruestung[name] = ausruestung
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Ausrüstung '{name}' wurde aktualisiert.")

        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Ausrüstung: {e}")
            self.show_error("Fehler beim Aktualisieren der Ausrüstung")

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Ausrüstung."""
        import time
        from kivy.metrics import dp

        ausruestung = self.get_all_ausruestung()
        if not ausruestung:
            self.show_error("Keine Ausrüstung zum Löschen verfügbar.")
            return

        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        self._ausruestung_checkboxes = {}
        self._ausruestung_last_cb_times = {}

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
                if key in self._ausruestung_last_cb_times and (now - self._ausruestung_last_cb_times[key]) < 0.5:
                    return
                self._ausruestung_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._ausruestung_checkboxes[item_name] = checkbox

        for ausruestung_name in sorted(ausruestung):
            create_checkbox(ausruestung_name)

        scroll_height = min(len(ausruestung) * dp(48), dp(250))
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
            for ausruestung_name in sorted(ausruestung):
                if search_text and search_text.lower() not in ausruestung_name.lower():
                    continue
                if ausruestung_name in self._ausruestung_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=ausruestung_name))
                    cb_existing = self._ausruestung_checkboxes[ausruestung_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(ausruestung_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Ausrüstung löschen"),
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
        for name, cb in self._ausruestung_checkboxes.items():
            if cb.active:
                selected.append(name)

        if not selected:
            self.show_error("Bitte wähle mindestens eine Ausrüstung zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Ausrüstung",
            on_confirm=self._confirm_delete_ausruestung
        )

    def _confirm_delete_ausruestung(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for ausruestung_name in selected:
                success = charakter.remove_ausruestung(ausruestung_name)
                if success:
                    Logger.info(f"Ausrüstung '{ausruestung_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Ausrüstung '{ausruestung_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Ausrüstung(en) gelöscht")

            Logger.info(f"{len(selected)} Ausrüstung(en) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Ausrüstungen: {e}")
            self.show_error("Fehler beim Löschen der Ausrüstungen")

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
            Clock.schedule_once(lambda dt: _dismiss_confirm_popup(), 0)
            Clock.schedule_once(_dismiss_confirm_popup, 0.2)

        def _on_confirm_release(x):
            # dismiss() darf nicht synchron im on_release-Handler aufgerufen
            # werden – auf Android blockiert das laufende Touch-Event die
            # Dismiss-Animation. Daher erst im nächsten Frame schließen und
            # on_confirm() mit ausreichend Abstand danach ausführen.
            Clock.schedule_once(lambda dt: _dismiss_confirm_popup(), 0)
            Clock.schedule_once(_dismiss_confirm_popup, 0.2)
            Clock.schedule_once(lambda dt: on_confirm(), 0.35)

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

    def save_ausruestung(self, *args):
        """Speichert eine neue Ausrüstung"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Ausrüstung darf nicht leer sein.")
            return

        if not kategorie:
            self.show_error("Bitte geben Sie eine Kategorie an.")
            return

        try:
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.ausruestung:
                self.show_error(f"Ausrüstung '{name}' existiert bereits.")
                return

            new_ausruestung = Ausruestung(
                name=name,
                kategorie=kategorie,
                gewicht=gewicht,
                kosten=kosten,
                setting=setting,
                beschreibung=beschreibung,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                custom=True
            )

            success = charakter.add_ausruestung(new_ausruestung)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()

                self.dismiss_dialog()
                Logger.info(f"Ausrüstung '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Ausrüstung '{name}' konnte nicht hinzugefügt werden.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Ausrüstung: {e}")
            self.show_error("Fehler beim Speichern der Ausrüstung")

    def delete_ausruestung(self, *args):
        """Löscht die ausgewählten Ausrüstungen"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Ausrüstung zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            for ausruestung_name in selected:
                success = charakter.remove_ausruestung(ausruestung_name)
                if success:
                    Logger.info(f"Ausrüstung '{ausruestung_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Ausrüstung '{ausruestung_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Ausrüstung(en) gelöscht")

            Logger.info(f"{len(selected)} Ausrüstung(en) wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Ausrüstungen: {e}")
            self.show_error("Fehler beim Löschen der Ausrüstungen")

    def on_ausruestung_select(self, ausruestung_name):
        """Callback wenn eine Ausrüstung ausgewählt wurde"""
        self.selected_ausruestung = ausruestung_name

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_ausruestung = None

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
        Logger.error(f"Ausrüstung-Fehler: {message}")

    def get_all_ausruestung(self):
        """Gibt eine Liste aller verfügbaren Ausrüstung zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.ausruestung.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Ausrüstung: {e}")
        return []

    def _refresh_ausruestung_view(self):
        """Aktualisiert das Ausrüstung-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
        except Exception as e:
            Logger.warning(f"Ausrüstung-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass