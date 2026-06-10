# utils/archetypen_sync.py
"""
Synchronisation der mitgelieferten Archetypen ins persistente
Benutzer-Verzeichnis (Android).

Reine Datei-Logik ohne Kivy-Abhängigkeiten, damit sie in Unit-Tests
ohne App-Kontext geprüft werden kann. Logging und Plattform-Erkennung
verbleiben beim Aufrufer (main.py).
"""

import shutil
from pathlib import Path


def repariere_mojibake_name(name: str) -> str:
    """Repariert Mojibake in Dateinamen aus der APK-Extraktion.

    Der Java-Tar-Extractor von python-for-android (jtar) castet beim Parsen
    der Header signierte Bytes direkt zu chars. UTF-8-Bytes ≥ 0x80 werden
    dadurch sign-extended: 0xC3 → U+FFC3. 'Kopfgeldjäger' landet so als
    'Kopfgeldjￃﾤger' auf dem Gerät (verifiziert mit jtar 2.3 + OpenJDK).

    Zusätzlich wird klassisches Latin-1-Mojibake ('Ã¤' → 'ä') repariert.
    Rückkonvertierung nur, wenn die rekonstruierten Bytes gültiges UTF-8
    ergeben — reine ASCII-Namen und echte Umlaut-Namen bleiben unverändert.
    """
    # Muster 1: Java-signed-byte-Mojibake (U+FF80–U+FFFF)
    if any(0xFF80 <= ord(c) <= 0xFFFF for c in name):
        try:
            raw = bytes(
                (ord(c) - 0xFF00) if 0xFF80 <= ord(c) <= 0xFFFF else ord(c)
                for c in name
            )
            return raw.decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return name

    # Muster 2: Latin-1-Mojibake ('Ã¤')
    try:
        return name.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def zaehle_archetypen(verzeichnis: Path) -> int:
    """Zählt JSON-Dateien (rekursiv) in einem Verzeichnis. 0 bei Fehlern."""
    try:
        verzeichnis = Path(verzeichnis)
        if not verzeichnis.is_dir():
            return 0
        return sum(1 for f in verzeichnis.rglob('*.json') if f.is_file())
    except OSError:
        return 0


def finde_beste_quelle(kandidaten, ziel: Path):
    """Wählt aus den Kandidaten das Verzeichnis mit den meisten Archetypen-JSONs.

    Das Zielverzeichnis selbst wird übersprungen, damit nie "von sich
    selbst" kopiert wird (z.B. wenn ein Kandidaten-Pfad versehentlich auf
    das persistente Verzeichnis zeigt).

    Returns:
        tuple: (Pfad oder None, Anzahl JSONs in der Quelle)
    """
    try:
        ziel_resolved = Path(ziel).resolve()
    except OSError:
        ziel_resolved = Path(ziel)

    beste = None
    beste_anzahl = 0
    for kandidat in kandidaten:
        pfad = Path(kandidat)
        try:
            if pfad.resolve() == ziel_resolved:
                continue
        except OSError:
            continue
        anzahl = zaehle_archetypen(pfad)
        if anzahl > beste_anzahl:
            beste = pfad
            beste_anzahl = anzahl
    return beste, beste_anzahl


def sync_archetypen(quelle: Path, ziel: Path) -> dict:
    """Kopiert fehlende oder geänderte Archetypen von quelle nach ziel.

    - Vergleich über Dateigröße statt mtime, da die APK-Extraktion keine
      brauchbaren Timestamps setzt.
    - Mojibake-Namen aus der APK-Extraktion werden beim Kopieren repariert;
      eine eventuell früher kopierte Mojibake-Variante im Ziel wird entfernt.

    Returns:
        dict: Statistik mit 'kopiert', 'repariert', 'vorhanden', 'fehler'
    """
    statistik = {'kopiert': 0, 'repariert': 0, 'vorhanden': 0, 'fehler': 0}
    quelle = Path(quelle)
    ziel = Path(ziel)
    ziel.mkdir(parents=True, exist_ok=True)

    for item in quelle.rglob('*'):
        if not item.is_file():
            continue
        rel_path = item.relative_to(quelle)
        ziel_name = repariere_mojibake_name(item.name)
        target = ziel / rel_path.parent / ziel_name
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if ziel_name != item.name:
                statistik['repariert'] += 1
                # Alte Mojibake-Variante im Ziel aufräumen
                alte_variante = ziel / rel_path.parent / item.name
                if alte_variante.exists():
                    alte_variante.unlink()
            if not target.exists() or item.stat().st_size != target.stat().st_size:
                shutil.copy2(str(item), str(target))
                statistik['kopiert'] += 1
            else:
                statistik['vorhanden'] += 1
        except OSError:
            statistik['fehler'] += 1

    return statistik
