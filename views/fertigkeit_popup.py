# fertigkeit-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.fertigkeit import Fertigkeit

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'fertigkeit_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'fertigkeit_popup.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"fertigkeit_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class FertigkeitDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_attribut = None

    def open_attribut_menu(self, instance_item):
        app = App.get_running_app()
        charakter = app.controller.charakter
        attribute = list(charakter.get_attribute_dict().keys())

        menu_items = [
            {
                "text": attribut,
                "on_release": lambda x=attribut: self.select_attribut(x),
            }
            for attribut in attribute
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_attribut(self, attribut):
        self.selected_attribut = attribut
        if hasattr(self.ids, 'selected_attribut_text'):
            self.ids.selected_attribut_text.text = attribut

class DeleteFertigkeitDialogContent(MDBoxLayout):
    def __init__(self, fertigkeiten_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.fertigkeiten_callback = fertigkeiten_callback
        self.menu_callback = menu_callback
        self.dialog = None

    def open_menu(self, instance_item):
        if not self.fertigkeiten_callback:
            return

        fertigkeiten = self.fertigkeiten_callback()
        if not fertigkeiten:
            return

        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in fertigkeiten
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'fertigkeit_dropdown'):
            self.ids.fertigkeit_dropdown.text = text_item

class FertigkeitDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_fertigkeit = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Fertigkeit"""
        dialog_content = FertigkeitDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Fertigkeit hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_fertigkeit,
        )

    def show_delete_dialog(self):
        """Zeigt das Overlay zum Löschen von Fertigkeiten (suchbare Liste mit Mehrfachauswahl)"""
        fertigkeiten = self.get_all_fertigkeiten()
        if not fertigkeiten:
            self.show_error("Keine Fertigkeiten zum Löschen verfügbar.")
            return

        from views.element_overlay import ElementListContent
        content = ElementListContent(
            items=fertigkeiten,
            multi_select=True,
        )
        self.dialog_content = content

        overlay = self._get_overlay()
        overlay.open(
            title="Fertigkeit löschen",
            content_widget=content,
            action_text="Löschen",
            on_action=self._on_delete_action_clicked,
        )

    def save_fertigkeit(self, *args):
        """Speichert eine neue Fertigkeit"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name der Fertigkeit darf nicht leer sein.")
            return

        # Validiere Attribut
        if not hasattr(self.dialog_content, 'selected_attribut') or not self.dialog_content.selected_attribut:
            self.show_error("Bitte wähle ein Attribut aus.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.fertigkeiten:
                self.show_error(f"Fertigkeit '{name}' existiert bereits.")
                return

            # Attributobjekt abrufen
            attribut = charakter.get_attribute_dict().get(self.dialog_content.selected_attribut)
            if attribut is None:
                self.show_error(f"Attribut '{self.dialog_content.selected_attribut}' nicht gefunden.")
                return

            grundfertigkeit = self.dialog_content.ids.grundfertigkeit_checkbox.active

            new_fertigkeit = Fertigkeit(
                fertigkeit_name=name,
                attribut=attribut,
                grundfertigkeit=grundfertigkeit,
                custom=True
            )

            # Füge die Fertigkeit hinzu
            charakter.add_fertigkeit(new_fertigkeit)

            # Speichere die Custom Fertigkeiten
            charakter.save_custom_fertigkeiten()

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Fertigkeit '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Fertigkeit: {e}")
            self.show_error("Fehler beim Speichern der Fertigkeit")

    def delete_fertigkeit(self, *args):
        """Löscht die ausgewählten Fertigkeiten"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Fertigkeit zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            for fertigkeit_name in selected:
                charakter.remove_fertigkeit(fertigkeit_name)
                Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde gelöscht.")

            charakter.save_custom_fertigkeiten()

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_fertigkeit_view()
            self._show_success_snackbar(f"{len(selected)} Fertigkeit(en) gelöscht")

            Logger.info(f"{len(selected)} Fertigkeit(en) wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Fertigkeiten: {e}")
            self.show_error("Fehler beim Löschen der Fertigkeiten")

    def _on_delete_action_clicked(self):
        """Phase 1: Zeigt Bestätigungs-Popup vor dem Löschen (Two-Phase Pattern)"""
        if not self.dialog_content:
            return

        selected = self.dialog_content.get_selected_items()
        if not selected:
            self.show_error("Bitte wähle mindestens eine Fertigkeit zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Fertigkeit",
            on_confirm=self._confirm_delete_fertigkeit
        )

    def _confirm_delete_fertigkeit(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for fertigkeit_name in selected:
                charakter.remove_fertigkeit(fertigkeit_name)
                Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde gelöscht.")

            charakter.save_custom_fertigkeiten()

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_fertigkeit_view()
            self._show_success_snackbar(f"{len(selected)} Fertigkeit(en) gelöscht")

            Logger.info(f"{len(selected)} Fertigkeit(en) wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Fertigkeiten: {e}")
            self.show_error("Fehler beim Löschen der Fertigkeiten")

    def _show_delete_confirmation_popup(self, selected_items, item_type, on_confirm):
        """Zeigt separates Bestätigungs-Popup OHNE Checkboxen (Two-Phase Pattern)."""
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp

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

        self._delete_confirm_popup = MDDialog(
            MDDialogHeadlineText(text=f"{item_type} löschen?"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._delete_confirm_popup.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Löschen"),
                    style="filled",
                    on_release=lambda x: (
                        self._delete_confirm_popup.dismiss(),
                        on_confirm()
                    )
                ),
            ),
            size_hint=(0.85, None),
        )
        self._delete_confirm_popup.open()

    def on_fertigkeit_select(self, fertigkeit_name):
        """Callback wenn eine Fertigkeit im Dropdown ausgewählt wurde"""
        self.selected_fertigkeit = fertigkeit_name
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_fertigkeit_text')):
            self.dialog_content.ids.selected_fertigkeit_text.text = fertigkeit_name
            Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_fertigkeit = None

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
        Logger.error(f"Fertigkeit-Fehler: {message}")

    def get_all_fertigkeiten(self):
        """Gibt eine Liste aller verfügbaren Fertigkeiten zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.fertigkeiten.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Fertigkeiten: {e}")
        return []

    def _refresh_fertigkeit_view(self):
        """Aktualisiert das Eigenschaften-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Eigenschaften', 'eigenschaften_widget')
                if widget and hasattr(widget, 'update_eigenschaften'):
                    widget.update_eigenschaften()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.debug(f"Eigenschaften-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass
