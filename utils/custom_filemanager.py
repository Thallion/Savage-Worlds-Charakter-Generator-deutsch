# utils/custom_filemanager.py

from kivymd.uix.filemanager import MDFileManager
import os
import string
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import platform
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText

class CustomFileManager(MDFileManager):
    """
    Benutzerdefinierter FileManager mit verbesserter Fehlerbehandlung und
    robuster Laufwerksanzeige.
    Android: Schnellzugriff auf gängige Verzeichnisse statt nur / und /storage.
    """

    def _get_android_paths(self):
        """
        Ermittelt verfügbare Android-Verzeichnisse mit Schnellzugriffen.
        Gibt Liste von (pfad, anzeige_name, icon) Tupeln zurück.
        """
        paths = []

        # Interner Speicher (primärer Zugriffspunkt für Nutzer)
        internal = "/storage/emulated/0"
        if os.path.exists(internal) and os.access(internal, os.R_OK):
            paths.append((internal, "Interner Speicher", "cellphone"))

        # Häufig genutzte Unterverzeichnisse
        quick_dirs = [
            ("Download", "Downloads", "download"),
            ("Documents", "Dokumente", "file-document"),
            ("DCIM", "Kamera (DCIM)", "camera"),
            ("Pictures", "Bilder", "image"),
            ("Music", "Musik", "music"),
        ]
        for subdir, label, icon in quick_dirs:
            full = os.path.join(internal, subdir)
            if os.path.exists(full) and os.access(full, os.R_OK):
                paths.append((full, label, icon))

        # App-eigenes Verzeichnis (SavageWorldsCharGen)
        app_dir = os.path.join(internal, "SavageWorldsCharGen")
        if os.path.exists(app_dir) and os.access(app_dir, os.R_OK):
            paths.append((app_dir, "SW CharGen Daten", "sword-cross"))

        # Externe SD-Karte suchen
        storage_dir = "/storage"
        if os.path.exists(storage_dir):
            try:
                for entry in os.listdir(storage_dir):
                    # Überspringe den internen Speicher-Symlink
                    if entry in ("emulated", "self"):
                        continue
                    sd_path = os.path.join(storage_dir, entry)
                    if os.path.isdir(sd_path) and os.access(sd_path, os.R_OK):
                        paths.append((sd_path, f"SD-Karte ({entry})", "sd"))
            except PermissionError:
                Logger.warning("CustomFileManager: Kein Zugriff auf /storage")

        # App-privates Verzeichnis (immer zugreifbar, auch ohne Berechtigungen)
        try:
            from android.storage import app_storage_path  # noqa: F401
            private_path = app_storage_path()
            if os.path.exists(private_path):
                paths.append((private_path, "App-Verzeichnis (privat)", "lock"))
        except ImportError:
            # Fallback: Versuche typischen privaten Pfad
            private_candidates = [
                "/data/data/org.test.savageworlds/files",
                os.path.expanduser("~"),
            ]
            for p in private_candidates:
                if os.path.exists(p) and os.access(p, os.R_OK):
                    paths.append((p, "App-Verzeichnis", "lock"))
                    break

        # Storage root als letzten Fallback
        if os.path.exists(storage_dir) and os.access(storage_dir, os.R_OK):
            paths.append((storage_dir, "Storage (alle)", "harddisk"))

        # Root nur als absoluten Notfall
        paths.append(("/", "Dateisystem (/)", "folder-network"))

        return paths

    def show_disks(self):
        """
        Zeigt verfügbare Laufwerke/Schnellzugriffe an.
        Android: Gängige Verzeichnisse statt nur / und /storage.
        """
        # Setze den aktuellen Pfad zurück
        self.current_path = ""

        # Manager-Liste für die RecycleView vorbereiten
        manager_list = []

        # Windows Laufwerke identifizieren
        if os.name == 'nt':
            Logger.debug("CustomFileManager: Zeige Windows-Laufwerke an")
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    manager_list.append({
                        "viewclass": "MDListItem",
                        "path": drive,
                        "text": f"{letter}:",
                        "icon": "harddisk",
                        "events_callback": self.select_directory_on_press_button
                    })

        # Android: Schnellzugriffspfade
        elif platform == 'android':
            Logger.debug("CustomFileManager: Zeige Android-Schnellzugriffe an")
            for path, label, icon in self._get_android_paths():
                manager_list.append({
                    "viewclass": "MDListItem",
                    "path": path,
                    "text": label,
                    "icon": icon,
                    "events_callback": self.select_directory_on_press_button
                })

        # Unix/Linux/MacOS Standardpfade
        else:
            Logger.debug("CustomFileManager: Zeige Unix/Linux-Pfade an")
            # Home-Verzeichnis
            home_dir = os.path.expanduser("~")
            if os.path.exists(home_dir):
                manager_list.append({
                    "viewclass": "MDListItem",
                    "path": home_dir,
                    "text": "Home",
                    "icon": "home",
                    "events_callback": self.select_directory_on_press_button
                })

            # Root-Verzeichnis
            manager_list.append({
                "viewclass": "MDListItem",
                "path": "/",
                "text": "/",
                "icon": "harddisk",
                "events_callback": self.select_directory_on_press_button
            })

        # Daten für RecycleView bereitstellen
        self.ids.rv.data = manager_list

        # Historie zurücksetzen
        self.history = []

    def back(self):
        """
        Überschriebene back()-Methode mit verbesserter Fehlerbehandlung.
        Verhindert Abstürze durch wiederholtes Zurückgehen.
        """
        try:
            if not self.current_path:
                # Bereits auf Laufwerksebene, einfach schließen
                self.close()
                return

            # Aktuelle Pfadkomponenten
            path_components = self.current_path.split(os.sep)

            # Prüfen, ob wir bereits im Root sind
            if len(path_components) <= 1 or self.current_path == os.path.expanduser("~"):
                # Bei Root/Home: Laufwerksanzeige oder Schließen
                Logger.debug("FileManager: Wurzel erreicht, zeige Laufwerke an")
                self.show_disks()
                return

            # Android: Bei Schnellzugriffspfaden zurück zur Übersicht
            if platform == 'android':
                android_roots = ["/storage/emulated/0", "/storage"]
                if self.current_path in android_roots:
                    self.show_disks()
                    return

            # Normaler Fall: Eine Ebene zurück
            new_path = os.path.dirname(self.current_path)
            if os.path.exists(new_path) and os.access(new_path, os.R_OK):
                self.show(new_path)
            else:
                # Pfad existiert nicht mehr oder kein Zugriff
                Logger.warning(f"Pfad nicht verfügbar: {new_path}")
                self.show_disks()

        except Exception as e:
            # Bei Fehlern zur Laufwerksanzeige zurückkehren
            Logger.error(f"Fehler bei FileManager.back(): {str(e)}")
            try:
                self.show_disks()
            except Exception as e2:
                # Wenn selbst show_disks fehlschlägt, schließen
                Logger.error(f"Kritischer Fehler: {str(e2)}")
                self.close()


# Definition der ViewAdapter-Klasse hinzufügen
class ListItemViewAdapter:
    """Adapter, der ViewClass für MDListItem-Einträge in der RecycleView handhabt"""

    @staticmethod
    def get_view(recycleview, index, item_data):
        """Erstellt ein MDListItem basierend auf den übergebenen Daten"""
        item = MDListItem()
        item.path = item_data.get("path", "")
        item.events_callback = item_data.get("events_callback")

        # Icon hinzufügen
        item.add_widget(MDListItemLeadingIcon(icon=item_data.get("icon", "folder")))

        # Text hinzufügen
        item.add_widget(MDListItemHeadlineText(text=item_data.get("text", "")))

        def on_release(instance):
            if item.events_callback and callable(item.events_callback):
                item.events_callback(item.path)

        item.on_release = on_release
        return item

# Am Ende der CustomFileManager-Klasse hinzufügen
def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # ViewAdapter für MDListItem registrieren
    self.ids.rv.viewclass = "MDListItem"
    self.ids.rv.view_adapter = ListItemViewAdapter()
