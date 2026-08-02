#!/usr/bin/env python3
"""
Script zur Erstellung einer version_info.txt Datei für PyInstaller
um Virenscanner-False-Positives zu reduzieren
"""

import os
from pathlib import Path

# Version Info Template für Windows Executables
version_info_template = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers und prodvers sollten immer 4-Tupel sein, auch wenn sie 0 sind
    filevers=(0,8,2,7),
    prodvers=(0,8,2,7),
# Enthält eine Bitmaske, die verschiedene Attribute der Datei angibt  
    mask=0x3f,
# Enthält eine Bitmaske, die den gültigen Bits in fileflags entspricht
    flags=0x0,
# Das Betriebssystem, für das diese Datei erstellt wurde
    OS=0x40004,  # VOS_NT_WINDOWS32
# Der allgemeine Dateityp
    fileType=0x1,  # VFT_APP
# Die Funktion der Datei
    subtype=0x0,
# Datum und Uhrzeit der Erstellung der Datei
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Jean-Michel Fenske'),
        StringStruct(u'FileDescription', u'Savage Worlds Charakter Generator - Ein Tool zur Erstellung und Verwaltung von Charakteren für das Savage Worlds Rollenspielsystem'),
        StringStruct(u'FileVersion', u'0.8.2.7'),
        StringStruct(u'InternalName', u'SavageWorldsCharakterGenerator'),
        StringStruct(u'LegalCopyright', u'© 2024 Jean-Michel Fenske - Open Source (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)'),
        StringStruct(u'OriginalFilename', u'SavageWorldsCharakterGenerator.exe'),
        StringStruct(u'ProductName', u'Savage Worlds Charakter Generator'),
        StringStruct(u'ProductVersion', u'0.8.2.7'),
        StringStruct(u'Comments', u'Erstellt mit Python und Kivy/KivyMD - https://github.com/Thallion/Savage-Worlds-Charakter-Generator-deutsch'),
        StringStruct(u'LegalTrademarks', u'Savage Worlds ist ein eingetragenes Warenzeichen von Pinnacle Entertainment Group')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

def create_version_info():
    """Erstelle die version_info.txt Datei"""
    version_info_path = Path('version_info.txt')
    
    print("Erstelle version_info.txt für PyInstaller...")
    
    try:
        with open(version_info_path, 'w', encoding='utf-8') as f:
            f.write(version_info_template)
        
        print(f"✓ version_info.txt erfolgreich erstellt: {version_info_path.absolute()}")
        print("Diese Datei kann in der PyInstaller .spec Datei verwendet werden.")
        
    except Exception as e:
        print(f"✗ Fehler beim Erstellen der version_info.txt: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_version_info()