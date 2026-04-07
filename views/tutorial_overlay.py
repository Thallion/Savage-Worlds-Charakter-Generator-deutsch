# views/tutorial_overlay.py
"""
Tutorial-Overlay mit Spotlight-Funktion für geführte Einführung.
"""

import time

from kivy.lang import Builder
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.scrollview import MDScrollView

from utils.platform_utils import is_mobile_layout

_mobile = is_mobile_layout()


class SpotlightOverlay(Widget):
    """
    Overlay-Widget mit Spotlight-Ausschnitt.
    Zeigt einen halbtransparenten Hintergrund mit einem Ausschnitt
    um das hervorgehobene Element.
    """
    
    background_color = ListProperty([0, 0, 0, 0.7])
    spotlight_rect = ListProperty([0, 0, 0, 0])
    spotlight_radius = NumericProperty(dp(20))
    corner_radius = ListProperty([dp(10)])
    animation_duration = NumericProperty(0.3)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._spotlight_pos = (0, 0)
        self._spotlight_size = (0, 0)
    
    def set_spotlight(self, widget, margin=dp(10)):
        """
        Setzt den Spotlight auf ein Widget.
        
        Args:
            widget: Das Widget das hervorgehoben werden soll
            margin: Zusätzlicher Abstand um das Widget
        """
        if not widget:
            self.spotlight_rect = [0, 0, 0, 0]
            return
        
        try:
            pos = widget.to_window(*widget.pos)
            size = widget.size
            
            x = pos[0] - margin
            y = pos[1] - margin
            w = size[0] + 2 * margin
            h = size[1] + 2 * margin
            
            self._spotlight_pos = pos
            self._spotlight_size = size
            
            self.spotlight_rect = [x, y, w, h]
            Logger.debug(f"Spotlight gesetzt auf: {self.spotlight_rect}")
        except Exception as e:
            Logger.error(f"Fehler beim Setzen des Spotlights: {e}")
            self.spotlight_rect = [0, 0, 0, 0]
    
    def clear_spotlight(self):
        """Entfernt den Spotlight."""
        self.spotlight_rect = [0, 0, 0, 0]
    
    def on_spotlight_rect(self, instance, value):
        """Wird aufgerufen wenn sich der Spotlight ändert."""
        self.canvas.ask_update()


