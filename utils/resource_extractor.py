"""
Resource Extractor für PyInstaller EXE
Extrahiert chars, templates, settings und assets vom _MEIPASS in das EXE-Verzeichnis
"""
import sys
import os
import shutil
import json
from pathlib import Path
from kivy.logger import Logger

class ResourceExtractor:
    """Extrahiert Ressourcen aus PyInstaller temp folder in EXE directory"""
    
    def __init__(self):
        self.exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else None
        self.temp_dir = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS') else None
        self.extracted_marker = self.exe_dir / '.resources_extracted' if self.exe_dir else None
        
    def is_pyinstaller_exe(self) -> bool:
        """Prüft ob die App als PyInstaller EXE läuft"""
        return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    def resources_already_extracted(self) -> bool:
        """Prüft ob Ressourcen bereits extrahiert wurden"""
        if not self.extracted_marker:
            return False
        return self.extracted_marker.exists()
    
    def extract_resources(self) -> bool:
        """
        Extrahiert alle Ressourcen vom temp folder ins EXE directory
        
        Returns:
            bool: True wenn erfolgreich extrahiert oder bereits vorhanden
        """
        if not self.is_pyinstaller_exe():
            Logger.info("ResourceExtractor: Nicht in PyInstaller EXE - keine Extraktion nötig")
            return True
            
        if self.resources_already_extracted():
            Logger.info("ResourceExtractor: Ressourcen bereits extrahiert - überspringe")
            return True
            
        Logger.info("ResourceExtractor: Starte Ressourcen-Extraktion...")
        
        try:
            # Definiere Verzeichnisse die extrahiert werden sollen
            directories_to_extract = [
                'settings',
                'templates', 
                'chars',
                'assets',
                'config'
            ]
            
            extracted_count = 0
            
            for dir_name in directories_to_extract:
                source_path = self.temp_dir / dir_name
                target_path = self.exe_dir / dir_name
                
                if source_path.exists():
                    Logger.info(f"ResourceExtractor: Extrahiere {dir_name}...")
                    
                    # Zielverzeichnis erstellen wenn nicht vorhanden
                    target_path.mkdir(parents=True, exist_ok=True)
                    
                    # Alle Dateien kopieren
                    for item in source_path.rglob('*'):
                        if item.is_file():
                            # Relative Pfad berechnen
                            rel_path = item.relative_to(source_path)
                            target_file = target_path / rel_path
                            
                            # Zielverzeichnis erstellen
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Datei kopieren (überschreibe nur wenn Quelle neuer ist)
                            if not target_file.exists() or item.stat().st_mtime > target_file.stat().st_mtime:
                                shutil.copy2(item, target_file)
                                extracted_count += 1
                    
                    Logger.info(f"ResourceExtractor: {dir_name} erfolgreich extrahiert")
                else:
                    Logger.warning(f"ResourceExtractor: {dir_name} nicht in temp folder gefunden")
            
            # Marker-Datei erstellen mit Metadaten
            self._create_extraction_marker(extracted_count)
            
            Logger.info(f"ResourceExtractor: Extraktion abgeschlossen - {extracted_count} Dateien extrahiert")
            return True
            
        except Exception as e:
            Logger.error(f"ResourceExtractor: Fehler beim Extrahieren: {str(e)}")
            return False
    
    def _create_extraction_marker(self, file_count: int):
        """Erstellt Marker-Datei mit Extraktions-Metadaten"""
        marker_data = {
            'extracted_at': str(Path.cwd()),
            'file_count': file_count,
            'version': '1.0',
            'temp_path': str(self.temp_dir) if self.temp_dir else None
        }
        
        try:
            with open(self.extracted_marker, 'w', encoding='utf-8') as f:
                json.dump(marker_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            Logger.error(f"ResourceExtractor: Fehler beim Erstellen der Marker-Datei: {str(e)}")
    
    def force_re_extract(self):
        """Erzwingt Neu-Extraktion durch Löschen der Marker-Datei"""
        if self.extracted_marker and self.extracted_marker.exists():
            self.extracted_marker.unlink()
            Logger.info("ResourceExtractor: Marker-Datei gelöscht - nächster Start wird Ressourcen neu extrahieren")
    
    def get_extraction_info(self) -> dict:
        """Gibt Informationen über die letzte Extraktion zurück"""
        if not self.extracted_marker or not self.extracted_marker.exists():
            return {}
        
        try:
            with open(self.extracted_marker, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

# Globale Instanz für einfache Nutzung
resource_extractor = ResourceExtractor()