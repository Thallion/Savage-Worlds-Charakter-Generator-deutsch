#!/usr/bin/env python3
"""
Bulk-Extraktion aller PDFs in Texte/ via pdftotext.

Speichert pro PDF eine .txt-Datei in logs/pdf_extracted/<name>.txt.
"""
import os
import subprocess
from pathlib import Path


def extract_all_pdfs():
    """Extrahiere alle PDFs aus Texte/ via pdftotext -layout."""
    src_dir = Path('Texte')
    out_dir = Path('logs/pdf_extracted')
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(src_dir.glob('*.pdf'))
    extracted = 0
    skipped = 0
    failed = []

    for pdf in pdfs:
        # Slugify name (entferne ®, etc.)
        slug = pdf.stem
        slug = slug.replace('®', '').replace('—', '-')
        out_path = out_dir / f"{slug}.txt"
        if out_path.exists():
            skipped += 1
            continue
        try:
            result = subprocess.run(
                ['pdftotext', '-layout', str(pdf), str(out_path)],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                extracted += 1
                print(f"  ✓ {pdf.name} → {out_path.name}")
            else:
                failed.append((pdf.name, result.stderr))
        except Exception as e:
            failed.append((pdf.name, str(e)))

    print(f"\n=== Extraktion abgeschlossen ===")
    print(f"Extrahiert: {extracted}")
    print(f"Übersprungen (existiert bereits): {skipped}")
    print(f"Fehlgeschlagen: {len(failed)}")
    for name, err in failed:
        print(f"  ❌ {name}: {err[:100]}")


if __name__ == '__main__':
    extract_all_pdfs()
