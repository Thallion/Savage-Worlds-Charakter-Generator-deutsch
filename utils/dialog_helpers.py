# utils/dialog_helpers.py
"""
Dialog-Helper-Funktionen für Performance-Optimierung (Android Performance Plan Schritt 8).

Stellt einfache Helper-Funktionen bereit, um gecachte Dialoge in bestehenden Views zu verwenden.
Diese ersetzen die direkten MDDialog-Instanziierungen durch Cache-optimierte Alternativen.
"""

from kivy.logger import Logger
from utils.dialog_cache import get_dialog_cache


def show_cached_info_dialog(title="Information", message="", button_text="OK", on_confirm=None):
    """
    Zeigt einen Info-Dialog mit caching.

    Args:
        title (str): Dialog-Titel
        message (str): Hauptnachricht
        button_text (str): Text des Bestätigungs-Buttons
        on_confirm (callable): Callback beim Bestätigen
    """
    cache = get_dialog_cache()
    dialog = cache.get_info_dialog(title, message, button_text, on_confirm)
    dialog.open()
    Logger.debug(f"DialogHelper: Info-Dialog geöffnet - '{title}'")


def show_cached_confirmation_dialog(title="Bestätigung", message="",
                                  confirm_text="Bestätigen", cancel_text="Abbrechen",
                                  on_confirm=None, on_cancel=None):
    """
    Zeigt einen Bestätigungs-Dialog mit caching.

    Args:
        title (str): Dialog-Titel
        message (str): Hauptnachricht
        confirm_text (str): Text des Bestätigungs-Buttons
        cancel_text (str): Text des Abbrechen-Buttons
        on_confirm (callable): Callback beim Bestätigen
        on_cancel (callable): Callback beim Abbrechen
    """
    cache = get_dialog_cache()
    dialog = cache.get_confirmation_dialog(title, message, confirm_text, cancel_text, on_confirm, on_cancel)
    dialog.open()
    Logger.debug(f"DialogHelper: Bestätigungs-Dialog geöffnet - '{title}'")


def show_cached_choice_dialog(title="Auswahl", message="", choices=None, on_choice=None):
    """
    Zeigt einen Auswahl-Dialog mit caching.

    Args:
        title (str): Dialog-Titel
        message (str): Hauptnachricht
        choices (list): Liste von (text, value) Tupeln
        on_choice (callable): Callback bei Auswahl
    """
    if not choices:
        choices = [("OK", "ok")]

    cache = get_dialog_cache()
    dialog = cache.get_choice_dialog(title, message, choices, on_choice)
    dialog.open()
    Logger.debug(f"DialogHelper: Auswahl-Dialog geöffnet - '{title}' mit {len(choices)} Optionen")


# Spezielle Helper für häufige Dialog-Patterns

def show_cached_not_duplicatable_dialog(handicap_name):
    """
    Zeigt einen gecachten Dialog für nicht-duplizierbare Handicaps.

    Args:
        handicap_name (str): Name des Handicaps
    """
    message = (f"Das Handicap '{handicap_name}' kann nicht mehrfach ausgewählt werden.\n"
               "Handicaps der gleichen Art sind nur einmal pro Charakter möglich.")
    show_cached_info_dialog(
        title="Bereits ausgewählt",
        message=message,
        button_text="Verstanden"
    )


def show_cached_max_points_dialog():
    """Zeigt einen gecachten Dialog für maximale Handicap-Punkte."""
    message = ("Du hast bereits das Maximum von 4 Handicap-Punkten erreicht.\n"
               "Weitere Handicaps können nur gegen Aufstiege erworben werden.")
    show_cached_info_dialog(
        title="Maximum erreicht",
        message=message,
        button_text="Verstanden"
    )


def show_cached_no_advancement_dialog(kosten, char_name=""):
    """
    Zeigt einen gecachten Dialog für fehlende Aufstiege.

    Args:
        kosten (int): Benötigte Aufstiege
        char_name (str): Name des Charakters (optional)
    """
    char_info = f" {char_name}" if char_name else ""
    message = (f"Für diese Aktion werden {kosten} Aufstieg{'e' if kosten > 1 else ''} benötigt.\n"
               f"Charakter{char_info} hat nicht genügend Aufstiege verfügbar.")
    show_cached_info_dialog(
        title="Nicht genügend Aufstiege",
        message=message,
        button_text="Verstanden"
    )