class TutorialDialog:
    """
    Dialog für Tutorial-Schritte.
    Zeigt Erklärungen und Navigation.
    """
    
    def __init__(self, tutorial_service, on_complete=None, on_skip=None):
        self.tutorial_service = tutorial_service
        self.on_complete = on_complete
        self.on_skip = on_skip
        self.current_step = 0
        self.dialog = None
        self.steps = tutorial_service.get_welcome_steps()
        self._last_nav_time = 0  # Debounce für Navigation (Android Touch-Bounce)

    def _nav_debounce_check(self) -> bool:
        """Prüft ob ein Navigations-Event zu schnell hintereinander kommt."""
        now = time.monotonic()
        if (now - self._last_nav_time) < 0.5:
            return False
        self._last_nav_time = now
        return True

    def start(self):
        """Startet das Tutorial."""
        if not self.steps:
            Logger.warning("Keine Tutorial-Schritte gefunden")
            return

        self.current_step = 0
        self._show_step()

    def _show_step(self):
        """Zeigt den aktuellen Schritt."""
        if self.current_step >= len(self.steps):
            self._finish_tutorial()
            return

        step = self.steps[self.current_step]
        title = step.get('title', f'Schritt {self.current_step + 1}')
        text = step.get('text', '').replace('\\n', '\n')

        if self.dialog:
            self.dialog.dismiss()

        content = self._create_content(text, self.current_step + 1, len(self.steps))

        if _mobile:
            # Mobile: kompakte Buttons
            buttons = []
            if self.current_step > 0:
                back_btn = MDButton(style="text", on_release=lambda x: self._previous_step(),
                                    size_hint_x=None, width=dp(40))
                back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
                buttons.append(back_btn)

            skip_btn = MDButton(style="text", on_release=lambda x: self._skip_tutorial(),
                                size_hint_x=None, width=dp(40))
            skip_btn.add_widget(MDButtonIcon(icon="close"))
            buttons.append(skip_btn)

            is_last = self.current_step >= len(self.steps) - 1
            next_icon = "check" if is_last else "arrow-right"
            next_btn = MDButton(
                style="filled",
                on_release=lambda x: self._finish_tutorial() if is_last else self._next_step(),
                size_hint_x=None, width=dp(40)
            )
            next_btn.add_widget(MDButtonIcon(icon=next_icon))
            buttons.append(next_btn)
        else:
            # Desktop: Buttons mit Text
            buttons = []
            if self.current_step > 0:
                buttons.append(
                    MDButton(
                        MDButtonText(text="Zurück"),
                        style="outlined",
                        on_release=lambda x: self._previous_step()
                    )
                )

            buttons.append(
                MDButton(
                    MDButtonText(text="Überspringen"),
                    style="text",
                    on_release=lambda x: self._skip_tutorial()
                )
            )

            is_last = self.current_step >= len(self.steps) - 1
            next_text = "Fertig" if is_last else "Weiter"
            buttons.append(
                MDButton(
                    MDButtonText(text=next_text),
                    style="filled",
                    on_release=lambda x: self._finish_tutorial() if is_last else self._next_step()
                )
            )

        self.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(*buttons),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.dialog.open()

    def _create_content(self, text, current, total):
        """Erstellt den Content für den Dialog."""
        # Verfügbare Höhe für Scroll-Bereich berechnen
        # Dialog: ~85% Bildschirmbreite, Höhe wird auto-berechnet
        # Headline ~dp(56), Buttons ~dp(56), Padding ~dp(40), Dots ~dp(24)
        is_landscape = Window.width > Window.height
        if _mobile and is_landscape:
            # Querformat: wenig Höhe verfügbar → kleinerer ScrollView damit Buttons sichtbar bleiben
            max_content_height = Window.height * 0.35
        elif _mobile:
            max_content_height = Window.height * 0.5
        else:
            max_content_height = dp(400)

        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6) if _mobile else dp(12),
            size_hint_y=None,
        )

        # Text in ScrollView für Querformat
        text_label = MDLabel(
            text=text,
            theme_text_color="Primary",
            markup=True,
            size_hint_y=None,
            adaptive_height=True,
        )

        scroll = MDScrollView(
            size_hint_y=None,
            height=max_content_height,
        )
        text_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
            padding=(0, 0, dp(8), 0),
        )
        text_container.add_widget(text_label)
        scroll.add_widget(text_container)
        layout.add_widget(scroll)

        # Fortschritts-Dots
        dots_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(20),
            spacing=dp(4),
            adaptive_width=True,
            pos_hint={"center_x": 0.5}
        )
        for i in range(total):
            dot = MDLabel(
                text="●" if i == current - 1 else "○",
                theme_text_color="Primary" if i == current - 1 else "Secondary",
                size_hint_x=None,
                width=dp(20),
                font_style="Body" if _mobile else "Body",
                role="small" if _mobile else "medium",
            )
            dots_layout.add_widget(dot)
        layout.add_widget(dots_layout)

        # Gesamthöhe: ScrollView + Dots
        layout.height = max_content_height + dp(26)

        return layout

    def _next_step(self):
        """Geht zum nächsten Schritt."""
        if not self._nav_debounce_check():
            return
        self.current_step += 1
        self._show_step()

    def _previous_step(self):
        """Geht zum vorherigen Schritt."""
        if not self._nav_debounce_check():
            return
        if self.current_step > 0:
            self.current_step -= 1
            self._show_step()

    def _skip_tutorial(self):
        """Überspringt das Tutorial."""
        if not self._nav_debounce_check():
            return
        if self.dialog:
            self.dialog.dismiss()
        self.tutorial_service.mark_welcome_completed()
        if self.on_skip:
            self.on_skip()
        Logger.info("Tutorial übersprungen")

    def _finish_tutorial(self):
        """Beendet das Tutorial."""
        if not self._nav_debounce_check():
            return
        if self.dialog:
            self.dialog.dismiss()
        self.tutorial_service.mark_welcome_completed()
        if self.on_complete:
            self.on_complete()
        Logger.info("Tutorial abgeschlossen")


