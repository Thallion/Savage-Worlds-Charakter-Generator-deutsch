# views/popup_basis.py
"""
Gemeinsame Basis für die Element-Dialog-Handler (Waffe, Rüstung, Schild,
Ausrüstung, Talent, Handicap, Macht, Fertigkeit).

Bündelt das in allen Handlern identische Gerüst:
- Overlay-Beschaffung und Dialog-Schließen
- Fehler-/Erfolgsmeldungen über den Dialog-Service
- Two-Phase-Lösch-Flow: Auswahl über das `SearchBottomSheet` mit Suchfeld
  und Checkboxen (Phase 1) → separates Bestätigungs-Popup ohne Checkboxen
  (Phase 2)

Die Android-Workarounds (SearchBottomSheet statt MDDialog für die Suchliste,
on_release + 500ms-Debounce für Checkboxen, separates Bestätigungs-Popup,
Clock-verzögertes dismiss) — siehe docs/ANDROID_WORKAROUNDS.md.
Historisch existieren zwei Dismiss-Timing-Varianten für das Bestätigungs-
Popup; die Basis liefert die gestaffelte Variante (Waffe/Rüstung/Schild/
Ausrüstung), `SofortDismissMixin` die sofortige Variante (Talent/Handicap/
Macht/Fertigkeit).

Element-spezifisch bleiben in den Subklassen: Hinzufügen/Bearbeiten/Speichern,
das tatsächliche Löschen (`_confirm_delete_elemente`) und der View-Refresh.
"""

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout

from utils.platform_utils import is_mobile_layout

_mobile = is_mobile_layout()


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
        """Zeigt das Two-Phase Popup zum Löschen von Elementen (Phase 1).

        Die Auswahl läuft über `SearchBottomSheet` (ModalView), NICHT über
        einen `MDDialog`: Such-/Filterlisten in einem MDDialog scrollen auf
        Android nicht (der Dialog stiehlt die Touch-Events), und der
        Scrollbalken lag über den Checkboxen. Siehe
        docs/ANDROID_WORKAROUNDS.md → SearchBottomSheet.
        """
        elemente = self._get_loeschbare_elemente()
        if not elemente:
            self.show_error(f"Keine {self.element_name_plural} zum Löschen verfügbar.")
            return

        from views.ui_components import SearchBottomSheet

        self._delete_popup = SearchBottomSheet(
            title=f"{self.element_name} löschen",
            items=sorted(elemente),
            multi_select=True,
            on_confirm=self._on_delete_action_clicked,
            search_hint=f"{self.element_name} suchen...",
        )
        self._delete_popup.open()

    def _on_delete_action_clicked(self, selected=None, *args):
        """Phase 1: Übernimmt die Auswahl und zeigt das Bestätigungs-Popup."""
        selected = list(selected) if selected else []

        if not selected:
            self.show_error(
                f"Bitte wähle mindestens {self.artikel_unbestimmt} {self.element_name} zum Löschen aus."
            )
            return

        self._pending_delete_items = selected
        # Erst im nächsten Frame öffnen: das Auswahl-Sheet schließt sich
        # gerade, ein sofort geöffneter Dialog kann auf Android in dessen
        # Dismiss-Animation hängenbleiben.
        Clock.schedule_once(
            lambda dt: self._show_delete_confirmation_popup(
                selected_items=selected,
                item_type=self.element_name,
                on_confirm=self._confirm_delete_elemente,
            ),
            0.1,
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
        # Die feste Höhe gehört an den ScrollView, NICHT an sein Kind — sonst
        # sind Einträge jenseits der Deckelung nicht erreichbar.
        content.bind(minimum_height=content.setter('height'))
        if _mobile:
            # Platz für den breiten Scrollbalken, sonst liegt er über dem Text
            content.padding = [0, 0, dp(32), 0]

        for item_name in selected_items:
            list_item = MDListItem(size_hint_y=None, height=dp(48))
            list_item.add_widget(MDListItemSupportingText(text=item_name))
            content.add_widget(list_item)

        list_height = min(dp(48) * len(selected_items), dp(200))
        scroll = MDScrollView(
            size_hint=(1, None),
            height=list_height,
            do_scroll_x=False,
            do_scroll_y=True,
        )
        scroll.add_widget(content)

        main_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=list_height + dp(32),
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
