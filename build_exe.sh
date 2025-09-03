#!/bin/bash
# ===================================================================
# Savage Worlds Charakter Generator - Build Script
# Erstellt Windows EXE mit Wine und Linux Binary mit PyInstaller
# ===================================================================

set -e  # Bei Fehlern beenden

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji für bessere Lesbarkeit
WINE_EMOJI="🍷"
LINUX_EMOJI="🐧" 
SUCCESS_EMOJI="✅"
ERROR_EMOJI="❌"
CLEAN_EMOJI="🧹"
BUILD_EMOJI="🔨"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

print_header() {
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${CYAN} Savage Worlds Generator - Build Script${NC}"
    echo -e "${CYAN}=================================================${NC}"
}

print_step() {
    echo -e "\n${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}${SUCCESS_EMOJI} $1${NC}"
}

print_error() {
    echo -e "${RED}${ERROR_EMOJI} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

cleanup_build_files() {
    print_step "${CLEAN_EMOJI} Bereinige Build-Artefakte..."
    
    # Temporäre spec-Dateien löschen
    rm -f wine_simple.spec wine_fixed.spec 2>/dev/null || true
    
    # Build-Verzeichnis bereinigen
    if [ -d "build" ]; then
        rm -rf build
        print_success "Build-Verzeichnis bereinigt"
    fi
    
    # __pycache__ bereinigen
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # .pyc Dateien löschen
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Build-Artefakte bereinigt"
}

check_wine() {
    print_step "🔍 Prüfe Wine-Installation..."
    
    if ! command -v wine &> /dev/null; then
        print_error "Wine nicht gefunden! Installiere mit: sudo apt install wine"
        return 1
    fi
    
    # Prüfe Python in Wine
    if ! wine python --version &> /dev/null; then
        print_error "Python nicht in Wine installiert!"
        print_warning "Installiere Python für Windows in Wine"
        return 1
    fi
    
    # Prüfe PyInstaller in Wine  
    if ! wine python -m PyInstaller --version &> /dev/null; then
        print_error "PyInstaller nicht in Wine installiert!"
        print_warning "Installiere mit: wine python -m pip install pyinstaller"
        return 1
    fi
    
    print_success "Wine-Umgebung bereit"
    return 0
}

build_wine_exe() {
    print_step "${WINE_EMOJI} Baue Windows EXE mit Wine..."
    
    # Basierend auf dem funktionierenden savage_worlds_generator.spec
    cat > wine_build_temp.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Bestimme das Projektverzeichnis
project_dir = Path.cwd()

# Sammle alle Daten-Dateien (EXAKT wie im originalen savage_worlds_generator.spec)
datas = [
    # Assets Ordner
    (str(project_dir / 'assets'), 'assets'),
    
    # Config Dateien
    (str(project_dir / 'config'), 'config'),
    
    # Settings Dateien
    (str(project_dir / 'settings'), 'settings'),
    
    # Templates
    (str(project_dir / 'templates'), 'templates'),
    
    # Views (KV-Dateien) - WICHTIG für pointbar_view.kv!
    (str(project_dir / 'views'), 'views'),
    
    # Chars Ordner
    (str(project_dir / 'chars'), 'chars'),
    
    # Main KV-Datei
    (str(project_dir / 'main.kv'), '.'),
    
    # KivyMD Daten
    ('venv/lib/python3.12/site-packages/kivymd', 'kivymd') if os.path.exists('venv/lib/python3.12/site-packages/kivymd') else None,
]

# Filtere None-Werte heraus
datas = [item for item in datas if item is not None]

# Hidden imports (EXAKT wie im originalen savage_worlds_generator.spec)
hiddenimports = [
    'kivymd',
    'kivymd.app',
    'kivymd.uix.screen',
    'kivymd.uix.boxlayout',
    'kivymd.uix.label',
    'kivymd.uix.button',
    'kivymd.uix.textfield',
    'kivymd.uix.tab',
    'kivymd.theming',
    'kivy',
    'kivy.app',
    'kivy.lang',
    'kivy.clock',
    'kivy.properties',
    'kivy.core.window',
    'kivy.logger',
    'kivy.metrics',
    'kivy.uix.popup',
    'kivy.uix.scrollview',
    'kivy.uix.widget',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'json',
    'logging',
    'functools',
    'webbrowser',
    're',
    'sys',
    'os'
]

# Module die oft False-Positives auslösen ausschließen
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',
    'tornado',
    'zmq',
    'sqlite3',
    'distutils',
    'setuptools',
    'pip',
    'wheel'
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SavageWorldsCharakterGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX oft False-Positive Auslöser
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Für GUI-Anwendung auf False setzen
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
    icon=str(project_dir / 'assets' / 'bowman.png') if (project_dir / 'assets' / 'bowman.png').exists() else None,
)
EOF

    # Wine Build ausführen
    print_step "Starte Wine PyInstaller..."
    
    # Kivy-Config für Wine setzen - Mock GL für bessere Kompatibilität
    export KIVY_NO_CONFIG=1
    export KIVY_WINDOW=sdl2
    export KIVY_GL_BACKEND=mock
    export USE_OPENGL_MOCK=1
    
    if WINEDEBUG=-all wine python -m PyInstaller --clean --noconfirm wine_build_temp.spec; then
        # Prüfe Ergebnis
        if [ -f "dist/SavageWorldsCharakterGenerator.exe" ]; then
            local size_mb=$(du -m "dist/SavageWorldsCharakterGenerator.exe" | cut -f1)
            print_success "Windows EXE erstellt (${size_mb} MB)"
            
            # Backup mit Timestamp
            cp "dist/SavageWorldsCharakterGenerator.exe" "dist/SavageWorldsCharakterGenerator_${TIMESTAMP}.exe" 2>/dev/null || true
        else
            print_error "Windows EXE nicht gefunden!"
            return 1
        fi
    else
        print_error "Wine Build fehlgeschlagen!"
        return 1
    fi
    
    # Temporäre spec löschen
    rm -f wine_build_temp.spec
    
    return 0
}

