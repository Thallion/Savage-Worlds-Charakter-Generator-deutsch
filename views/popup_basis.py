# views/popup_basis.py
"""
Gemeinsame Basis für die Element-Dialog-Handler (Waffe, Rüstung, Schild,
Ausrüstung, Talent, Handicap, Macht, Fertigkeit).

Bündelt das in allen Handlern identische Gerüst:
- Overlay-Beschaffung und Dialog-Schließen
- Fehler-/Erfolgsmeldungen über den Dialog-Service
- Two-Phase-Lösch-Flow: Auswahl-Popup mit Checkboxen + Suchfeld (Phase 1)
  → separates Bestätigungs-Popup ohne Checkboxen (Phase 2)

Die Android-Workarounds (on_release + 500ms-Debounce für Checkboxen,
separates Bestätigungs-Popup, Clock-verzögertes dismiss) sind unverändert
aus den Einzeldateien übernommen — siehe docs/ANDROID_WORKAROUNDS.md.
Historisch existieren zwei Dismiss-Timing-Varianten für das Bestätigungs-
Popup; die Basis liefert die gestaffelte Variante (Waffe/Rüstung/Schild/
Ausrüstung), `SofortDismissMixin` die sofortige Variante (Talent/Handicap/
Macht/Fertigkeit).

Element-spezifisch bleiben in den Subklassen: Hinzufügen/Bearbeiten/Speichern,
das tatsächliche Löschen (`_confirm_delete_elemente`) und der View-Refresh.
"""

import time

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout


class BasisDialogHandler:
    """Gemeinsames Gerüst der Element-Dialog-Handler.

    Subklassen konfigurieren:
        element_name         Singular, z.B. "Waffe" (Dialogtitel, Meldungen)
        element_name_plural  Plural, z.B. "Waffen"
        artikel_unbestimmt   "eine" (die Waffe) bzw. "ein" (das Talent)

    Subklassen implementieren:
        _get_loeschbare_elemente()   Liste der löschbaren Element-Namen
        _confirm_delete_elemente()   Phase 2: tatsächliches Löschen
        _reset_selection()           Auswahl zurücksetzen (z.B. selected_waffe)
    """

    element_name = "Element"
    element_name_plural = "Elemente"
    artikel_unbestimmt = "ein"

    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.dialog_content = None

    # ------------------------------------------------------------------
    # Hooks für Subklassen
    # ------------------------------------------------------------------
    def _get_loeschbare_elemente(self):
        """Gibt die Liste der löschbaren Element-Namen zurück."""
        raise NotImplementedError

    def _confirm_delete_elemente(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch."""
        raise NotImplementedError

    def _reset_selection(self):
        """Setzt die element-spezifische Auswahl zurück (z.B. selected_waffe)."""

    # ------------------------------------------------------------------
    # Overlay / Dialog-Verwaltung
    # ------------------------------------------------------------------
    def _get_overlay(self):
        """Gibt eine gecachte ElementOverlay-Instanz zurück"""
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self._reset_selection()

    # ------------------------------------------------------------------
    # Meldungen
    # ------------------------------------------------------------------
    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception as e:
            Logger.warning(f"{self.element_name}-Fehler: Dialog-Service nicht verfügbar: {e}")
        Logger.error(f"{self.element_name}-Fehler: {message}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception as e:
            Logger.warning(f"{self.element_name}-Snackbar konnte nicht angezeigt werden: {e}")

    # ------------------------------------------------------------------
    # Two-Phase-Lösch-Flow
    # ------------------------------------------------------------------
    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Elementen (Phase 1)."""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        elemente = self._get_loeschbare_elemente()
        if not elemente:
            self.show_error(f"Keine {self.element_name_plural} zum Löschen verfügbar.")
            return

        self._delete_checkboxes = {}
        self._delete_last_cb_times = {}

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
                if key in self._delete_last_cb_times and (now - self._delete_last_cb_times[key]) < 0.5:
                    return
                self._delete_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._delete_checkboxes[item_name] = checkbox

        for element_name in sorted(elemente):
            create_checkbox(element_name)

        scroll_height = min(len(elemente) * dp(48), dp(250))
        scroll = MDScrollView(
            size_hint=(1, None),
            height=scroll_height,
            do_scroll_x=False,
            do_scroll_y=True,
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
            for element_name in sorted(elemente):
                if search_text and search_text.lower() not in element_name.lower():
                    continue
                # Bestehende Checkbox wiederverwenden statt neue zu erstellen
                if element_name in self._delete_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=element_name))
                    cb_existing = self._delete_checkboxes[element_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(element_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text=f"{self.element_name} löschen"),
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
        selected = [name for name, cb in self._delete_checkboxes.items() if cb.active]

        if not selected:
            self.show_error(
                f"Bitte wähle mindestens {self.artikel_unbestimmt} {self.element_name} zum Löschen aus."
            )
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected,
            item_type=self.element_name,
            on_confirm=self._confirm_delete_elemente,
        )

    def _confirm_popup_callbacks(self, dismiss_fn, on_confirm):
        """Button-Callbacks des Bestätigungs-Popups (gestaffelte Variante).

        dismiss() darf nicht synchron im on_release-Handler aufgerufen
        werden – auf Android blockiert das laufende Touch-Event die
        Dismiss-Animation. Daher erst im nächsten Frame schließen und
        on_confirm() mit ausreichend Abstand danach ausführen.
        """
        def _on_cancel(x):
            Clock.schedule_once(lambda dt: dismiss_fn(), 0)
            Clock.schedule_once(dismiss_fn, 0.2)

        def _on_confirm_release(x):
            Clock.schedule_once(lambda dt: dismiss_fn(), 0)
            Clock.schedule_once(dismiss_fn, 0.2)
            Clock.schedule_once(lambda dt: on_confirm(), 0.35)

        return _on_cancel, _on_confirm_release

    def _show_delete_confirmation_popup(self, selected_items, item_type, on_confirm):
        """Zeigt separates Bestätigungs-Popup OHNE Checkboxen (Two-Phase Pattern)."""
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText

        content = MDList(size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        for item_name in selected_items:
            list_item = MDListItem(size_hint_y=None, height=dp(48))
            list_item.add_widget(MDListItemSupportingText(text=item_name))
            content.add_widget(list_item)

        scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True)
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

        _on_cancel, _on_confirm_release = self._confirm_popup_callbacks(
            _dismiss_confirm_popup, on_confirm
        )

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


class SofortDismissMixin:
    """Dismiss-Timing-Variante der neueren Popups (Talent/Handicap/Macht/Fertigkeit).

    Sofortiger Dismiss-Versuch plus verzögerter Nachfass-Dismiss, falls der
    erste auf Android durch Timing-Probleme der Animation nicht gegriffen hat.
    """

    def _confirm_popup_callbacks(self, dismiss_fn, on_confirm):
        def _on_cancel(x):
            dismiss_fn()
            Clock.schedule_once(dismiss_fn, 0.15)

        def _on_confirm_release(x):
            # Dialog zuerst schließen, dann die eigentliche Aktion verzögert
            # ausführen. Auf Android kann das synchrone Aufrufen von
            # on_confirm() (mit UI-Refresh) die Dismiss-Animation unterbrechen
            # und den Dialog in einem inkonsistenten Zustand hinterlassen.
            dismiss_fn()
            Clock.schedule_once(dismiss_fn, 0.15)
            Clock.schedule_once(lambda dt: on_confirm(), 0.2)

        return _on_cancel, _on_confirm_release
