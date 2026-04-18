#!/usr/bin/env python3
"""
Script zum Reparieren der Builder.load_file() Pfade für PyInstaller
Ersetzt relative Pfade durch path_utils-basierte Pfade
"""

import os
import re
from pathlib import Path

def fix_builder_paths():
    """Repariert alle Builder.load_file() Pfade in den View-Dateien"""
    
    project_root = Path.cwd()
    views_dir = project_root / "views"
    
    if not views_dir.exists():
        print(f"❌ Views-Verzeichnis nicht gefunden: {views_dir}")
        return False
    
    # Pattern für Builder.load_file() mit relativen Pfaden
    pattern = r"Builder\.load_file\(['\"]views/([^'\"]+\.kv)['\"]\)"
    replacement_template = """# KV-Datei laden mit PyInstaller-kompatiblem Pfad
from utils.path_utils import get_application_root
import os
kv_path = os.path.join(get_application_root(), 'views', '{kv_file}')
Builder.load_file(kv_path)"""
    
    fixed_files = []
    
    # Durchsuche alle Python-Dateien im views-Verzeichnis
    for py_file in views_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        print(f"🔍 Prüfe {py_file.name}...")
        
        try:
            # Datei lesen
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Suche nach Builder.load_file() Aufrufen
            matches = re.findall(pattern, content)
            
            if matches:
                print(f"  📝 Gefunden: {len(matches)} Builder.load_file() Aufrufe")
                
                # Prüfe ob bereits path_utils importiert sind
                has_path_utils_import = 'from utils.path_utils import get_application_root' in content
                has_os_import = 'import os' in content and not content.startswith('import os\n')
                
                for kv_file in matches:
                    old_call = f"Builder.load_file('views/{kv_file}')"
                    
                    if has_path_utils_import:
                        # Nur den Builder-Aufruf ersetzen
                        new_call = f"""kv_path = os.path.join(get_application_root(), 'views', '{kv_file}')
Builder.load_file(kv_path)"""
                    else:
                        # Vollständigen Ersatz mit Imports
                        new_call = replacement_template.format(kv_file=kv_file)
                    
                    content = content.replace(old_call, new_call)
                    print(f"  ✅ Ersetzt: views/{kv_file}")
                
                # Datei zurückschreiben
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files.append(py_file.name)
            else:
                print(f"  ⏭️  Keine Änderungen nötig")
                
        except Exception as e:
            print(f"  ❌ Fehler bei {py_file.name}: {e}")
            continue
    
    print(f"\n📊 Zusammenfassung:")
    print(f"  Reparierte Dateien: {len(fixed_files)}")
    for file in fixed_files:
        print(f"    ✅ {file}")
    
    return len(fixed_files) > 0

if __name__ == "__main__":
    print("🔧 Repariere PyInstaller Builder.load_file() Pfade...")
    success = fix_builder_paths()
    
    if success:
        print("\n🎉 Erfolgreich abgeschlossen!")
        print("Die View-Dateien verwenden jetzt PyInstaller-kompatible Pfade")
    else:
        print("\n💥 Keine Dateien repariert oder Fehler aufgetreten")