class TabHintDialog:
    """
    Dialog für kontextuelle Tab-Hilfen.
    """
    
    def __init__(self):
        self.dialog = None
    
    def show_hint(self, title, text, tab_id=None):
        """
        Zeigt einen Hilfe-Dialog.
        
        Args:
            title: Titel des Dialogs
            text: Hilfe-Text
            tab_id: Optional die Tab-ID für Status-Tracking
        """
        if self.dialog:
            self.dialog.dismiss()
        
        content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
        )
        text_label = MDLabel(
            text=text.replace('\\n', '\n\n'),
            theme_text_color="Primary",
            size_hint_y=None,
            adaptive_height=True,
        )
        content.add_widget(text_label)
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self._on_close(tab_id)
                )
            ),
            size_hint=(0.85, None),
        )
        self.dialog.open()
    
    def _on_close(self, tab_id):
        """Wird beim Schließen aufgerufen."""
        if self.dialog:
            self.dialog.dismiss()
        
        if tab_id:
            try:
                from services.service_container import service_container
                tutorial_service = service_container.get_tutorial_service()
                if tutorial_service:
                    tutorial_service.mark_tab_hint_as_shown(tab_id)
            except Exception as e:
                Logger.error(f"Fehler beim Markieren des Tab-Hints: {e}")
    
    def dismiss(self):
        """Schließt den Dialog."""
        if self.dialog:
            self.dialog.dismiss()


_welcome_tutorial_active = False


def show_welcome_tutorial(on_complete=None, on_skip=None, force=False):
    """
    Zeigt das Willkommens-Tutorial.

    Args:
        on_complete: Callback wenn Tutorial abgeschlossen
        on_skip: Callback wenn Tutorial übersprungen
        force: Wenn True, wird der Tutorial-Zustand zurückgesetzt und das Tutorial immer gestartet
    """
    global _welcome_tutorial_active

    if _welcome_tutorial_active:
        Logger.info("Willkommens-Tutorial ist bereits geöffnet")
        return

    try:
        from services.service_container import service_container

        tutorial_service = service_container.get_tutorial_service()
        if not tutorial_service:
            Logger.error("TutorialService nicht verfügbar")
            return

        if force:
            tutorial_service.reset_welcome()
            tutorial_service.reset_all_tab_hints()
        elif not tutorial_service.should_show_welcome():
            Logger.info("Willkommens-Tutorial wurde bereits abgeschlossen")
            return

        _welcome_tutorial_active = True

        def _on_done():
            global _welcome_tutorial_active
            _welcome_tutorial_active = False
            if on_complete:
                on_complete()

        def _on_skipped():
            global _welcome_tutorial_active
            _welcome_tutorial_active = False
            if on_skip:
                on_skip()

        dialog = TutorialDialog(tutorial_service, on_complete=_on_done, on_skip=_on_skipped)
        dialog.start()

    except Exception as e:
        _welcome_tutorial_active = False
        Logger.error(f"Fehler beim Starten des Tutorials: {e}")


def show_tab_hint(tab_id):
    """
    Zeigt einen Tab-Hinweis.
    
    Args:
        tab_id: Die ID des Tabs
    """
    try:
        from services.service_container import service_container
        
        tutorial_service = service_container.get_tutorial_service()
        if not tutorial_service:
            return
        
        hint = tutorial_service.get_tab_hint(tab_id)
        if not hint:
            return
        
        dialog = TabHintDialog()
        dialog.show_hint(hint.get('title', ''), hint.get('text', ''), tab_id)
        
    except Exception as e:
        Logger.error(f"Fehler beim Anzeigen des Tab-Hints: {e}")


def reset_tutorial_state():
    """Setzt den Tutorial-Zustand zurück."""
    try:
        from services.service_container import service_container
        
        tutorial_service = service_container.get_tutorial_service()
        if tutorial_service:
            tutorial_service.reset_welcome()
            tutorial_service.reset_all_tab_hints()
            Logger.info("Tutorial-Zustand zurückgesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen des Tutorial-Zustands: {e}")
