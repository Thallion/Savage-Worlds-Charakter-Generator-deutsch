# utils/dialog_cache.py
"""
Dialog-Cache-System für Performance-Optimierung (Android Performance Plan Schritt 8).

Bietet wiederverwendbare Dialog-Templates um die Kosten für Dialog-Erstellung zu reduzieren.
Häufig verwendete Dialoge werden gecacht und nur ihr Inhalt wird aktualisiert.
"""

from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp


class DialogCache:
    """
    Cache für wiederverwendbare Dialoge. Reduziert die Kosten für Dialog-Erstellung
    durch Wiederverwendung bestehender Dialog-Instanzen mit aktualisierten Inhalten.
    """

    def __init__(self):
        """Initialisiert den Dialog-Cache."""
        self._cached_dialogs = {}
        self._app = MDApp.get_running_app()
        self._theme_cls = self._app.theme_cls if self._app else None
        Logger.info("DialogCache initialisiert")

    def get_info_dialog(self, title="Information", message="", button_text="OK", on_confirm=None):
        """
        Holt oder erstellt einen Info-Dialog mit caching.

        Args:
            title (str): Dialog-Titel
            message (str): Hauptnachricht
            button_text (str): Text des Bestätigungs-Buttons
            on_confirm (callable): Callback beim Bestätigen

        Returns:
            MDDialog: Gecachte oder neue Dialog-Instanz
        """
        cache_key = "info_dialog"

        if cache_key not in self._cached_dialogs:
            Logger.debug("DialogCache: Erstelle neuen Info-Dialog")
            self._cached_dialogs[cache_key] = self._create_info_dialog()

        # Dialog-Inhalt aktualisieren
        dialog = self._cached_dialogs[cache_key]
        self._update_info_dialog(dialog, title, message, button_text, on_confirm)

        Logger.debug(f"DialogCache: Info-Dialog wiederverwendet - '{title}'")
        return dialog

    def get_confirmation_dialog(self, title="Bestätigung", message="",
                               confirm_text="Bestätigen", cancel_text="Abbrechen",
                               on_confirm=None, on_cancel=None):
        """
        Holt oder erstellt einen Bestätigungs-Dialog mit caching.

        Args:
            title (str): Dialog-Titel
            message (str): Hauptnachricht
            confirm_text (str): Text des Bestätigungs-Buttons
            cancel_text (str): Text des Abbrechen-Buttons
            on_confirm (callable): Callback beim Bestätigen
            on_cancel (callable): Callback beim Abbrechen

        Returns:
            MDDialog: Gecachte oder neue Dialog-Instanz
        """
        cache_key = "confirmation_dialog"

        if cache_key not in self._cached_dialogs:
            Logger.debug("DialogCache: Erstelle neuen Bestätigungs-Dialog")
            self._cached_dialogs[cache_key] = self._create_confirmation_dialog()

        # Dialog-Inhalt aktualisieren
        dialog = self._cached_dialogs[cache_key]
        self._update_confirmation_dialog(dialog, title, message,
                                       confirm_text, cancel_text,
                                       on_confirm, on_cancel)

        Logger.debug(f"DialogCache: Bestätigungs-Dialog wiederverwendet - '{title}'")
        return dialog

    def get_choice_dialog(self, title="Auswahl", message="", choices=None, on_choice=None):
        """
        Holt oder erstellt einen Auswahl-Dialog mit caching.

        Args:
            title (str): Dialog-Titel
            message (str): Hauptnachricht
            choices (list): Liste von (text, value) Tupeln
            on_choice (callable): Callback bei Auswahl

        Returns:
            MDDialog: Gecachte oder neue Dialog-Instanz
        """
        cache_key = f"choice_dialog_{len(choices) if choices else 0}"

        if cache_key not in self._cached_dialogs:
            Logger.debug(f"DialogCache: Erstelle neuen Auswahl-Dialog für {len(choices) if choices else 0} Optionen")
            self._cached_dialogs[cache_key] = self._create_choice_dialog(len(choices) if choices else 0)

        # Dialog-Inhalt aktualisieren
        dialog = self._cached_dialogs[cache_key]
        self._update_choice_dialog(dialog, title, message, choices, on_choice)

        Logger.debug(f"DialogCache: Auswahl-Dialog wiederverwendet - '{title}'")
        return dialog

    def _create_info_dialog(self):
        """Erstellt einen neuen Info-Dialog-Template."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )

        # Message-Label (wird später aktualisiert)
        message_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content.add_widget(message_label)

        # Dialog erstellen
        dialog = MDDialog(
            MDDialogHeadlineText(text=""),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: None  # Wird später aktualisiert
                )
            ),
            md_bg_color=self._theme_cls.surfaceColor if self._theme_cls else None,
            size_hint=(0.85, None),
            auto_dismiss=False,
        )

        # Referenzen für spätere Updates speichern
        dialog._cache_content = content
        dialog._cache_message_label = message_label

        return dialog

    def _create_confirmation_dialog(self):
        """Erstellt einen neuen Bestätigungs-Dialog-Template."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )

        # Message-Label (wird später aktualisiert)
        message_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content.add_widget(message_label)

        # Buttons (werden später aktualisiert)
        cancel_button = MDButton(
            MDButtonText(text="Abbrechen"),
            style="text",
            on_release=lambda x: None
        )

        confirm_button = MDButton(
            MDButtonText(text="Bestätigen"),
            style="text",
            on_release=lambda x: None
        )

        # Dialog erstellen
        dialog = MDDialog(
            MDDialogHeadlineText(text=""),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(cancel_button, confirm_button),
            md_bg_color=self._theme_cls.surfaceColor if self._theme_cls else None,
            size_hint=(0.85, None),
            auto_dismiss=False,
        )

        # Referenzen für spätere Updates speichern
        dialog._cache_content = content
        dialog._cache_message_label = message_label
        dialog._cache_cancel_button = cancel_button
        dialog._cache_confirm_button = confirm_button

        return dialog

    def _create_choice_dialog(self, choice_count):
        """Erstellt einen neuen Auswahl-Dialog-Template."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(20),
            adaptive_height=True
        )

        # Message-Label
        message_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content.add_widget(message_label)

        # Button-Container für Auswahloptionen
        button_container = MDBoxLayout(
            orientation="vertical" if choice_count > 3 else "horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48) if choice_count <= 3 else dp(48 * choice_count),
            adaptive_height=True
        )

        # Platzhalter-Buttons erstellen (werden später aktualisiert)
        choice_buttons = []
        for i in range(max(choice_count, 4)):  # Mindestens 4 für Flexibilität
            button = MDButton(
                style="elevated",
                size_hint_x=1 if choice_count > 3 else None,
                width=dp(120) if choice_count <= 3 else None,
                on_release=lambda x: None
            )
            button.add_widget(MDButtonText(text=""))
            button_container.add_widget(button)
            choice_buttons.append(button)

        content.add_widget(button_container)

        # Dialog erstellen
        dialog = MDDialog(
            MDDialogHeadlineText(text=""),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                )
            ),
            md_bg_color=self._theme_cls.surfaceColor if self._theme_cls else None,
            size_hint=(0.85, None),
            auto_dismiss=False,
        )

        # Referenzen für spätere Updates speichern
        dialog._cache_content = content
        dialog._cache_message_label = message_label
        dialog._cache_button_container = button_container
        dialog._cache_choice_buttons = choice_buttons

        return dialog

    def _update_info_dialog(self, dialog, title, message, button_text, on_confirm):
        """Aktualisiert den Inhalt eines Info-Dialogs."""
        # Titel aktualisieren
        if hasattr(dialog, 'children') and len(dialog.children) > 0:
            for child in dialog.children:
                if hasattr(child, 'text'):
                    child.text = title
                    break

        # Nachricht aktualisieren
        dialog._cache_message_label.text = message

        # Button-Text und Callback aktualisieren
        button_container = None
        for child in dialog.children:
            if hasattr(child, '__class__') and 'ButtonContainer' in child.__class__.__name__:
                button_container = child
                break

        if button_container and len(button_container.children) > 0:
            button = button_container.children[0]
            for button_child in button.children:
                if hasattr(button_child, 'text'):
                    button_child.text = button_text
                    break

            # Callback aktualisieren
            def handle_confirm(*args):
                dialog.dismiss()
                if on_confirm:
                    on_confirm()

            button.unbind(on_release=button.on_release)
            button.bind(on_release=handle_confirm)

    def _update_confirmation_dialog(self, dialog, title, message, confirm_text, cancel_text, on_confirm, on_cancel):
        """Aktualisiert den Inhalt eines Bestätigungs-Dialogs."""
        # Titel aktualisieren
        if hasattr(dialog, 'children') and len(dialog.children) > 0:
            for child in dialog.children:
                if hasattr(child, 'text'):
                    child.text = title
                    break

        # Nachricht aktualisieren
        dialog._cache_message_label.text = message

        # Button-Texte aktualisieren
        for child in dialog._cache_cancel_button.children:
            if hasattr(child, 'text'):
                child.text = cancel_text
                break

        for child in dialog._cache_confirm_button.children:
            if hasattr(child, 'text'):
                child.text = confirm_text
                break

        # Callbacks aktualisieren
        def handle_cancel(*args):
            dialog.dismiss()
            if on_cancel:
                on_cancel()

        def handle_confirm(*args):
            dialog.dismiss()
            if on_confirm:
                on_confirm()

        # Alte Bindings entfernen und neue setzen
        dialog._cache_cancel_button.unbind(on_release=dialog._cache_cancel_button.on_release)
        dialog._cache_confirm_button.unbind(on_release=dialog._cache_confirm_button.on_release)

        dialog._cache_cancel_button.bind(on_release=handle_cancel)
        dialog._cache_confirm_button.bind(on_release=handle_confirm)

    def _update_choice_dialog(self, dialog, title, message, choices, on_choice):
        """Aktualisiert den Inhalt eines Auswahl-Dialogs."""
        if not choices:
            choices = [("OK", "ok")]

        # Titel aktualisieren
        if hasattr(dialog, 'children') and len(dialog.children) > 0:
            for child in dialog.children:
                if hasattr(child, 'text'):
                    child.text = title
                    break

        # Nachricht aktualisieren
        dialog._cache_message_label.text = message

        # Buttons aktualisieren
        for i, button in enumerate(dialog._cache_choice_buttons):
            if i < len(choices):
                text, value = choices[i]
                button.opacity = 1
                button.disabled = False

                # Button-Text aktualisieren
                for child in button.children:
                    if hasattr(child, 'text'):
                        child.text = text
                        break

                # Callback aktualisieren
                def handle_choice(choice_value=value):
                    dialog.dismiss()
                    if on_choice:
                        on_choice(choice_value)

                button.unbind(on_release=button.on_release)
                button.bind(on_release=lambda x, v=value: handle_choice(v))
            else:
                # Button verstecken wenn nicht benötigt
                button.opacity = 0
                button.disabled = True

    def clear_cache(self):
        """Leert den Dialog-Cache."""
        for dialog in self._cached_dialogs.values():
            if dialog:
                try:
                    dialog.dismiss()
                except Exception as e:
                    # Dialog kann bereits geschlossen sein
                    Logger.warning(f"DialogCache: Dialog konnte nicht geschlossen werden: {e}")

        self._cached_dialogs.clear()
        Logger.info("DialogCache geleert")

    def get_cache_info(self):
        """
        Gibt Informationen über den Cache zurück.

        Returns:
            dict: Cache-Statistiken
        """
        return {
            'cached_dialogs': len(self._cached_dialogs),
            'dialog_types': list(self._cached_dialogs.keys())
        }


# Globale Cache-Instanz
_dialog_cache = None

def get_dialog_cache():
    """
    Holt die globale DialogCache-Instanz (Singleton-Pattern).

    Returns:
        DialogCache: Globale Cache-Instanz
    """
    global _dialog_cache
    if _dialog_cache is None:
        _dialog_cache = DialogCache()
    return _dialog_cache