def show_cached_remove_or_reduce_dialog(item_name, on_remove=None, on_reduce=None, on_cancel=None):
    """
    Zeigt einen gecachten Dialog zum Entfernen oder Reduzieren eines Elements.

    Args:
        item_name (str): Name des Elements
        on_remove (callable): Callback zum Entfernen
        on_reduce (callable): Callback zum Reduzieren
        on_cancel (callable): Callback zum Abbrechen
    """
    message = (f"Möchten Sie das Handicap '{item_name}' komplett entfernen oder nur reduzieren?\n\n"
               "Entfernen: Handicap wird komplett entfernt\n"
               "Reduzieren: Wandelt ein schweres Handicap in ein geringfügiges um")

    choices = [
        ("Entfernen", "remove"),
        ("Reduzieren", "reduce")
    ]

    def handle_choice(choice):
        if choice == "remove" and on_remove:
            on_remove()
        elif choice == "reduce" and on_reduce:
            on_reduce()
        elif on_cancel:
            on_cancel()

    show_cached_choice_dialog(
        title=f"{item_name} bearbeiten",
        message=message,
        choices=choices,
        on_choice=handle_choice
    )


def show_cached_pathfinder_kostenlos_dialog(talent_name, on_kostenlos=None, on_kosten=None, on_cancel=None):
    """
    Zeigt einen gecachten Dialog für kostenlose Pathfinder-Talente.

    Args:
        talent_name (str): Name des Talents
        on_kostenlos (callable): Callback für kostenlose Wahl
        on_kosten (callable): Callback für normale Kosten
        on_cancel (callable): Callback für Abbrechen
    """
    message = (f"Das Talent '{talent_name}' ist ein Klassen-, Hintergrund- oder Experte-Talent und kann in Savage Pathfinder "
               "während der Charaktererstellung kostenlos gewählt werden.\n\n"
               "Möchten Sie dieses Talent kostenlos wählen oder mit den normalen Kosten (2 Handicap-Punkte oder 1 Aufstieg)?")

    choices = [
        ("Kostenlos wählen", "kostenlos"),
        ("Normale Kosten", "kosten"),
        ("Abbrechen", "cancel")
    ]

    def handle_choice(choice):
        if choice == "kostenlos" and on_kostenlos:
            on_kostenlos()
        elif choice == "kosten" and on_kosten:
            on_kosten()
        elif choice == "cancel" and on_cancel:
            on_cancel()

    show_cached_choice_dialog(
        title="Kostenloses Pathfinder-Talent",
        message=message,
        choices=choices,
        on_choice=handle_choice
    )


def show_cached_transaction_dialog(title, message, action_text, on_action=None, on_cancel=None):
    """
    Zeigt einen gecachten Transaktions-Dialog.

    Args:
        title (str): Dialog-Titel
        message (str): Hauptnachricht
        action_text (str): Text des Aktions-Buttons
        on_action (callable): Callback für die Aktion
        on_cancel (callable): Callback für Abbrechen
    """
    show_cached_confirmation_dialog(
        title=title,
        message=message,
        confirm_text=action_text,
        cancel_text="Abbrechen",
        on_confirm=on_action,
        on_cancel=on_cancel
    )


# Cache-Management-Funktionen

def clear_dialog_cache():
    """Leert den Dialog-Cache (für Tests oder Aufräumen)."""
    cache = get_dialog_cache()
    cache.clear_cache()
    Logger.info("DialogCache über Helper geleert")


def get_dialog_cache_info():
    """
    Holt Informationen über den Dialog-Cache.

    Returns:
        dict: Cache-Statistiken
    """
    cache = get_dialog_cache()
    return cache.get_cache_info()


# Kompatibilitäts-Wrapper für bestehenden Code

class CachedDialogMixin:
    """
    Mixin-Klasse für bestehende Widgets, um gecachte Dialoge einfach zu integrieren.

    Beispiel-Verwendung:
    ```python
    class MyWidget(CachedDialogMixin, MDBoxLayout):
        def some_method(self):
            self.show_info_dialog("Titel", "Nachricht")
    ```
    """

    def show_info_dialog(self, title="Information", message="", button_text="OK", on_confirm=None):
        """Zeigt einen gecachten Info-Dialog."""
        show_cached_info_dialog(title, message, button_text, on_confirm)

    def show_confirmation_dialog(self, title="Bestätigung", message="",
                               confirm_text="Bestätigen", cancel_text="Abbrechen",
                               on_confirm=None, on_cancel=None):
        """Zeigt einen gecachten Bestätigungs-Dialog."""
        show_cached_confirmation_dialog(title, message, confirm_text, cancel_text, on_confirm, on_cancel)

    def show_choice_dialog(self, title="Auswahl", message="", choices=None, on_choice=None):
        """Zeigt einen gecachten Auswahl-Dialog."""
        show_cached_choice_dialog(title, message, choices, on_choice)

    def show_not_duplicatable_dialog(self, item_name):
        """Zeigt einen gecachten Dialog für nicht-duplizierbare Elemente."""
        show_cached_not_duplicatable_dialog(item_name)

    def show_max_points_dialog(self):
        """Zeigt einen gecachten Dialog für maximale Punkte."""
        show_cached_max_points_dialog()

    def show_no_advancement_dialog(self, kosten, char_name=""):
        """Zeigt einen gecachten Dialog für fehlende Aufstiege."""
        show_cached_no_advancement_dialog(kosten, char_name)