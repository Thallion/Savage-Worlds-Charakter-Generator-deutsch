#!/bin/bash
# ===================================================================
# Savage Worlds Charakter Generator - Local Android Build mit Docker
# Erstellt Android APK mit Buildozer + Docker (lokaler Test)
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
DOCKER_EMOJI="🐋"
ANDROID_EMOJI="📱"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

print_header() {
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${CYAN} Savage Worlds Generator - Android Docker Build${NC}"
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

check_docker() {
    print_step "${DOCKER_EMOJI} Prüfe Docker-Installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker nicht gefunden! Installiere Docker Desktop oder docker.io"
        return 1
    fi
    
    # Prüfe ob Docker läuft
    if ! docker info &> /dev/null; then
        print_error "Docker läuft nicht! Starte Docker Desktop oder docker service"
        return 1
    fi
    
    print_success "Docker gefunden und läuft"
    return 0
}

prepare_build() {
    print_step "📋 Bereite Build vor..."
    
    # Erstelle Build-Ordner
    mkdir -p build-output bin
    
    # Backup der buildozer.spec
    cp buildozer.spec buildozer.spec.backup
    
    # Update buildozer.spec für Docker Build
    print_step "Aktualisiere buildozer.spec..."
    
    # Setze Android-optimierte Konfiguration
    sed -i.tmp "s|android.accept_sdk_license = .*|android.accept_sdk_license = True|" buildozer.spec
    sed -i.tmp "s|android.skip_update = .*|android.skip_update = False|" buildozer.spec
    
    # Aktualisiere Version mit Timestamp
    VERSION=$(grep "version = " buildozer.spec | cut -d' ' -f3)
    NEW_VERSION="${VERSION}.$(date +%m%d)"
    sed -i.tmp "s|version = .*|version = $NEW_VERSION|" buildozer.spec
    
    print_success "Build-Vorbereitung abgeschlossen"
}

build_with_official_docker() {
    print_step "${ANDROID_EMOJI} Baue APK mit offiziellem Kivy Docker..."
    
    # Hole aktuelles Kivy Buildozer Docker Image
    print_step "Lade Docker Image..."
    docker pull kivy/buildozer:latest
    
    # Führe Build im Container aus
    print_step "Starte Android Build..."
    
    if docker run --rm \
        --volume "$(pwd)":/home/user/app \
        --volume ~/.buildozer:/home/user/.buildozer \
        --workdir /home/user/app \
        --env USER=user \
        --env HOME=/home/user \
        kivy/buildozer:latest \
        bash -c "
            set -e
            echo '${DOCKER_EMOJI} Container Setup...'
            
            # Berechtigungen korrigieren
            sudo chown -R user:user /home/user/app
            sudo chown -R user:user /home/user/.buildozer 2>/dev/null || true
            
            # Buildozer initialisieren
            buildozer init 2>/dev/null || echo 'Buildozer bereits initialisiert'
            
            # SDK aktualisieren
            echo '${ANDROID_EMOJI} Aktualisiere Android SDK...'
            yes | buildozer android update 2>/dev/null || echo 'SDK Update abgeschlossen'
            
            # APK Build
            echo '${BUILD_EMOJI} Erstelle APK...'
            buildozer android debug --verbose
            
            # Ergebnisse anzeigen
            echo '${SUCCESS_EMOJI} Build abgeschlossen!'
            ls -la bin/ 2>/dev/null || echo 'Kein bin/ Verzeichnis gefunden'
        "; then
        print_success "Docker Build erfolgreich"
        return 0
    else
        print_error "Docker Build fehlgeschlagen"
        return 1
    fi
}

build_with_custom_docker() {
    print_step "🔧 Alternative Docker-Methode..."
    
    # Erstelle eigenes Dockerfile
    cat > Dockerfile.buildozer << 'EOF'
FROM ubuntu:22.04

# System Setup
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    git \
    unzip \
    openjdk-11-jdk \
    wget \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Java Environment
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Python Dependencies
RUN python3 -m pip install --upgrade pip wheel setuptools
RUN python3 -m pip install buildozer cython kivy

# Arbeitsverzeichnis
WORKDIR /app

# Build-Script
COPY . .

# Build-Befehl
CMD ["python3", "-m", "buildozer", "android", "debug"]
EOF

    # Baue eigenes Image
    print_step "Erstelle Custom Docker Image..."
    if docker build -f Dockerfile.buildozer -t savage-worlds-android . --no-cache; then
        print_step "Führe Custom Build aus..."
        
        if docker run --rm \
            -v "$(pwd)/bin":/app/bin \
            savage-worlds-android; then
            print_success "Custom Docker Build erfolgreich"
            return 0
        else
            print_error "Custom Docker Build fehlgeschlagen"
            return 1
        fi
    else
        print_error "Docker Image Build fehlgeschlagen"
        return 1
    fi
}

analyze_results() {
    print_step "📊 Analysiere Build-Ergebnisse..."
    
    # Suche nach APK Dateien
    APK_COUNT=0
    
    # Prüfe verschiedene Locations
    for location in "bin" "build-output" "."; do
        if [ -d "$location" ]; then
            find "$location" -maxdepth 1 -name "*.apk" -type f 2>/dev/null | while read apk; do
                if [ -f "$apk" ]; then
                    APK_COUNT=$((APK_COUNT + 1))
                    APK_SIZE=$(du -h "$apk" | cut -f1)
                    APK_NAME=$(basename "$apk")
                    
                    echo -e "${GREEN}${ANDROID_EMOJI} APK gefunden: ${APK_NAME}${NC}"
                    echo -e "   📏 Größe: ${APK_SIZE}"
                    echo -e "   📍 Pfad: ${apk}"
                    
                    # Kopiere zur Standard-Location
                    mkdir -p bin
                    cp "$apk" "bin/${APK_NAME}" 2>/dev/null || true
                fi
            done
        fi
    done
    
    # Finale Ergebnisse
    if [ -d "bin" ] && [ "$(find bin -name '*.apk' | wc -l)" -gt 0 ]; then
        echo -e "\n${GREEN}${SUCCESS_EMOJI} APK Build erfolgreich!${NC}"
        echo -e "${CYAN}📱 Finale APK-Dateien:${NC}"
        ls -lah bin/*.apk
    else
        echo -e "\n${RED}${ERROR_EMOJI} Keine APK-Dateien gefunden!${NC}"
        return 1
    fi
    
    return 0
}

cleanup() {
    print_step "🧹 Bereinige Build-Artefakte..."
    
    # Entferne temporäre Docker-Dateien
    rm -f Dockerfile.buildozer
    rm -f buildozer.spec.tmp
    
    # Optionale Bereinigung (nur wenn erfolgreich)
    if [ "$1" = "success" ]; then
        # Docker Images bereinigen (optional)
        docker image prune -f --filter label=stage=buildozer 2>/dev/null || true
    fi
    
    print_success "Bereinigung abgeschlossen"
}

show_results() {
    print_step "📋 Build-Zusammenfassung:"
    
    echo -e "${CYAN}🐋 Docker Android Build${NC}"
    echo -e "   📅 Zeitstempel: ${TIMESTAMP}"
    echo -e "   📂 Projekt: $(basename "$PROJECT_DIR")"
    
    if [ -d "bin" ] && [ "$(find bin -name '*.apk' | wc -l)" -gt 0 ]; then
        echo -e "\n${GREEN}📱 APK-Ergebnisse:${NC}"
        for apk in bin/*.apk; do
            if [ -f "$apk" ]; then
                APK_SIZE=$(du -h "$apk" | cut -f1)
                echo -e "   ✅ $(basename "$apk") (${APK_SIZE})"
            fi
        done
        
        echo -e "\n${CYAN}💡 Nächste Schritte:${NC}"
        echo -e "   📱 Teste APK auf Android-Gerät oder Emulator"
        echo -e "   🔄 Verwende 'adb install bin/*.apk' für Installation"
        echo -e "   🚀 Für Release-Build: verwende 'release' statt 'debug'"
    else
        echo -e "\n${RED}❌ Build fehlgeschlagen${NC}"
        echo -e "   📋 Prüfe buildozer.log für Details"
        echo -e "   🔧 Teste buildozer.spec Konfiguration"
    fi
}

main() {
    cd "$PROJECT_DIR"
    
    print_header
    
    # Parse Argumente
    BUILD_MODE="${1:-debug}"
    
    case "$BUILD_MODE" in
        "debug"|"release")
            echo -e "${BLUE}📱 Build-Modus: ${BUILD_MODE}${NC}"
            ;;
        *)
            echo "Usage: $0 [debug|release]"
            exit 1
            ;;
    esac
    
    # Pre-Checks
    if ! check_docker; then
        exit 1
    fi
    
    # Build-Vorbereitung
    prepare_build
    
    # Versuche offiziellen Docker Build
    if build_with_official_docker; then
        BUILD_SUCCESS=true
    else
        print_warning "Offizieller Docker Build fehlgeschlagen, versuche Custom Build..."
        if build_with_custom_docker; then
            BUILD_SUCCESS=true
        else
            BUILD_SUCCESS=false
        fi
    fi
    
    # Ergebnisse analysieren
    if [ "$BUILD_SUCCESS" = true ]; then
        if analyze_results; then
            cleanup success
            show_results
            print_success "Android Docker Build erfolgreich abgeschlossen! ${SUCCESS_EMOJI}"
        else
            cleanup failure
            print_error "Ergebnis-Analyse fehlgeschlagen"
            exit 1
        fi
    else
        cleanup failure
        print_error "Alle Docker Build-Methoden fehlgeschlagen"
        exit 1
    fi
}

# Script ausführen
main "$@"