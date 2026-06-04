#!/usr/bin/env python3
"""
SOLL/IST Abweichungs-Analyse: Ausrüstung der gespeicherten Archetyp-Chars
vs. Bogen-Anforderungen in Texte/.

Berücksichtigt: Inventar-Items, Waffen, Rüstungen, Schilde, Cyberware
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, 'logs')
from check_fehlende_ausruestung import (
    ITEM_ALIASES, load_settings,
)
from check_pdf_gear import split_gear_items, find_item_in_catalog


# Bogen-Text → Setting
SETTING_TO_BOGEN = {
    'Deadlands': 'Texte/US85040PDF_Deadlands_Archetypen-Set_meta.txt',
    'Fantasy Kompendium': 'Texte/SW_Fantasy_Kompendium_Archetypen.txt',
    'Savage Pathfinder': 'Texte/SWPF_Archetypen.txt',
    'SciFi Kompendium': 'Texte/SciFi Kompendium Archetypen.txt',
    'Superkräfte Kompendium': 'Texte/Superkräfte Archetypen.txt',
    'SWAE Wilde Welten': 'Texte/SWAE_Wilde_Welten_Archetypen.txt',
    'SuSK (Sundered Skies)': 'Texte/SuSK Archetypen.txt',
    'Worlds of Ulisses': 'Texte/Worlds_of_Ulisses_Archetypen.txt',
}

# Erweiterte DE→EN Mapping
DE_TO_EN = {
    'akrobatin': 'ACROBAT', 'alchemist': 'ALCHEMIST', 'amazone': 'AMAZON',
    'aristokrat': 'ARISTOCRAT', 'assassinin': 'ASSASSIN', 'barbarin': 'BARBARIAN',
    'barde': 'BARD', 'bogenschuetze': 'ARCHER', 'champion': 'CHAMPION',
    'diebin': 'THIEF', 'drachenkämpfer': 'DRAGON_FIGHTER', 'drachenkmpf': 'DRAGON_FIGHTER',
    'druidin': 'DRUID', 'hexe': 'WITCH', 'krieger': 'WARRIOR', 'klerikerin': 'CLERIC',
    'loremaster': 'LOREMASTER', 'magier': 'MAGE', 'mönch': 'MONK', 'moench': 'MONK',
    'narr': 'JESTER', 'paladin': 'PALADIN', 'ritter': 'KNIGHT', 'rüpel': 'BRUTE',
    'ruepel': 'BRUTE', 'schamane': 'SHAMAN', 'schwerttänzerin': 'SWORD_DANCER',
    'schwerttzn': 'SWORD_DANCER', 'tiermeister': 'BEAST_MASTER',
    'totemkrieger': 'TOTEM_WARRIOR', 'totemkmpf': 'TOTEM_WARRIOR',
    'tüftler': 'TINKERER', 'tueftler': 'TINKERER', 'verteidiger': 'DEFENDER',
    'waldläufer': 'RANGER', 'waldlaeuf': 'RANGER', 'zauberer': 'SORCERER',
    # SciFi Kompendium
    'commander': 'COMMANDER', 'psyker': 'PSYKER', 'surveyor': 'SURVEYOR',
    'ambassador': 'AMBASSADOR', 'hacker': 'HACKER', 'infiltrator': 'INFILTRATOR',
    'influencer': 'INFLUENCER', 'mercenary': 'MERCENARY', 'roughneck': 'ROUGHNECK',
    'mystic': 'MYSTIC', 'morpher': 'MORPHER', 'spacer': 'SPACER',
    # Superkräfte
    'panzer': 'TANK', 'schuetze': 'GUNNER', 'eismann': 'ICEMAN',
    'feuervogel': 'FIRE BIRD', 'detektiv': 'DETECTIVE', 'schläger': 'BRAWLER',
    'schlaeger': 'BRAWLER', 'walküre': 'VALKYRIE', 'walkuere': 'VALKYRIE',
    'sprinter': 'SPEEDSTER',
    # Savage Pathfinder
    'amiri': 'AMIRI', 'ezren': 'EZREN', 'harsk': 'HARSK', 'kyra': 'KYRA',
    'lem': 'LEM', 'lini': 'LINI', 'merisiel': 'MERISIEL', 'sajan': 'SAJAN',
    'seelah': 'SEELAH', 'seoni': 'SEONI', 'valeros': 'VALEROS',
}


def parse_english_gear_clean(text_path):
    """
    Parser für EN-Bögen. Liefert {arch_name: [items]} ohne ADVANCES/etc.
    """
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    archetypes = {}
    current = None
    in_gear = False
    gear_lines = []
    section_names = (
        'ATTRIBUTES', 'SKILLS', 'HINDRANCES', 'EDGES', 'POWERS', 'GEAR', 'ADVANCES',
        'ANCESTRY', 'POWER LEVEL', 'RANK', 'SUPER POWERS', 'POWER POINTS',
    )
    stop_words = ('RANK', 'ADVANCE', 'R A N K', 'D ADVANCE')
    for line in text.split('\n'):
        s = line.strip()
        if re.match(r'^[=\-=]{3,}$', s):
            continue
        # Skip RANK/ADVANCE Zeilen
        if any(sw in s.upper() for sw in stop_words):
            in_gear = False
            if current and gear_lines:
                archetypes[current] = ' '.join(gear_lines)
            current = None
            gear_lines = []
            continue
        # Archetype-Detection (vor gear)
        is_arch = (
            re.match(r'^[A-Z][A-Z\s\-]{2,40}$', s)
            and s not in section_names
            and not any(sw in s.upper() for sw in stop_words)
        )
        if is_arch:
            if in_gear and current:
                archetypes[current] = ' '.join(gear_lines)
            elif current and gear_lines:
                archetypes[current] = ' '.join(gear_lines)
            current = s
            gear_lines = []
            in_gear = False
            continue
        if s == 'GEAR':
            in_gear = True
            gear_lines = []
            continue
        if in_gear:
            if s in section_names and s != 'GEAR':
                in_gear = False
                if current:
                    archetypes[current] = ' '.join(gear_lines)
                gear_lines = []
                continue
            if s:
                gear_lines.append(s)
    if current and gear_lines:
        archetypes[current] = ' '.join(gear_lines)
    return archetypes


def find_archetype_in_bogen(char_name, bogen_dict):
    if not bogen_dict or not char_name or char_name == '?':
        return None
    cn = char_name.lower()
    cn_norm = re.sub(r'[\s_\-]+', '', cn)
    if cn_norm in DE_TO_EN:
        target = DE_TO_EN[cn_norm].upper()
        for arch_name in bogen_dict.keys():
            if arch_name.upper() == target:
                return arch_name
    for arch_name in bogen_dict.keys():
        if arch_name.upper() == cn.upper():
            return arch_name
    for arch_name in bogen_dict.keys():
        an_norm = re.sub(r'[\s_\-]+', '', arch_name.upper())
        if cn_norm == an_norm:
            return arch_name
    for arch_name in bogen_dict.keys():
        if cn in arch_name.lower() or arch_name.lower() in cn:
            return arch_name
    return None


def main():
    settings = load_settings()

    # Bogen parsen
    bogen_cache = {}
    for setting_key, bogen_path in SETTING_TO_BOGEN.items():
        if Path(bogen_path).exists():
            bogen_cache[setting_key] = parse_english_gear_clean(bogen_path)
        else:
            bogen_cache[setting_key] = {}

    # Chars laden
    chars = []
    for f in sorted(Path('chars/Archetypen').glob('Archetyp_*.json')):
        try:
            with open(f) as fp:
                data = json.load(fp)
            chars.append({
                'file': f.name,
                'name': data.get('profil_daten', {}).get('Name', '?'),
                'setting': data.get('active_setting_name', '?'),
                'all_inv': (
                    data.get('selected_allgemeine_ausruestung', []) +
                    data.get('selected_waffen', []) +
                    data.get('selected_ruestungen', []) +
                    data.get('selected_schilde', []) +
                    [k for k, v in data.get('selected_elements', {}).get('ausruestung', {}).items()
                     if v.get('ausgewaehlt')]
                ),
            })
        except Exception:
            pass

    out = []
    out.append("# SOLL/IST Abweichungs-Analyse: Ausrüstung (Stand: 2026-06-04)\n\n")
    out.append("**Klassifizierung:**\n")
    out.append("- **FEHLT_OFFEN**: Bogen-Item ist im Katalog vorhanden, Char hat es nicht → **kann ergänzt werden** (Schritt 1)\n")
    out.append("- **FEHLT_KATALOG**: Bogen-Item ist im Katalog NICHT vorhanden → **muss ergänzt werden** (Schritt 2, Freigabe erforderlich)\n")
    out.append("- **ZUVIEL**: Char hat Item, das im Bogen nicht erwähnt wird (häufig: Approximation/Subsitution im Build)\n")
    out.append("- **OK**: SOLL vollständig gedeckt\n\n")
    out.append("**Wichtig:** 'OFFEN' bedeutet Item-Key existiert im Katalog. Im Build-Lauf kann `s.kaufen(item)` aufgerufen werden.\n\n")
    out.append("---\n\n")

    # Aggregiere pro Setting
    by_setting = defaultdict(list)
    for c in chars:
        by_setting[c['setting']].append(c)

    summary_rows = []

    for setting in sorted(by_setting.keys()):
        bogen_dict = bogen_cache.get(setting, {})
        if not bogen_dict:
            continue
        out.append(f"## {setting} ({len(by_setting[setting])} Chars vs. {len(bogen_dict)} Bögen)\n\n")

        setting_keys = settings.get(setting, {}).get('ausruestung_keys', set())
        total_open = 0
        total_missing = 0

        for c in by_setting[setting]:
            arch_key = find_archetype_in_bogen(c['name'], bogen_dict)
            if arch_key is None:
                continue
            bogen_text = bogen_dict[arch_key]
            bogen_items = set(split_gear_items(bogen_text))
            # Filter offensichtliche Nicht-Items
            bogen_items = {x for x in bogen_items
                           if not re.match(r'^\$?\d+$', x.strip()) and
                           x.lower() not in ('none', 'keine', '—')}
            char_inv = set(c['all_inv'])

            # Klassifiziere SOLL-Items
            offen = []   # im Katalog, nicht im Inventar
            fehlt_kat = []  # nicht im Katalog, nicht im Inventar
            for item in bogen_items:
                if item in char_inv:
                    continue
                in_cat = find_item_in_catalog(item, setting_keys)
                if in_cat:
                    offen.append((item, in_cat))
                else:
                    fehlt_kat.append(item)
            zuviel = char_inv - bogen_items

            if not offen and not fehlt_kat and not zuviel:
                continue

            total_open += len(offen)
            total_missing += len(fehlt_kat)

            out.append(f"### {c['name']} ↔ {arch_key}\n\n")
            if offen:
                out.append(f"- **🟢 FEHLT_OFFEN** ({len(offen)}): " +
                           ', '.join(f"`{o[0]}` (→`{o[1]}`)" for o in offen[:6]) +
                           (f", ... +{len(offen)-6}" if len(offen) > 6 else "") + "\n")
            if fehlt_kat:
                out.append(f"- **🔴 FEHLT_KATALOG** ({len(fehlt_kat)}): " +
                           ', '.join(f"`{f}`" for f in fehlt_kat[:6]) +
                           (f", ... +{len(fehlt_kat)-6}" if len(fehlt_kat) > 6 else "") + "\n")
            if zuviel:
                out.append(f"- **⚠ ZUVIEL** ({len(zuviel)}): " +
                           ', '.join(f"`{z}`" for z in list(zuviel)[:6]) +
                           (f", ... +{len(zuviel)-6}" if len(zuviel) > 6 else "") + "\n")
            out.append("\n")

        summary_rows.append((setting, len(by_setting[setting]), total_open, total_missing))

    out.append("---\n\n")
    out.append("## Zusammenfassung\n\n")
    out.append("| Setting | Chars | FEHLT_OFFEN (Schritt 1) | FEHLT_KATALOG (Schritt 2) |\n")
    out.append("|---|---|---|---|\n")
    for s, c, o, m in summary_rows:
        out.append(f"| {s} | {c} | **{o}** | **{m}** |\n")
    total_o = sum(r[2] for r in summary_rows)
    total_m = sum(r[3] for r in summary_rows)
    out.append(f"| **Gesamt** | – | **{total_o}** | **{total_m}** |\n")
    out.append("\n**Schritt 1 (offen):** Diese Items sind im Katalog vorhanden — Build-Skripte können sie per `s.kaufen(name)` einbauen.\n")
    out.append("**Schritt 2 (Katalog):** Diese Items fehlen im Katalog — User-Freigabe + Katalog-Erweiterung erforderlich.\n")

    with open('logs/soll_ist_ausruestung.md', 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"Bericht: logs/soll_ist_ausruestung.md")
    print(f"OFFEN: {total_o}  KATALOG: {total_m}")


if __name__ == '__main__':
    main()
