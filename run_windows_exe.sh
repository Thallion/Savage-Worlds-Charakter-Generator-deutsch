#!/bin/bash
# Wrapper-Script zum Ausführen der Windows EXE mit Wine
# Mit optimierten Graphics-Einstellungen für Wine-Kompatibilität

echo "🍷 Starte Savage Worlds Generator (Windows) mit Wine..."

# Setze Wine-optimierte Umgebungsvariablen
export WINEPREFIX="$HOME/.wine"
export KIVY_WINDOW=sdl2
export KIVY_GL_BACKEND=mock  # Mock-Backend für bessere Wine-Kompatibilität
export KIVY_NO_CONFIG=1
export USE_OPENGL_MOCK=1
export WINEDEBUG=-all  # Unterdrücke Wine-Debug-Meldungen

# Starte die EXE
if [ -f "dist/SavageWorldsCharakterGenerator.exe" ]; then
    echo "🚀 Starte Anwendung..."
    cd dist
    wine SavageWorldsCharakterGenerator.exe
    cd ..
else
    echo "❌ Windows EXE nicht gefunden! Führe zuerst './build_exe.sh wine' aus."
    exit 1
fi