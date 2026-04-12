# macht-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.macht import Macht

import os
import sys
import time

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'macht_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'macht_popup.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"macht_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class MachtDialogContent(MDBoxLayout):
    def __init__(self, macht_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None

        # Wenn Macht-Daten übergeben wurden, befülle die Felder
        if macht_data:
            self.edit_mode = True
            self.original_name = macht_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(macht_data), 0.1)

    def _fill_fields(self, macht_data):
        """Befüllt die Felder mit den Macht-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = macht_data.get('name', '')

        if hasattr(self.ids, 'rang_input'):
            self.ids.rang_input.text = macht_data.get('rang', '')

        if hasattr(self.ids, 'machtpunkte_input'):
            self.ids.machtpunkte_input.text = str(macht_data.get('machtpunkte', 0))

        if hasattr(self.ids, 'reichweite_input'):
            self.ids.reichweite_input.text = macht_data.get('reichweite', '')

        if hasattr(self.ids, 'dauer_input'):
            self.ids.dauer_input.text = macht_data.get('dauer', '')

        if hasattr(self.ids, 'effekt_input'):
            self.ids.effekt_input.text = macht_data.get('effekt', '')

        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = macht_data.get('beschreibung', '')

        if hasattr(self.ids, 'voraussetzungen_input'):
            voraussetzungen = macht_data.get('voraussetzungen', [])
            if isinstance(voraussetzungen, list):
                self.ids.voraussetzungen_input.text = ', '.join(voraussetzungen)
            else:
                self.ids.voraussetzungen_input.text = str(voraussetzungen)

class DeleteMachtDialogContent(MDBoxLayout):
    def __init__(self, maechte_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.maechte_callback = maechte_callback
        self.menu_callback = menu_callback
        self.dialog = None

    def open_menu(self, instance_item):
        if not self.maechte_callback:
            return

        maechte = self.maechte_callback()
        if not maechte:
            return

        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in maechte
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'macht_dropdown'):
            self.ids.macht_dropdown.text = text_item

class MachtDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_macht = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Macht"""
        dialog_content = MachtDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Macht hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_macht,
        )

    def show_edit_dialog(self, macht_name_key):
        """Zeigt den Dialog zum Bearbeiten einer bestehenden Macht"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            # Hole die Macht
            macht = charakter.maechte.get(macht_name_key)
            if not macht:
                self.show_error(f"Macht '{macht_name_key}' nicht gefunden.")
                return

            # Erstelle Dialog-Content mit Macht-Daten
            macht_data = {
                'name': macht.name,
                'rang': macht.rang,
                'machtpunkte': macht.machtpunkte,
                'reichweite': macht.reichweite,
                'dauer': macht.dauer,
                'effekt': macht.effekt,
                'beschreibung': macht.beschreibung,
                'voraussetzungen': macht.voraussetzungen
            }

            dialog_content = MachtDialogContent(macht_data=macht_data)
            self.dialog_content = dialog_content
            self.selected_macht = macht_name_key  # Speichere den Key für Updates

            overlay = self._get_overlay()
            overlay.open(
                title="Macht bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_macht,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_macht(self, *args):
        """Aktualisiert eine bestehende Macht"""
        if not self.dialog_content or not self.selected_macht:
            Logger.error("Dialog-Content oder ausgewählte Macht nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name der Macht darf nicht leer sein.")
            return

        # Sammle alle Eingabedaten
        rang = self.dialog_content.ids.rang_input.text.strip()
        machtpunkte_text = self.dialog_content.ids.machtpunkte_input.text.strip()
        reichweite = self.dialog_content.ids.reichweite_input.text.strip()
        dauer = self.dialog_content.ids.dauer_input.text.strip()
        effekt = self.dialog_content.ids.effekt_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        voraussetzungen = [v.strip() for v in self.dialog_content.ids.voraussetzungen_input.text.split(',') if v.strip()]

        if not machtpunkte_text.isdigit():
            self.show_error("Machtpunkte müssen eine gültige Zahl sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            # Hole die bestehende Macht
            macht = charakter.maechte.get(self.selected_macht)
            if not macht:
                self.show_error(f"Macht '{self.selected_macht}' nicht mehr gefunden.")
                return

            # Wenn der Name geändert wurde und bereits existiert
            if name != macht.name and name in charakter.maechte:
                self.show_error(f"Eine Macht mit dem Namen '{name}' existiert bereits.")
                return

            # Aktualisiere die Macht
            old_name = macht.name
            macht.name = name
            macht.rang = rang
            macht.machtpunkte = int(machtpunkte_text)
            macht.reichweite = reichweite
            macht.dauer = dauer
            macht.effekt = effekt
            macht.beschreibung = beschreibung
            macht.voraussetzungen = voraussetzungen

            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                new_key = name
                old_key = self.selected_macht

                # Macht unter neuem Key speichern und alten löschen
                charakter.maechte[new_key] = macht
                if old_key != new_key and old_key in charakter.maechte:
                    del charakter.maechte[old_key]

                    # Auch in selected_maechte aktualisieren
                    if old_key in charakter.selected_maechte:
                        idx = charakter.selected_maechte.index(old_key)
                        charakter.selected_maechte[idx] = new_key

            # Speichere die Custom Mächte
            charakter.save_custom_maechte()

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Macht '{name}' wurde aktualisiert.")

        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Macht: {e}")
            self.show_error("Fehler beim Aktualisieren der Macht")

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Mächten."""
        from kivy.core.window import Window
        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        maechte = self.get_all_maechte()
        if not maechte:
            self.show_error("Keine Mächte zum Löschen verfügbar.")
            return

        self._macht_checkboxes = {}
        self._macht_last_cb_times = {}

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
                if key in self._macht_last_cb_times and (now - self._macht_last_cb_times[key]) < 0.5:
                    return
                self._macht_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._macht_checkboxes[item_name] = checkbox

        for macht_name in sorted(maechte):
            create_checkbox(macht_name)

        scroll_height = min(len(maechte) * dp(48), dp(250))
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
            orientation="vertical", spacing=dp(8), size_hint_y=None,
            padding=dp(16), height=scroll_height + dp(80),
        )

        search_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(56), hint_text="Suchen...")
        search_field.add_widget(MDTextFieldHintText(text="Suchen..."))
        main_content.add_widget(search_field)
        main_content.add_widget(scroll)

        def populate_list(search_text):
            content.clear_widgets()
            for macht_name in sorted(maechte):
                if search_text and search_text.lower() not in macht_name.lower():
                    continue
                if macht_name in self._macht_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=macht_name))
                    cb_existing = self._macht_checkboxes[macht_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(macht_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Macht löschen"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text",
                         on_release=lambda x: self._delete_popup.dismiss()),
                MDButton(MDButtonText(text="Weiter"), style="filled",
                         on_release=self._on_delete_action_clicked),
            ),
            size_hint=(0.85, None), auto_dismiss=False,
        )
        self._delete_popup.open()

    def _on_delete_action_clicked(self, *args):
        """Phase 1: Sammelt ausgewählte Items und zeigt Bestätigungs-Popup."""
        selected = [name for name, cb in self._macht_checkboxes.items() if cb.active]

        if not selected:
            self.show_error("Bitte wähle mindestens eine Macht zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected, item_type="Macht", on_confirm=self._confirm_delete_macht
        )

    def save_macht(self, *args):
        """Speichert eine neue Macht"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name der Macht darf nicht leer sein.")
            return

        # Sammle alle Eingabedaten
        rang = self.dialog_content.ids.rang_input.text.strip()
        machtpunkte_text = self.dialog_content.ids.machtpunkte_input.text.strip()
        reichweite = self.dialog_content.ids.reichweite_input.text.strip()
        dauer = self.dialog_content.ids.dauer_input.text.strip()
        effekt = self.dialog_content.ids.effekt_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        voraussetzungen = [v.strip() for v in self.dialog_content.ids.voraussetzungen_input.text.split(',') if v.strip()]

        if not machtpunkte_text.isdigit():
            self.show_error("Machtpunkte müssen eine gültige Zahl sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.maechte:
                self.show_error(f"Macht '{name}' existiert bereits.")
                return

            new_macht = Macht(
                name=name,
                rang=rang,
                machtpunkte=int(machtpunkte_text),
                reichweite=reichweite,
                dauer=dauer,
                effekt=effekt,
                beschreibung=beschreibung,
                voraussetzungen=voraussetzungen,
                custom=True
            )

            success = charakter.add_macht(new_macht)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()

                self.dismiss_dialog()
                Logger.info(f"Macht '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Macht '{name}' konnte nicht hinzugefügt werden.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Macht: {e}")
            self.show_error("Fehler beim Speichern der Macht")

    def delete_macht(self, *args):
        """Löscht die ausgewählten Mächte"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Macht zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            for macht_name in selected:
                success = charakter.remove_macht(macht_name)
                if success:
                    Logger.info(f"Macht '{macht_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Macht '{macht_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_macht_view()
            self._show_success_snackbar(f"{len(selected)} Macht/Mächte gelöscht")

            Logger.info(f"{len(selected)} Macht/Mächte wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Mächte: {e}")
            self.show_error("Fehler beim Löschen der Mächte")

    def _on_delete_action_clicked(self, *args):
        """Phase 1: Zeigt Bestätigungs-Popup vor dem Löschen (Two-Phase Pattern)"""
        if not self.dialog_content:
            return

        selected = self.dialog_content.get_selected_items()
        if not selected:
            self.show_error("Bitte wähle mindestens eine Macht zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Macht",
            on_confirm=self._confirm_delete_macht
        )

    def _confirm_delete_macht(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for macht_name in selected:
                success = charakter.remove_macht(macht_name)
                if success:
                    Logger.info(f"Macht '{macht_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Macht '{macht_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_macht_view()
            self._show_success_snackbar(f"{len(selected)} Macht/Mächte gelöscht")

            Logger.info(f"{len(selected)} Macht/Mächte wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Mächte: {e}")
            self.show_error("Fehler beim Löschen der Mächte")

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

    def on_macht_select(self, macht_name):
        """Callback wenn eine Macht im Dropdown ausgewählt wurde"""
        self.selected_macht = macht_name
        # Dialog-Content aktualisieren wenn vorhanden
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_macht_text')):
            self.dialog_content.ids.selected_macht_text.text = macht_name
            Logger.info(f"Macht '{macht_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_macht = None

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
        Logger.error(f"Macht-Fehler: {message}")

    def get_all_maechte(self):
        """Gibt eine Liste aller verfügbaren Mächte zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.maechte.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Mächte: {e}")
        return []

    def _refresh_macht_view(self):
        """Aktualisiert das Macht-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
        except Exception as e:
            Logger.debug(f"Macht-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass
