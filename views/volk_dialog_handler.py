# views/volk_dialog_handler.py
"""
Dialog-Handler für Völker (Hinzufügen/Bearbeiten/Löschen).

Aus views/volk_popup.py ausgezogen; der VolkGeneratorWizard wird lazy aus
volk_popup importiert (vermeidet Import-Zyklus, lädt dabei dessen KV-Datei).
volk_popup re-exportiert VolkDialogHandler für bestehende Importe.
"""

import time

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from models.volk import Volk
from utils.platform_utils import is_mobile_layout

_mobile = is_mobile_layout()


class VolkDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_volk = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt den Wizard zum Erstellen eines neuen Volkes"""
        from views.volk_popup import VolkGeneratorWizard  # Lazy: vermeidet Import-Zyklus
        wizard = VolkGeneratorWizard(
            controller=self.controller,
            callback=self._on_volk_created
        )
        wizard.start_wizard()

    def show_edit_dialog(self, volk_name):
        """Zeigt den Wizard zum Bearbeiten eines Volkes"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if volk_name not in charakter.voelker:
                self.show_error(f"Abstammung '{volk_name}' nicht gefunden.")
                return
            
            volk = charakter.voelker[volk_name]
            
            from views.volk_popup import VolkGeneratorWizard  # Lazy: vermeidet Import-Zyklus
            wizard = VolkGeneratorWizard(
                controller=self.controller,
                callback=self._on_volk_created,
                edit_volk=volk
            )
            wizard.start_wizard()
            
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeiten-Dialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeiten-Dialogs")

    def _on_volk_created(self, volk_name, volk_obj):
        """Callback nach erfolgreicher Volk-Erstellung/Bearbeitung.
        Wählt das Volk aus und öffnet das Zusatzelement-Overlay (Phase 2),
        damit der Benutzer freie Talente/Attribute sofort auswählen kann."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                if widget and hasattr(widget, 'open_volk_dropdown'):
                    widget.open_volk_dropdown()
                    Logger.info(f"Neues Volk '{volk_name}' erstellt — Overlay geöffnet")
                    
                    # Force refresh of Eigenschaften view after overlay animation completes
                    # This ensures dice icons are properly updated when Volkseigenarten
                    # modify attributes
                    from kivy.clock import Clock
                    Clock.schedule_once(self._force_eigenschaften_refresh, 0.5)
                    return
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Overlays für neues Volk: {e}")
        self._refresh_volk_view()

    def _force_eigenschaften_refresh(self, dt):
        """Erzwingt ein UI-Refresh der Eigenschaften-View nach Volkseigenarten-Änderungen."""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'controller') and app.controller:
                app.controller.dispatch('on_charakter_updated')
                Logger.debug("Eigenschaften-View Refresh nach Volkseigenarten erzwungen")
        except Exception as e:
            Logger.error(f"Fehler beim Erzwingen des Eigenschaften-Refresh: {e}")

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Völkern."""
        import time
        from kivymd.uix.list import MDListItemTrailingCheckbox

        voelker = self.get_all_voelker()
        if not voelker:
            self.show_error("Keine Abstammungen zum Löschen verfügbar.")
            return

        self._volk_checkboxes = {}
        self._volk_last_cb_times = {}

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
                if key in self._volk_last_cb_times and (now - self._volk_last_cb_times[key]) < 0.5:
                    return
                self._volk_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._volk_checkboxes[item_name] = checkbox

        for volk_name in sorted(voelker):
            create_checkbox(volk_name)

        scroll_height = min(len(voelker) * dp(48), dp(250))
        scroll = MDScrollView(
            size_hint=(1, None),
            height=scroll_height,
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(20) if _mobile else dp(15),
            bar_margin=dp(8) if _mobile else dp(4),
        )
        if _mobile:
            scroll.scroll_type = ['bars', 'content']
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
            for volk_name in sorted(voelker):
                if search_text and search_text.lower() not in volk_name.lower():
                    continue
                if volk_name in self._volk_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=volk_name))
                    cb_existing = self._volk_checkboxes[volk_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(volk_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Abstammung löschen"),
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
        selected = [name for name, cb in self._volk_checkboxes.items() if cb.active]

        if not selected:
            self.show_error("Bitte wähle mindestens eine Abstammung zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected, item_type="Abstammung", on_confirm=self._confirm_delete_volk
        )

    def save_volk(self, *args):
        """Speichert ein neues Volk"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name der Abstammung darf nicht leer sein.")
            return

        handicaps = [h.strip() for h in self.dialog_content.ids.handicaps_input.text.split(',') if h.strip()]
        talente = [t.strip() for t in self.dialog_content.ids.talente_input.text.split(',') if t.strip()]
        besonderheiten = [b.strip() for b in self.dialog_content.ids.besonderheiten_input.text.split(',') if b.strip()]

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.voelker:
                self.show_error(f"Abstammung '{name}' existiert bereits.")
                return

            new_volk = Volk(
                name=name,
                handicaps=handicaps,
                talente=talente,
                besonderheiten=besonderheiten,
                custom=True
            )

            charakter.voelker[name] = new_volk

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Volk '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Volks: {e}")
            self.show_error("Fehler beim Speichern des Volks")

    def delete_volk(self, *args):
        """Löscht die ausgewählten Völker"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Abstammung zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            deleted_count = 0
            skipped_count = 0
            for volk_name in selected:
                if volk_name in charakter.voelker:
                    if charakter.voelker[volk_name].ausgewaehlt:
                        Logger.warning(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                        skipped_count += 1
                        continue

                    del charakter.voelker[volk_name]
                    Logger.info(f"Volk '{volk_name}' wurde gelöscht.")
                    deleted_count += 1

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_volk_view()

            if deleted_count > 0 and skipped_count > 0:
                self._show_success_snackbar(
                    f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen (aktuell ausgewählt)"
                )
            elif deleted_count > 0:
                self._show_success_snackbar(f"{deleted_count} Abstammung(en) gelöscht")
            else:
                self.show_error(
                    "Kein Volk konnte gelöscht werden.\n"
                    "Wähle das aktuell ausgewählte Volk zuerst ab, bevor du es löschst."
                )

            Logger.info(f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Völker: {e}")
            self.show_error("Fehler beim Löschen der Abstammungen")

    def _confirm_delete_volk(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            deleted_count = 0
            skipped_count = 0
            for volk_name in selected:
                if volk_name in charakter.voelker:
                    if charakter.voelker[volk_name].ausgewaehlt:
                        Logger.warning(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                        skipped_count += 1
                        continue

                    del charakter.voelker[volk_name]
                    Logger.info(f"Volk '{volk_name}' wurde gelöscht.")
                    deleted_count += 1

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_volk_view()

            if deleted_count > 0 and skipped_count > 0:
                self._show_success_snackbar(
                    f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen (aktuell ausgewählt)"
                )
            elif deleted_count > 0:
                self._show_success_snackbar(f"{deleted_count} Abstammung(en) gelöscht")
            else:
                self.show_error(
                    "Kein Volk konnte gelöscht werden.\n"
                    "Wähle das aktuell ausgewählte Volk zuerst ab, bevor du es löschst."
                )

            Logger.info(f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Völker: {e}")
            self.show_error("Fehler beim Löschen der Abstammungen")

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

    def on_volk_select(self, volk_name):
        """Callback wenn ein Volk im Dropdown ausgewählt wurde"""
        self.selected_volk = volk_name
        # Dialog-Content aktualisieren wenn vorhanden
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_volk_text')):
            self.dialog_content.ids.selected_volk_text.text = volk_name
            Logger.info(f"Volk '{volk_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_volk = None

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
        Logger.error(f"Volk-Fehler: {message}")

    def get_all_voelker(self):
        """Gibt eine Liste aller verfügbaren Völker zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.voelker.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Völker: {e}")
        return []

    def _refresh_volk_view(self):
        """Aktualisiert das Volk-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                if widget and hasattr(widget, 'aktualisiere_ui'):
                    widget.aktualisiere_ui()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.warning(f"Volk-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass
