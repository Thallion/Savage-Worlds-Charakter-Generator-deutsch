"""Master-Build-Skript fuer alle 5 DSA-Archetypen.

Liest die 5 Bogen-PDFs und baut die Archetypen headless via driver.py.
Schreibt Anomalie-Bericht + Logdateien pro Archetyp.
"""
import sys, traceback, subprocess
sys.path.insert(0, '.claude/skills/archetyp-erstellen')

# Baue jeden Archetyp durch Aufruf des jeweiligen Build-Skripts
BUILD_SCRIPTS = [
    'logs/build_alissa_aventurien.py',
    'logs/build_furun_aventurien.py',
    'logs/build_radrosch_aventurien.py',
    'logs/build_tallula_aventurien.py',
    'logs/build_ssrrhyl_aventurien.py',
]

import os
os.chdir('/home/jean/Dokumente/GitHub/Savage-Worlds-Charakter-Generator-deutsch')

for script in BUILD_SCRIPTS:
    print(f"\n{'='*70}\n{os.path.basename(script)}\n{'='*70}")
    r = subprocess.run(
        ['python3', script],
        env={**os.environ, 'SDL_VIDEODRIVER': 'dummy'},
        capture_output=True, text=True, timeout=300
    )
    print(f"Exit-Code: {r.returncode}")
    if r.stdout:
        # nur letzte Zeilen
        lines = r.stdout.strip().split('\n')
        for l in lines[-30:]:
            print(' ', l)
    if r.stderr:
        print('STDERR:', r.stderr[-500:])