build_linux_binary() {
    print_step "${LINUX_EMOJI} Baue Linux Binary..."
    
    # Virtuelle Umgebung aktivieren falls vorhanden
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_success "Virtuelle Umgebung aktiviert"
    fi
    
    # Native Linux Build
    if python -m PyInstaller --clean --noconfirm savage_worlds_generator.spec; then
        # Prüfe Ergebnis
        if [ -f "dist/SavageWorldsCharakterGenerator" ]; then
            local size_mb=$(du -m "dist/SavageWorldsCharakterGenerator" | cut -f1)
            print_success "Linux Binary erstellt (${size_mb} MB)"
            
            # Backup mit Timestamp
            cp "dist/SavageWorldsCharakterGenerator" "dist/SavageWorldsCharakterGenerator_${TIMESTAMP}" 2>/dev/null || true
        else
            print_error "Linux Binary nicht gefunden!"
            return 1
        fi
    else
        print_error "Linux Build fehlgeschlagen!"
        return 1
    fi
    
    return 0
}

show_results() {
    print_step "📋 Build-Ergebnisse:"
    
    if [ -f "dist/SavageWorldsCharakterGenerator.exe" ]; then
        local exe_size=$(du -h "dist/SavageWorldsCharakterGenerator.exe" | cut -f1)
        echo -e "${GREEN}${WINE_EMOJI} Windows EXE: ${exe_size}${NC}"
        echo -e "   📍 dist/SavageWorldsCharakterGenerator.exe"
    fi
    
    if [ -f "dist/SavageWorldsCharakterGenerator" ]; then
        local bin_size=$(du -h "dist/SavageWorldsCharakterGenerator" | cut -f1)
        echo -e "${GREEN}${LINUX_EMOJI} Linux Binary: ${bin_size}${NC}"
        echo -e "   📍 dist/SavageWorldsCharakterGenerator"
    fi
    
    echo -e "\n${CYAN}💡 Nächste Schritte:${NC}"
    echo -e "   1. EXE auf Windows-System testen"
    echo -e "   2. VirusTotal Upload (virustotal.com)" 
    echo -e "   3. GitHub Release erstellen"
}

main() {
    cd "$PROJECT_DIR"
    
    print_header
    
    # Parse Argumente
    BUILD_WINE=true
    BUILD_LINUX=true
    
    case "${1:-both}" in
        "wine"|"windows")
            BUILD_LINUX=false
            print_step "Nur Windows EXE wird erstellt"
            ;;
        "linux"|"native")
            BUILD_WINE=false
            print_step "Nur Linux Binary wird erstellt"
            ;;
        "both"|"")
            print_step "Windows EXE und Linux Binary werden erstellt"
            ;;
        *)
            echo "Usage: $0 [wine|linux|both]"
            exit 1
            ;;
    esac
    
    # Bereinigung
    cleanup_build_files
    
    # Builds
    if [ "$BUILD_WINE" = true ]; then
        if check_wine && build_wine_exe; then
            print_success "Windows EXE erfolgreich erstellt"
        else
            print_error "Windows EXE Build fehlgeschlagen"
            exit 1
        fi
    fi
    
    if [ "$BUILD_LINUX" = true ]; then
        if build_linux_binary; then
            print_success "Linux Binary erfolgreich erstellt"
        else
            print_error "Linux Binary Build fehlgeschlagen"
            exit 1
        fi
    fi
    
    # Finale Bereinigung
    cleanup_build_files
    
    # Ergebnisse zeigen
    show_results
    
    print_success "Build abgeschlossen! ${SUCCESS_EMOJI}"
}

# Script ausführen
main "$@"