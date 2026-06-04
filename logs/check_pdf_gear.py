#!/usr/bin/env python3
"""
Erweiterter Equipment-Check: parsed GEAR/Ausrüstung aus PDF-extrahierten Texten
und vergleicht mit den Setting-Katalogen.

Unterstützt:
- "GEAR" Header (EN)
- "AUSRÜSTUNG" / "Ausrüstung" Header (DE)
- "Gear:" inline (ETU)
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Reuse alias map from check_fehlende_ausruestung.py
sys.path.insert(0, 'logs')
from check_fehlende_ausruestung import (
    ITEM_ALIASES, load_settings,
)


# Setting-Zuordnung pro PDF-Titel
PDF_TO_SETTING = {
    'Pathfinder_for_Savage_Worlds_Archetype_Cards_Set_2': 'Savage Pathfinder',
    'Pathfinder_for_Savage_Worlds_Archetype_Cards_Set_3': 'Savage Pathfinder',
    'US85054PDF_SWPF_Archetypen_Set_meta': 'Savage Pathfinder',
    'Horror_Companion_Archetypes_(SWADE)': 'Horror Kompendium',
    'Super_Powers_Archetype_Cards_-_PDF': 'Superkräfte Kompendium',
    'Science_Fiction_Companion_Archetypes_(SWADE)': 'SciFi Kompendium',
    'SciFi Kompendium Archetypen': 'SciFi Kompendium',
    'US85040PDF_Deadlands_Archetypen-Set_meta': 'Deadlands',
    'ETU_Archetypes': 'SWAE',  # ETU ist modern/contemporary, ähnlich SWAE
    '50_Fathoms_SWADE_Conversion': '50 Fathoms',
    'Rippers_SWADE_Conversion': 'Rippers',
    'SW-Hellfrost-GER-Conversion': 'Hellfrost',
    'SW-sundered-skies-ger-konversion': 'Sundered Skies',
    'SWEX_to_SWADE': 'SWAE',
    'DToA - Brent Hardcastle': 'SWAE',
    'DToA - Doctor Daniel Davenport': 'SWAE',
    'DToA - Jimmy Patterson': 'SWAE',
    'DToA - Lady Amelia Valentine': 'SWAE',
    'Egnus_Amaron': 'SWAE',
    'Hzinth-Priester': 'Savage Aventurien',
    'Wildes_Aventurien': 'Savage Aventurien',
    'Wildes-Aventurien-V2.3': 'Savage Aventurien',
}


def parse_gear_from_layout_text(text, gear_pattern='GEAR'):
    """
    Parst Layout-Text und gibt {archetype_name: gear_text} zurück.
    Erkennt 'GEAR' (EN) oder 'AUSRÜSTUNG' (DE) Header.
    """
    lines = text.split('\n')
    archetypes = {}
    current = None
    in_gear = False
    gear_lines = []

    section_keywords = (
        'ATTRIBUTES', 'ATTRIBUTE', 'SKILLS', 'SKILL', 'FERTIGKEITEN', 'FERTIGKEIT',
        'HINDRANCES', 'HANDICAPS', 'HANDICAP', 'HANDIKAPS',
        'EDGES', 'EDGE', 'TALENTE', 'TALENT', 'KLASSENFÄHIGKEITEN',
        'ANCESTRY', 'ABSTAMMUNG', 'ABSTAMMUNGEN',
        'RANK', 'RANG', 'RACE', 'VOLK',
        'POWERS', 'MÄCHTE', 'MACHT',
        'ADVANCES', 'ADVANCE', 'AUFSTIEGE', 'VORAUSSETZUNGEN',
        'SUPER POWERS', 'POWER LEVEL', 'GEAR', 'AUSRÜSTUNG', 'Ausrüstung',
        'LANGUAGES', 'SPRACHEN', 'CLASS FEATURES', 'KLASSENFÄHIGKEIT',
    )

    gear_section = gear_pattern.upper()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # GEAR/AUSRÜSTUNG-Header erkennen
        if re.match(rf'^\s*{gear_section}\s*$', stripped, re.IGNORECASE):
            in_gear = True
            gear_lines = []
            continue

        # Sektionsende (wenn bekannte Sektion beginnt)
        if in_gear and any(re.match(rf'^\s*{kw}\s*$', stripped, re.IGNORECASE)
                           for kw in section_keywords if kw != gear_section):
            in_gear = False
            if current and gear_lines:
                archetypes[current] = ' '.join(gear_lines)
            gear_lines = []
            continue

        # Neue Archetyp-Erkennung: ALL CAPS Zeile mit Name (typisch Karten-Layout)
        # ODER DE all caps
        if not in_gear:
            # EN: "COMMANDER", "KIRA (BARBARIAN)" etc.
            # DE: "AMIRI (BARBAR)"
            # Erkenne Zeilen, die nur aus Großbuchstaben + Klammern bestehen
            name_match = re.match(r'^([A-ZÄÖÜ][A-ZÄÖÜ\s\-]{2,40})(\s*\([^)]+\))?\s*$', stripped)
            if name_match and not any(re.match(rf'^\s*{kw}\s*$', stripped, re.IGNORECASE)
                                       for kw in section_keywords):
                # Speichere vorherigen
                if current and gear_lines:
                    archetypes[current] = ' '.join(gear_lines)
                current = stripped
                gear_lines = []
                in_gear = False
                continue

        # In Gear sammeln
        if in_gear and stripped:
            gear_lines.append(stripped)

    # Letzten speichern
    if current and gear_lines:
        archetypes[current] = ' '.join(gear_lines)

    return archetypes


def parse_etu_gear(text):
    """Parst ETU 'Gear:'-Inline Format."""
    archetypes = {}
    current = None
    lines = text.split('\n')

    for line in lines:
        stripped = line.strip()
        # ETU: Großbuchstaben Name am Zeilenanfang
        # z.B. "THE CHEERLEADER", "THE PREPPER", etc.
        m = re.match(r'^THE\s+[A-Z][A-Z\s]+$', stripped)
        if m:
            if current:
                pass  # vorheriger wurde bereits in 'gear_lines' gespeichert
            current = stripped
            continue
        if current and 'Gear:' in line:
            # Gear-Sektion inline
            idx = line.find('Gear:')
            gear = line[idx+5:].strip()
            archetypes[current] = gear
            current = None
    return archetypes


def wb_contains(needle, hay):
    """Wortgrenzen-Substring: needle kommt in hay an einer Wortgrenze vor
    (Anfang oder nach einem Nicht-Buchstaben).

    Deutsche Komposita haben keine Leerzeichen → ein einfaches `in` lässt
    `stab` fälschlich in `Rauchstab`, `pike` in `spiked`, `handaxt` in
    `Zweihandaxt` matchen. Die Wortgrenzen-Prüfung verhindert diese
    Suffix-Treffer; legitime Komposita werden über die Alias-Map explizit
    aufgelöst (z.B. `sword` → `langschwert`)."""
    if not needle or not hay:
        return False
    if needle == hay:
        return True
    start = 0
    while True:
        i = hay.find(needle, start)
        if i < 0:
            return False
        if i == 0 or not hay[i - 1].isalpha():
            return True
        start = i + 1


def find_item_in_catalog(item_text, catalog_keys):
    """Versucht item_text im Katalog zu finden via Alias-Map (Wortgrenzen-Match)."""
    item_lower = item_text.lower().strip()
    if not item_lower or len(item_lower) < 2:
        return None

    # Deterministische Reihenfolge: catalog_keys ist ein Set → sonst variiert der
    # zurückgegebene Treffer (und damit OFFEN/IST-Einstufung) zwischen Läufen.
    catalog_keys = sorted(catalog_keys)

    # 1. Exakter Match
    for key in catalog_keys:
        if key.lower() == item_lower:
            return key

    # 2. Alias-Match
    candidates = [item_text]
    if item_text in ITEM_ALIASES:
        alias = ITEM_ALIASES[item_text]
        if alias is not None:
            candidates.extend(alias)
    elif item_lower in [a.lower() for a in ITEM_ALIASES]:
        # Case-insensitive
        for k, v in ITEM_ALIASES.items():
            if k.lower() == item_lower and v is not None:
                candidates.extend(v)
                break

    for cand in candidates:
        cand_lower = cand.lower()
        for key in catalog_keys:
            kl = key.lower()
            if cand_lower == kl or wb_contains(cand_lower, kl) or wb_contains(kl, cand_lower):
                return key

    return None


def split_gear_items(gear_text, strict_noise=False):
    """Splittet Gear-Text in einzelne Items (Komma-separiert, parens-aware).

    strict_noise=True verwirft zusätzlich Stat-Block-Fragmente (Würfel,
    Spalten-Reste, Prosa) — für die rohe PDF-Extraktion sinnvoll, NICHT für
    die SOLL/IST-Analyse (die mappt Stat-Items über Normalisierung)."""
    # Soft-Hyphen (U+00AD, ggf. + Whitespace) zusammenführen (PDF-Silbentrennung)
    gear_text = re.sub('­\\s*', '', gear_text)
    gear_text = re.sub(r'(\w)[‐-―-]\s+(\w)', r'\1\2', gear_text)
    # Entferne Geld
    text = re.sub(r'\$\d+[.,]?\d*\.?', '', gear_text)
    text = re.sub(r'\d+\s*GP\.?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*gp', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*\$', '', text)

    # Split by Komma, aber respektiere parens
    items = []
    depth = 0
    current = ''
    for ch in text:
        if ch == '(':
            depth += 1
            current += ch
        elif ch == ')':
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0:
            if current.strip():
                items.append(current.strip())
            current = ''
        else:
            current += ch
    if current.strip():
        items.append(current.strip())

    # Filtere offensichtliche Nicht-Items
    filtered = []
    noise_patterns = [
        # Stat-Descriptoren / Würfel
        r'^\s*W?\d+\+?\d*\s*$',  # W6, W8+1, etc
        r'^\s*[+-]?\d+\s*$',  # reine Zahlen
        # Klammern-only
        r'^\s*\([^)]*\)\s*$',
        # Würfel + Modifier mit Buchstaben
        r'^\s*W?d?\d+\s*$',
        # Währung
        r'^\s*\$\d+',
        r'^\s*\d+\s*(GM|GP|Räder|gp)\s*$',
        # Edge/Handicap-Name-typisch (Großbuchstaben am Anfang + Edge-Keywords)
        r'^(Brave|Quick|Luck|Strength|Attractive|Connections|Persuasion|Fighting|Smarts|Spirit|Alertness|Marksman|Marken|Charismatic|Sweep|Ruthless|Heroic|Compassion|Power Surge|Super Edge|New Powers)',
    ]
    for item in items:
        # Trim
        it = item.strip()
        if not it or len(it) < 2:
            continue
        # Filter noise
        if any(re.match(p, it, re.IGNORECASE) for p in noise_patterns):
            continue
        # Languages raus
        if re.match(r'^(Languages?|Sprachen)\s*:', it, re.IGNORECASE):
            continue
        if it.lower() in ('common', 'elven', 'goblin', 'halfling', 'celestial', 'dwarven',
                          'sylvan', 'orcish', 'draconic', 'infernal', 'abyssal', 'giant',
                          'gemeinsprache', 'elfisch', 'goblinisch', 'halblingisch', 'orksprache',
                          'drakonisch', 'himmlisch', 'infernalisch', 'abyssisch', 'riesisch'):
            continue
        # "GM" allein
        if re.match(r'^\d+\s*GM\.?$', it):
            continue
        if strict_noise:
            low = it.lower()
            # Würfel-/Stat-Block-Fragmente (Spalten-Vermischung der PDF-Extraktion)
            if re.search(r'\b[dwW]\d+\b', it) or re.search(r'\d+d\d+', it):
                continue
            # Sektions-Schlüsselwörter / Stat-Namen aus vermischten Spalten
            if re.search(r'\b(attributes?|skills?|advances?|fighting|notice|stealth|'
                         r'shooting|spirit|smarts|strength|vigor|occult|gambling|'
                         r'intimidation|athletics|parry|toughness|rank|powers?|'
                         r'aufstiege|attribute|fertigkeiten|allgemeinwissen|kämpfen|'
                         r'heimlichkeit|schießen|überreden)\b', low):
                continue
            # Zu lange Fragmente = mit hoher Wahrscheinlichkeit Prosa/Stat-Mix
            if len(it) > 45:
                continue
            # Reste mit Doppelpunkt-Sektion ("AUFSTIEGE: ...")
            if re.match(r'^[A-ZÄÖÜ ]{3,}:', it):
                continue
        filtered.append(it)
    return filtered


def check_pdf_against_catalog(pdf_name, gear_dict, catalog_keys):
    """
    Prüft alle Gear-Items gegen den Katalog.
    Returns: list of {archetype, item, status}
    """
    findings = []
    for arch, gear in gear_dict.items():
        items = split_gear_items(gear, strict_noise=True)
        for item in items:
            matched = find_item_in_catalog(item, catalog_keys)
            if matched is None and item.lower() not in ['none', 'keine', '—', 'none.']:
                findings.append({
                    'pdf': pdf_name,
                    'archetype': arch,
                    'item': item,
                })
    return findings


def main():
    settings = load_settings()
    pdf_dir = Path('logs/pdf_extracted')

    out = []
    out.append("# Fehlende Ausrüstung (PDF-extrahiert) (Stand: 2026-06-04)\n\n")
    out.append("Systematische Cross-Prüfung: Items aus PDF-Bögen in `logs/pdf_extracted/`\n")
    out.append("gegen Setting-Kataloge in `settings/*.json`.\n\n")
    out.append("**Methodik:**\n")
    out.append("1. `pdftotext -layout` extrahiert Text aus allen `Texte/*.pdf` (26 PDFs, Stand 2026-06-04)\n")
    out.append("2. Parser erkennt 'GEAR' (EN), 'AUSRÜSTUNG' (DE), 'Gear:' inline (ETU)\n")
    out.append("3. Pro Archetyp: Items extrahieren → Alias-Map (EN→DE) → Katalog-Match\n")
    out.append("4. Items ohne Katalog-Match → MISSING\n\n")
    out.append("---\n\n")

    total_findings = []

    for pdf_path in sorted(pdf_dir.glob('*.txt')):
        # Slug zurück zu PDF-Name
        pdf_name = pdf_path.stem

        # Setting bestimmen
        # Versuche exakte + Fuzzy-Match
        setting_key = None
        for k, v in PDF_TO_SETTING.items():
            if k in pdf_name or pdf_name in k:
                setting_key = v
                break
        if setting_key is None:
            # Fallback: Slugifizierter Name
            for k, v in PDF_TO_SETTING.items():
                slug = k.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace('-', '_')
                if slug in pdf_name.upper() or pdf_name.upper() in slug:
                    setting_key = v
                    break
        if setting_key is None:
            out.append(f"## ? {pdf_name} — Setting nicht zugeordnet\n\n")
            continue

        if setting_key not in settings:
            out.append(f"## ? {pdf_name} — Setting '{setting_key}' nicht geladen\n\n")
            continue

        catalog = settings[setting_key]['ausruestung_keys']
        text = pdf_path.read_text(encoding='utf-8')

        # Passenden Parser wählen
        if 'ETU' in pdf_name:
            gear_dict = parse_etu_gear(text)
        else:
            # Versuche DE-Header, dann EN
            gear_dict = parse_gear_from_layout_text(text, gear_pattern='AUSRÜSTUNG')
            if not gear_dict:
                gear_dict = parse_gear_from_layout_text(text, gear_pattern='Ausrüstung')
            if not gear_dict:
                gear_dict = parse_gear_from_layout_text(text, gear_pattern='GEAR')

        if not gear_dict:
            out.append(f"## {pdf_name} → {setting_key}\n\n")
            out.append(f"⚠ Keine GEAR/Ausrüstung-Sektionen gefunden.\n\n")
            continue

        findings = check_pdf_against_catalog(pdf_name, gear_dict, catalog)
        total_findings.extend(findings)

        out.append(f"## {pdf_name} → **{setting_key}** ({len(gear_dict)} Archetypen)\n\n")
        if not findings:
            out.append(f"✅ Alle im Bogen genannten Items sind im Katalog vorhanden.\n\n")
        else:
            out.append(f"**❌ {len(findings)} Items fehlen im Katalog:**\n\n")
            by_item = defaultdict(list)
            for f in findings:
                by_item[f['item']].append(f['archetype'])
            for item, archs in sorted(by_item.items()):
                # Truncate item display
                display = item[:80] + ('...' if len(item) > 80 else '')
                out.append(f"- **{display}** — fehlt in: {', '.join(archs[:3])}{'...' if len(archs) > 3 else ''}\n")
            out.append("\n")

    # Summary
    out.append("---\n\n")
    out.append(f"## Gesamt\n\n")
    out.append(f"**{len(total_findings)} Items fehlen in Katalogen** (über alle {len(list(pdf_dir.glob('*.txt')))} PDFs).\n\n")
    by_setting = defaultdict(int)
    for f in total_findings:
        for k, v in PDF_TO_SETTING.items():
            if k in f['pdf'] or f['pdf'] in k:
                by_setting[v] += 1
                break
    out.append("| Setting | Fehlende Items |\n|---|---|\n")
    for s, count in sorted(by_setting.items(), key=lambda x: -x[1]):
        out.append(f"| {s} | {count} |\n")

    out_path = 'logs/fehlende_ausruestung_pdf.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"Bericht: {out_path}")
    print(f"Gesamt Findings: {len(total_findings)}")


if __name__ == '__main__':
    main()
