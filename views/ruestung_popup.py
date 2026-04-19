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

from models.ruestung import Ruestung

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
        kv_path = os.path.join(base_path, 'views', 'ruestung_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'ruestung_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"ruestung_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

# RuestungDialogContent
class RuestungDialogContent(MDBoxLayout):
    def __init__(self, ruestung_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Rüstungs-Daten übergeben wurden, befülle die Felder
        if ruestung_data:
            self.edit_mode = True
            self.original_name = ruestung_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(ruestung_data), 0.1)
    
    def _fill_fields(self, ruestung_data):
        """Befüllt die Felder mit den Rüstungs-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = ruestung_data.get('name', '')
        
        if hasattr(self.ids, 'torso_input'):
            self.ids.torso_input.text = str(ruestung_data.get('torso', 0))
        
        if hasattr(self.ids, 'arme_input'):
            self.ids.arme_input.text = str(ruestung_data.get('arme', 0))
        
        if hasattr(self.ids, 'beine_input'):
            self.ids.beine_input.text = str(ruestung_data.get('beine', 0))
        
        if hasattr(self.ids, 'kopf_input'):
            self.ids.kopf_input.text = str(ruestung_data.get('kopf', 0))
        
        if hasattr(self.ids, 'mindeststaerke_input'):
            self.ids.mindeststaerke_input.text = ruestung_data.get('mindeststaerke', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(ruestung_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(ruestung_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = ruestung_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = ruestung_data.get('beschreibung', '')

class DeleteRuestungDialogContent(MDBoxLayout):
    def __init__(self, ruestungen_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.ruestungen_callback = ruestungen_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.ruestungen_callback:
            return
            
        ruestungen = self.ruestungen_callback()
        if not ruestungen:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in ruestungen
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'ruestung_dropdown'):
            self.ids.ruestung_dropdown.text = text_item

class RuestungDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_ruestung = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen einer neuen Rüstung"""
        dialog_content = RuestungDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Rüstung hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_ruestung,
        )

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Rüstungen."""
        import time
        from kivy.metrics import dp

        ruestungen = self.get_all_ruestungen()
        if not ruestungen:
            self.show_error("Keine Rüstungen zum Löschen verfügbar.")
            return

        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        self._ruestung_checkboxes = {}
        self._ruestung_last_cb_times = {}

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
                if key in self._ruestung_last_cb_times and (now - self._ruestung_last_cb_times[key]) < 0.5:
                    return
                self._ruestung_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._ruestung_checkboxes[item_name] = checkbox

        for ruestung_name in sorted(ruestungen):
            create_checkbox(ruestung_name)

        scroll_height = min(len(ruestungen) * dp(48), dp(250))
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
            for ruestung_name in sorted(ruestungen):
                if search_text and search_text.lower() not in ruestung_name.lower():
                    continue
                if ruestung_name in self._ruestung_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=ruestung_name))
                    cb_existing = self._ruestung_checkboxes[ruestung_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(ruestung_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Rüstung löschen"),
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
        for name, cb in self._ruestung_checkboxes.items():
            if cb.active:
                selected.append(name)

        if not selected:
            self.show_error("Bitte wähle mindestens eine Rüstung zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type="Rüstung",
            on_confirm=self._confirm_delete_ruestung
        )

    def _confirm_delete_ruestung(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for ruestung_name in selected:
                success = charakter.remove_ausruestung(ruestung_name)
                if success:
                    Logger.info(f"Rüstung '{ruestung_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Rüstung '{ruestung_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Rüstung(en) gelöscht")

            Logger.info(f"{len(selected)} Rüstung(en) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Rüstungen: {e}")
            self.show_error("Fehler beim Löschen der Rüstungen")

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

    def show_edit_dialog(self, ruestung_name):
        """Zeigt das Overlay zum Bearbeiten einer bestehenden Rüstung"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            ruestung = charakter.ausruestung.get(ruestung_name)
            if not ruestung:
                self.show_error(f"Rüstung '{ruestung_name}' nicht gefunden.")
                return

            ruestung_data = {
                'name': ruestung.name,
                'torso': ruestung.torso,
                'arme': ruestung.arme,
                'beine': ruestung.beine,
                'kopf': ruestung.kopf,
                'mindeststaerke': ruestung.mindeststaerke,
                'gewicht': ruestung.gewicht,
                'kosten': ruestung.kosten,
                'setting': ruestung.setting,
                'beschreibung': ruestung.beschreibung
            }

            dialog_content = RuestungDialogContent(ruestung_data=ruestung_data)
            self.dialog_content = dialog_content
            self.selected_ruestung = ruestung_name

            overlay = self._get_overlay()
            overlay.open(
                title="Rüstung bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_ruestung,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_ruestung(self, *args):
        """Aktualisiert eine bestehende Rüstung"""
        if not self.dialog_content or not self.selected_ruestung:
            Logger.error("Dialog-Content oder ausgewählte Rüstung nicht gefunden")
            return
            
        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        
        # Rüstungswerte sammeln
        torso_text = self.dialog_content.ids.torso_input.text.strip()
        arme_text = self.dialog_content.ids.arme_input.text.strip()
        beine_text = self.dialog_content.ids.beine_input.text.strip()
        kopf_text = self.dialog_content.ids.kopf_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Rüstung darf nicht leer sein.")
            return

        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return

        try:
            torso = int(torso_text) if torso_text else 0
            arme = int(arme_text) if arme_text else 0
            beine = int(beine_text) if beine_text else 0
            kopf = int(kopf_text) if kopf_text else 0
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für die Schutzwerte, Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Hole die bestehende Rüstung
            ruestung = charakter.ausruestung.get(self.selected_ruestung)
            if not ruestung:
                self.show_error(f"Rüstung '{self.selected_ruestung}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != ruestung.name and name in charakter.ausruestung:
                self.show_error(f"Rüstung mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere die Rüstung
            old_name = ruestung.name
            ruestung.name = name
            ruestung.torso = torso
            ruestung.arme = arme
            ruestung.beine = beine
            ruestung.kopf = kopf
            ruestung.mindeststaerke = mindeststaerke
            ruestung.gewicht = gewicht
            ruestung.kosten = kosten
            ruestung.setting = setting
            ruestung.beschreibung = beschreibung
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                charakter.ausruestung[name] = ruestung
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Rüstung '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Rüstung: {e}")
            self.show_error("Fehler beim Aktualisieren der Rüstung")

    def save_ruestung(self, *args):
        """Speichert eine neue Rüstung"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        
        # Rüstungswerte sammeln
        torso_text = self.dialog_content.ids.torso_input.text.strip()
        arme_text = self.dialog_content.ids.arme_input.text.strip()
        beine_text = self.dialog_content.ids.beine_input.text.strip()
        kopf_text = self.dialog_content.ids.kopf_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Rüstung darf nicht leer sein.")
            return

        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return

        try:
            torso = int(torso_text) if torso_text else 0
            arme = int(arme_text) if arme_text else 0
            beine = int(beine_text) if beine_text else 0
            kopf = int(kopf_text) if kopf_text else 0
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für die Schutzwerte, Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if name in charakter.ausruestung:
                self.show_error(f"Rüstung '{name}' existiert bereits.")
                return

            new_ruestung = Ruestung(
                name=name,
                torso=torso,
                arme=arme,
                beine=beine,
                kopf=kopf,
                mindeststaerke=mindeststaerke,
                setting=setting,
                gewicht=gewicht,
                kosten=kosten,
                beschreibung=beschreibung,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                kategorie='Rüstung',
                custom=True
            )
            
            success = charakter.add_ausruestung(new_ruestung)
            
            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                self.dismiss_dialog()
                Logger.info(f"Rüstung '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Rüstung '{name}' konnte nicht hinzugefügt werden.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Rüstung: {e}")
            self.show_error("Fehler beim Speichern der Rüstung")

    def delete_ruestung(self, *args):
        """Löscht die ausgewählten Rüstungen"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Rüstung zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            for ruestung_name in selected:
                success = charakter.remove_ausruestung(ruestung_name)
                if success:
                    Logger.info(f"Rüstung '{ruestung_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Rüstung '{ruestung_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Rüstung(en) gelöscht")
            
            Logger.info(f"{len(selected)} Rüstung(en) wurde(n) gelöscht.")
            self.dismiss_dialog()
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Rüstungen: {e}")
            self.show_error("Fehler beim Löschen der Rüstungen")

    def on_ruestung_select(self, ruestung_name):
        """Callback wenn eine Rüstung ausgewählt wurde"""
        self.selected_ruestung = ruestung_name

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_ruestung = None

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
        Logger.error(f"Rüstung-Fehler: {message}")

    def get_all_ruestungen(self):
        """Gibt eine Liste aller verfügbaren Rüstungen zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() 
                       if isinstance(item, Ruestung)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Rüstungen: {e}")
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