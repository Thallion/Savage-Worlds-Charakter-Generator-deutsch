# talent-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.talent import Talent

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'talent_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'talent_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"talent_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class TalentDialogContent(MDBoxLayout):
    def __init__(self, talent_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Talent-Daten übergeben wurden, befülle die Felder
        if talent_data:
            self.edit_mode = True
            self.original_name = talent_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(talent_data), 0.1)
    
    def _fill_fields(self, talent_data):
        """Befüllt die Felder mit den Talent-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = talent_data.get('name', '')
        
        if hasattr(self.ids, 'kategorie_input'):
            self.ids.kategorie_input.text = talent_data.get('kategorie', '')
        
        if hasattr(self.ids, 'rang_input'):
            self.ids.rang_input.text = talent_data.get('rang', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = talent_data.get('beschreibung', '')
        
        if hasattr(self.ids, 'voraussetzungen_input'):
            voraussetzungen = talent_data.get('voraussetzungen', [])
            if isinstance(voraussetzungen, list):
                self.ids.voraussetzungen_input.text = ', '.join(voraussetzungen)
            else:
                self.ids.voraussetzungen_input.text = str(voraussetzungen)
        
        if hasattr(self.ids, 'neue_maechte_input'):
            self.ids.neue_maechte_input.text = str(talent_data.get('neue_maechte', 0))
        
        if hasattr(self.ids, 'machtpunkte_input'):
            self.ids.machtpunkte_input.text = str(talent_data.get('machtpunkte', 0))
        
class DeleteTalentDialogContent(MDBoxLayout):
    def __init__(self, talente_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.talente_callback = talente_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.talente_callback:
            return
            
        talente = self.talente_callback()
        if not talente:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in talente
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'talent_dropdown'):
            self.ids.talent_dropdown.text = text_item

class TalentDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_talent = None
        self.dialog_content = None

    def _get_overlay(self):
        """Gibt eine gecachte ElementOverlay-Instanz zurück"""
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen eines neuen Talents"""
        dialog_content = TalentDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neues Talent hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_talent,
        )

    def show_edit_dialog(self, talent_name_key):
        """Zeigt das Overlay zum Bearbeiten eines bestehenden Talents"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            talent = charakter.talente.get(talent_name_key)
            if not talent:
                self.show_error(f"Talent '{talent_name_key}' nicht gefunden.")
                return

            talent_data = {
                'name': talent.name,
                'kategorie': talent.kategorie,
                'rang': talent.rang,
                'beschreibung': talent.beschreibung,
                'voraussetzungen': talent.voraussetzungen,
                'neue_maechte': talent.neue_maechte,
                'machtpunkte': talent.machtpunkte
            }

            dialog_content = TalentDialogContent(talent_data=talent_data)
            self.dialog_content = dialog_content
            self.selected_talent = talent_name_key

            overlay = self._get_overlay()
            overlay.open(
                title="Talent bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_talent,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_talent(self, *args):
        """Aktualisiert ein bestehendes Talent"""
        if not self.dialog_content or not self.selected_talent:
            Logger.error("Dialog-Content oder ausgewähltes Talent nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name des Talents darf nicht leer sein.")
            return

        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        rang = self.dialog_content.ids.rang_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        voraussetzungen = [v.strip() for v in self.dialog_content.ids.voraussetzungen_input.text.split(',') if v.strip()]
        neue_maechte_text = self.dialog_content.ids.neue_maechte_input.text.strip()
        machtpunkte_text = self.dialog_content.ids.machtpunkte_input.text.strip()

        if neue_maechte_text and not neue_maechte_text.isdigit():
            self.show_error("Neue Mächte muss eine gültige Zahl sein.")
            return

        if machtpunkte_text and not machtpunkte_text.isdigit():
            self.show_error("Machtpunkte müssen eine gültige Zahl sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            talent = charakter.talente.get(self.selected_talent)
            if not talent:
                self.show_error(f"Talent '{self.selected_talent}' nicht mehr gefunden.")
                return

            if name != talent.name and name in charakter.talente:
                self.show_error(f"Ein Talent mit dem Namen '{name}' existiert bereits.")
                return

            old_name = talent.name
            talent.name = name
            talent.kategorie = kategorie
            talent.rang = rang
            talent.beschreibung = beschreibung
            talent.voraussetzungen = voraussetzungen
            talent.neue_maechte = int(neue_maechte_text) if neue_maechte_text else 0
            talent.machtpunkte = int(machtpunkte_text) if machtpunkte_text else 0

            if name != old_name:
                new_key = name
                old_key = self.selected_talent

                charakter.talente[new_key] = talent
                if old_key != new_key and old_key in charakter.talente:
                    del charakter.talente[old_key]

                    if old_key in charakter.selected_talente:
                        idx = charakter.selected_talente.index(old_key)
                        charakter.selected_talente[idx] = new_key

            charakter.save_custom_talents()

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Talent '{name}' wurde aktualisiert.")

        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Talents: {e}")
            self.show_error("Fehler beim Aktualisieren des Talents")

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Talenten."""
        import time
        from kivy.metrics import dp
        from kivy.core.window import Window

        talente = self.get_all_talente()
        if not talente:
            self.show_error("Keine Talente zum Löschen verfügbar.")
            return

        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        self._talent_checkboxes = {}
        self._talent_last_cb_times = {}

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
                if key in self._talent_last_cb_times and (now - self._talent_last_cb_times[key]) < 0.5:
                    return
                self._talent_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._talent_checkboxes[item_name] = checkbox

        for talent_name in sorted(talente):
            create_checkbox(talent_name)

        scroll_height = min(len(talente) * dp(48), dp(250))
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
            for talent_name in sorted(talente):
                if search_text and search_text.lower() not in talent_name.lower():
                    continue
                if talent_name in self._talent_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=talent_name))
                    cb_existing = self._talent_checkboxes[talent_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(talent_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Talent löschen"),
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
        for name, cb in self._talent_checkboxes.items():
            if cb.active:
                selected.append(name)

        if not selected:
            self.show_error("Bitte wähle mindestens ein Talent zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Talent",
            on_confirm=self._confirm_delete_talent
        )

    def save_talent(self, *args):
        """Speichert ein neues Talent"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name des Talents darf nicht leer sein.")
            return

        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        rang = self.dialog_content.ids.rang_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        voraussetzungen = [v.strip() for v in self.dialog_content.ids.voraussetzungen_input.text.split(',') if v.strip()]
        neue_maechte_text = self.dialog_content.ids.neue_maechte_input.text.strip()
        machtpunkte_text = self.dialog_content.ids.machtpunkte_input.text.strip()

        if neue_maechte_text and not neue_maechte_text.isdigit():
            self.show_error("Neue Mächte muss eine gültige Zahl sein.")
            return

        if machtpunkte_text and not machtpunkte_text.isdigit():
            self.show_error("Machtpunkte müssen eine gültige Zahl sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.talente:
                self.show_error(f"Talent '{name}' existiert bereits.")
                return

            new_talent = Talent(
                name=name,
                kategorie=kategorie,
                rang=rang,
                beschreibung=beschreibung,
                voraussetzungen=voraussetzungen,
                neue_maechte=int(neue_maechte_text) if neue_maechte_text else 0,
                machtpunkte=int(machtpunkte_text) if machtpunkte_text else 0,
                custom=True
            )

            charakter.add_talent(new_talent)

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Talent '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Talents: {e}")
            self.show_error("Fehler beim Speichern des Talents")

    def delete_talent(self, *args):
        """Löscht die ausgewählten Talente"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens ein Talent zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            for talent_name in selected:
                charakter.remove_talent(talent_name)
                Logger.info(f"Talent '{talent_name}' wurde gelöscht.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_eigenschaften_widget()
            self._show_success_snackbar(f"{len(selected)} Talent(e) gelöscht")

            Logger.info(f"{len(selected)} Talent(e) wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Talente: {e}")
            self.show_error("Fehler beim Löschen der Talente")

    def _on_delete_action_clicked(self, *args):
        """Phase 1: Zeigt Bestätigungs-Popup vor dem Löschen (Two-Phase Pattern)"""
        if not self.dialog_content:
            return

        selected = self.dialog_content.get_selected_items()
        if not selected:
            self.show_error("Bitte wähle mindestens ein Talent zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Talent",
            on_confirm=self._confirm_delete_talent
        )

    def _confirm_delete_talent(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for talent_name in selected:
                charakter.remove_talent(talent_name)
                Logger.info(f"Talent '{talent_name}' wurde gelöscht.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_eigenschaften_widget()
            self._show_success_snackbar(f"{len(selected)} Talent(e) gelöscht")

            Logger.info(f"{len(selected)} Talent(e) wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Talente: {e}")
            self.show_error("Fehler beim Löschen der Talente")

    def _show_delete_confirmation_popup(self, selected_items, item_type, on_confirm):
        """Zeigt separates Bestätigungs-Popup OHNE Checkboxen (Two-Phase Pattern).
        
        Verwendet das gleiche Pattern wie HTML-Export in html_manager.py.
        """
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

    def on_talent_select(self, talent_name):
        """Callback wenn ein Talent im Dropdown ausgewählt wurde"""
        self.selected_talent = talent_name
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_talent_text')):
            self.dialog_content.ids.selected_talent_text.text = talent_name
            Logger.info(f"Talent '{talent_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt das aktive Overlay"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_talent = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung als Snackbar (nicht-blockierend)"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception:
            pass
        Logger.error(f"Talent-Fehler: {message}")

    def get_all_talente(self):
        """Gibt eine Liste aller verfügbaren Talente zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.talente.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Talente: {e}")
        return []

    def _refresh_eigenschaften_widget(self):
        """Aktualisiert das Talente-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Talente', 'talente_widget')
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
        except Exception as e:
            Logger.debug(f"Talente-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass