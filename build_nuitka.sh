#!/bin/bash
# ===================================================================
# Savage Worlds Charakter Generator - Nuitka Build Script
# Erstellt Windows EXE mit Nuitka (weniger False-Positives)
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
NUITKA_EMOJI="⚡"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

print_header() {
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${CYAN} Savage Worlds Generator - Nuitka Build${NC}"
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

check_nuitka() {
    print_step "🔍 Prüfe Nuitka-Installation..."
    
    if ! python -c "import nuitka" &> /dev/null; then
        print_error "Nuitka nicht gefunden! Installiere mit: pip install nuitka"
        return 1
    fi
    
    local nuitka_version=$(python -c "import nuitka; print(nuitka.__version__)")
    print_success "Nuitka ${nuitka_version} gefunden"
    return 0
}

check_patchelf() {
    print_step "🔧 Prüfe patchelf-Installation..."
    
    if ! command -v patchelf &> /dev/null; then
        print_warning "patchelf nicht gefunden - installiere..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y patchelf
        elif command -v pacman &> /dev/null; then
            sudo pacman -S patchelf
        elif command -v dnf &> /dev/null; then
            sudo dnf install patchelf
        else
            print_error "Paketmanager nicht unterstützt. Installiere patchelf manuell."
            return 1
        fi
    fi
    
    if command -v patchelf &> /dev/null; then
        local patchelf_version=$(patchelf --version 2>&1 | head -n1)
        print_success "patchelf gefunden: ${patchelf_version}"
        return 0
    else
        print_error "patchelf-Installation fehlgeschlagen"
        return 1
    fi
}

cleanup_nuitka_files() {
    print_step "🧹 Bereinige Nuitka-Artefakte..."
    
    # Nuitka Build-Verzeichnisse
    rm -rf main.build main.dist main.onefile-build 2>/dev/null || true
    rm -rf SavageWorldsCharakterGenerator.build SavageWorldsCharakterGenerator.dist 2>/dev/null || true
    
    # __pycache__ bereinigen
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Nuitka-Artefakte bereinigt"
}

build_nuitka_exe() {
    print_step "${NUITKA_EMOJI} Baue Linux Binary mit Nuitka..."
    
    # Nuitka Build-Kommando für Linux
    local nuitka_cmd=(
        python -m nuitka
        --standalone
        --assume-yes-for-downloads
        --output-dir=dist
        --output-filename=SavageWorldsCharakterGenerator
        --include-data-dir=assets=assets
        --include-data-dir=config=config
        --include-data-dir=settings=settings
        --include-data-dir=templates=templates
        --include-data-dir=views=views
        --include-data-dir=chars=chars
        --include-data-file=main.kv=main.kv
        --plugin-enable=kivy
        --follow-imports
        --follow-import-to=kivymd
        --follow-import-to=reportlab
        --follow-import-to=requests
        --follow-import-to=PIL
        --nofollow-import-to=matplotlib
        --nofollow-import-to=numpy
        --nofollow-import-to=scipy
        --nofollow-import-to=tkinter
        --nofollow-import-to=sqlite3
        --remove-output
        --jobs=4
        main.py
    )
    
    print_step "Starte Nuitka Build..."
    echo -e "${YELLOW}Kommando: ${nuitka_cmd[*]}${NC}"
    
    if "${nuitka_cmd[@]}"; then
        # Prüfe Ergebnis (jetzt in dist/ Verzeichnis)
        if [ -f "dist/SavageWorldsCharakterGenerator" ]; then
            local size_mb=$(du -m "dist/SavageWorldsCharakterGenerator" | cut -f1)
            print_success "Linux Standalone mit Nuitka erstellt (${size_mb} MB)"
            
            # patchelf-Optimierung anwenden
            apply_patchelf_optimizations "dist/SavageWorldsCharakterGenerator"
            
            # Backup mit Timestamp
            cp "dist/SavageWorldsCharakterGenerator" "dist/SavageWorldsCharakterGenerator_standalone_${TIMESTAMP}" 2>/dev/null || true
        else
            print_error "Linux Binary nicht gefunden!"
            return 1
        fi
    else
        print_error "Nuitka Build fehlgeschlagen!"
        return 1
    fi
    
    return 0
}

apply_patchelf_optimizations() {
    local binary_file="$1"
    print_step "🔧 Wende patchelf-Optimierungen an..."
    
    if [ ! -f "$binary_file" ]; then
        print_error "Binary-Datei nicht gefunden: $binary_file"
        return 1
    fi
    
    # Prüfe aktuelle RPATH
    local current_rpath=$(patchelf --print-rpath "$binary_file" 2>/dev/null || echo "")
    print_step "Aktuelle RPATH: ${current_rpath:-'(leer)'}"
    
    # Setze optimierte RPATH für bessere Portabilität
    patchelf --set-rpath '$ORIGIN:$ORIGIN/lib:/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu' "$binary_file" 2>/dev/null || {
        print_warning "RPATH-Setzung fehlgeschlagen (möglicherweise nicht nötig)"
    }
    
    # Prüfe Interpreter
    local interpreter=$(patchelf --print-interpreter "$binary_file" 2>/dev/null || echo "")
    if [ -n "$interpreter" ]; then
        print_step "Aktueller Interpreter: $interpreter"
        
        # Versuche Standard-Interpreter zu setzen für bessere Kompatibilität
        local standard_interpreter="/lib64/ld-linux-x86-64.so.2"
        if [ -f "$standard_interpreter" ]; then
            patchelf --set-interpreter "$standard_interpreter" "$binary_file" 2>/dev/null || {
                print_warning "Interpreter-Setzung fehlgeschlagen"
            }
        fi
    fi
    
    # Entferne nicht benötigte DT_NEEDED Einträge (falls vorhanden)
    local needed_libs=$(patchelf --print-needed "$binary_file" 2>/dev/null || echo "")
    if [ -n "$needed_libs" ]; then
        print_step "Benötigte Bibliotheken gefunden, prüfe Optimierungen..."
        # Hier könnten spezifische Bibliotheken entfernt werden, falls nicht benötigt
    fi
    
    print_success "patchelf-Optimierungen angewendet"
}

build_nuitka_wine() {
    print_step "🍷 Baue Windows EXE mit Nuitka + Wine..."
    
    # Prüfe Wine
    if ! command -v wine &> /dev/null; then
        print_error "Wine nicht gefunden! Installiere mit: sudo apt install wine"
        return 1
    fi
    
    # Prüfe Python in Wine
    if ! wine python --version &> /dev/null; then
        print_error "Python nicht in Wine installiert!"
        return 1
    fi
    
    # Nuitka in Wine installieren falls nicht vorhanden
    if ! wine python -c "import nuitka" &> /dev/null; then
        print_step "Installiere Nuitka in Wine..."
        wine python -m pip install nuitka
    fi
    
    # Wine Nuitka Build
    local wine_nuitka_cmd=(
        wine python -m nuitka
        --onefile
        --standalone  
        --assume-yes-for-downloads
        --output-filename=SavageWorldsCharakterGenerator_wine.exe
        --windows-console-mode=disable
        --windows-icon-from-ico=assets/Savage-Worlds-Fanprodukt-Logo.png
        --include-data-dir=assets=assets
        --include-data-dir=config=config
        --include-data-dir=settings=settings
        --include-data-dir=templates=templates
        --include-data-dir=views=views
        --include-data-dir=chars=chars
        --include-data-file=main.kv=main.kv
        --plugin-enable=kivy
        --follow-imports
        --follow-import-to=kivymd
        --follow-import-to=reportlab
        --follow-import-to=requests
        --follow-import-to=PIL
        --nofollow-import-to=matplotlib
        --nofollow-import-to=numpy
        --nofollow-import-to=scipy
        --nofollow-import-to=tkinter
        --nofollow-import-to=sqlite3
        --remove-output
        --jobs=2
        main.py
    )
    
    print_step "Starte Wine Nuitka Build..."
    
    if WINEDEBUG=-all "${wine_nuitka_cmd[@]}"; then
        if [ -f "SavageWorldsCharakterGenerator_wine.exe" ]; then
            local size_mb=$(du -m "SavageWorldsCharakterGenerator_wine.exe" | cut -f1)
            print_success "Wine Nuitka EXE erstellt (${size_mb} MB)"
            
            # In dist-Ordner verschieben
            mkdir -p dist
            mv "SavageWorldsCharakterGenerator_wine.exe" "dist/"
            
            # Backup mit Timestamp
            cp "dist/SavageWorldsCharakterGenerator_wine.exe" "dist/SavageWorldsCharakterGenerator_wine_${TIMESTAMP}.exe" 2>/dev/null || true
        else
            print_error "Wine Nuitka EXE nicht gefunden!"
            return 1
        fi
    else
        print_error "Wine Nuitka Build fehlgeschlagen!"
        return 1
    fi
    
    return 0
}

show_results() {
    print_step "📋 Build-Ergebnisse:"
    
    if [ -f "dist/SavageWorldsCharakterGenerator" ]; then
        local exe_size=$(du -h "dist/SavageWorldsCharakterGenerator" | cut -f1)
        echo -e "${GREEN}${NUITKA_EMOJI} Nuitka Binary: ${exe_size}${NC}"
        echo -e "   📍 dist/SavageWorldsCharakterGenerator"
    fi
    
    if [ -f "dist/SavageWorldsCharakterGenerator_wine.exe" ]; then
        local wine_size=$(du -h "dist/SavageWorldsCharakterGenerator_wine.exe" | cut -f1)
        echo -e "${GREEN}🍷 Wine Nuitka EXE: ${wine_size}${NC}"
        echo -e "   📍 dist/SavageWorldsCharakterGenerator_wine.exe"
    fi
    
    echo -e "\n${CYAN}💡 Vorteile von Nuitka:${NC}"
    echo -e "   ✓ Weniger False-Positives bei Antiviren-Software"
    echo -e "   ✓ Bessere Performance durch native Kompilierung"
    echo -e "   ✓ Kleinere Dateigröße als PyInstaller"
    echo -e "   ✓ Keine Entpackung zur Laufzeit nötig"
}

main() {
    cd "$PROJECT_DIR"
    
    print_header
    
    # Parse Argumente
    BUILD_NATIVE=true
    BUILD_WINE=false
    
    case "${1:-native}" in
        "native"|"linux")
            BUILD_WINE=false
            print_step "Nur nativer Nuitka Build"
            ;;
        "wine"|"windows")
            BUILD_NATIVE=false
            BUILD_WINE=true
            print_step "Nur Wine Nuitka Build"
            ;;
        "both"|"all")
            BUILD_WINE=true
            print_step "Nativer und Wine Nuitka Build"
            ;;
        *)
            echo "Usage: $0 [native|wine|both]"
            exit 1
            ;;
    esac
    
    # Nuitka prüfen
    if ! check_nuitka; then
        exit 1
    fi
    
    # patchelf prüfen (nur für Linux Build)
    if [ "$BUILD_NATIVE" = true ]; then
        if ! check_patchelf; then
            print_warning "patchelf nicht verfügbar - Build ohne Optimierungen"
        fi
    fi
    
    # Bereinigung
    cleanup_nuitka_files
    
    # Builds
    if [ "$BUILD_NATIVE" = true ]; then
        if build_nuitka_exe; then
            print_success "Nativer Nuitka Build erfolgreich"
        else
            print_error "Nativer Nuitka Build fehlgeschlagen"
            exit 1
        fi
    fi
    
    if [ "$BUILD_WINE" = true ]; then
        if build_nuitka_wine; then
            print_success "Wine Nuitka Build erfolgreich"
        else
            print_warning "Wine Nuitka Build fehlgeschlagen (nicht kritisch)"
        fi
    fi
    
    # Finale Bereinigung
    cleanup_nuitka_files
    
    # Ergebnisse zeigen
    show_results
    
    print_success "Nuitka Build abgeschlossen! ${SUCCESS_EMOJI}"
}

# Script ausführen
main "$@"