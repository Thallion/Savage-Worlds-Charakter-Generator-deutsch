# utils/custom_filemanager.py

from kivymd.uix.filemanager import MDFileManager
import os
import string
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText

class CustomFileManager(MDFileManager):
    """
    Benutzerdefinierter FileManager mit verbesserter Fehlerbehandlung und
    robuster Laufwerksanzeige.
    """
    
    def show_disks(self):
        """
        Zeigt verfügbare Laufwerke an, ohne problematische OS-Befehle zu verwenden.
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
        
        # Unix/Linux/MacOS Standardpfade
        else:
            Logger.debug("CustomFileManager: Zeige Unix/Linux-Pfade an")
            # Root-Verzeichnis
            manager_list.append({
                "viewclass": "MDListItem",
                "path": "/",
                "text": "/",
                "icon": "harddisk",
                "events_callback": self.select_directory_on_press_button
            })
            
            # Für Android: Speicher-Verzeichnis
            if os.path.exists("/storage"):
                manager_list.append({
                    "viewclass": "MDListItem",
                    "path": "/storage",
                    "text": "Storage",
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
            
            # Normaler Fall: Eine Ebene zurück
            new_path = os.path.dirname(self.current_path)
            if os.path.exists(new_path):
                self.show(new_path)
            else:
                # Pfad existiert nicht mehr, zur Laufwerksanzeige zurückkehren
                Logger.warning(f"Pfad nicht mehr verfügbar: {new_path}")
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