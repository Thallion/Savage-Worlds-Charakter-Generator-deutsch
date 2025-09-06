#!/bin/bash
# ===================================================================
# Savage Worlds Charakter Generator - PyInstaller Windows Build
# Erstellt Windows EXE mit Wine + PyInstaller (stabilere Alternative zu Nuitka)
# ===================================================================

set -e  # Bei Fehlern beenden

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji
SUCCESS_EMOJI="✅"
ERROR_EMOJI="❌"
BUILD_EMOJI="🔨"
WINE_EMOJI="🍷"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

print_header() {
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${CYAN} Savage Worlds Generator - PyInstaller Windows Build${NC}"
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

check_wine() {
    print_step "🍷 Prüfe Wine-Installation..."
    
    if ! command -v wine &> /dev/null; then
        print_error "Wine nicht gefunden! Installiere mit: sudo apt install wine"
        return 1
    fi
    
    if ! wine python --version &> /dev/null; then
        print_error "Python nicht in Wine installiert!"
        return 1
    fi
    
    print_success "Wine und Python gefunden"
    return 0
}

install_pyinstaller_wine() {
    print_step "📦 Installiere PyInstaller in Wine..."
    
    if ! wine python -c "import PyInstaller" &> /dev/null; then
        print_step "Installiere PyInstaller in Wine..."
        wine python -m pip install pyinstaller
    fi
    
    print_success "PyInstaller in Wine verfügbar"
}

build_windows_exe() {
    print_step "${WINE_EMOJI} Baue Windows EXE mit Wine + PyInstaller..."
    
    # PyInstaller Kommando für Windows
    local pyinstaller_cmd=(
        wine python -m PyInstaller
        --onefile
        --windowed
        --name=SavageWorldsCharakterGenerator_wine
        --icon=assets/Savage-Worlds-Fanprodukt-Logo.png
        --add-data="assets;assets"
        --add-data="config;config"  
        --add-data="settings;settings"
        --add-data="templates;templates"
        --add-data="views;views"
        --add-data="chars;chars"
        --add-data="main.kv;."
        --hidden-import=kivymd
        --hidden-import=kivymd.app
        --hidden-import=kivymd.uix.boxlayout
        --hidden-import=kivymd.uix.tab
        --hidden-import=reportlab
        --hidden-import=reportlab.pdfgen
        --hidden-import=PIL
        --hidden-import=requests
        --collect-all=kivymd
        --collect-all=kivy
        main.py
    )
    
    print_step "Starte PyInstaller Windows Build..."
    echo -e "${YELLOW}Kommando: ${pyinstaller_cmd[*]}${NC}"
    
    if WINEDEBUG=-all "${pyinstaller_cmd[@]}"; then
        if [ -f "dist/SavageWorldsCharakterGenerator_wine.exe" ]; then
            local size_mb=$(du -m "dist/SavageWorldsCharakterGenerator_wine.exe" | cut -f1)
            print_success "Windows EXE mit PyInstaller erstellt (${size_mb} MB)"
            
            # Backup mit Timestamp
            cp "dist/SavageWorldsCharakterGenerator_wine.exe" "dist/SavageWorldsCharakterGenerator_pyinstaller_${TIMESTAMP}.exe" 2>/dev/null || true
        else
            print_error "Windows EXE nicht gefunden!"
            return 1
        fi
    else
        print_error "PyInstaller Build fehlgeschlagen!"
        return 1
    fi
    
    return 0
}

cleanup_pyinstaller_files() {
    print_step "🧹 Bereinige PyInstaller-Artefakte..."
    
    # PyInstaller Build-Verzeichnisse
    rm -rf build/ *.spec 2>/dev/null || true
    
    # __pycache__ bereinigen
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "PyInstaller-Artefakte bereinigt"
}

show_results() {
    print_step "📋 Build-Ergebnisse:"
    
    if [ -f "dist/SavageWorldsCharakterGenerator_wine.exe" ]; then
        local exe_size=$(du -h "dist/SavageWorldsCharakterGenerator_wine.exe" | cut -f1)
        echo -e "${GREEN}${WINE_EMOJI} PyInstaller Windows EXE: ${exe_size}${NC}"
        echo -e "   📍 dist/SavageWorldsCharakterGenerator_wine.exe"
    fi
    
    echo -e "\n${CYAN}💡 Vorteile von PyInstaller:${NC}"
    echo -e "   ✓ Bewährte und stabile Windows-Builds"
    echo -e "   ✓ Bessere Wine-Kompatibilität als Nuitka"
    echo -e "   ✓ Zuverlässige Dependency-Erkennung"
    echo -e "   ✓ Weniger komplexe Build-Pipeline"
}

main() {
    cd "$PROJECT_DIR"
    
    print_header
    
    # Wine prüfen
    if ! check_wine; then
        exit 1
    fi
    
    # PyInstaller installieren
    install_pyinstaller_wine
    
    # Bereinigung vor Build
    cleanup_pyinstaller_files
    
    # Windows EXE Build
    if build_windows_exe; then
        print_success "PyInstaller Windows Build erfolgreich"
    else
        print_error "PyInstaller Windows Build fehlgeschlagen"
        exit 1
    fi
    
    # Finale Bereinigung
    cleanup_pyinstaller_files
    
    # Ergebnisse zeigen
    show_results
    
    print_success "PyInstaller Windows Build abgeschlossen! ${SUCCESS_EMOJI}"
}

# Script ausführen
main "$@"