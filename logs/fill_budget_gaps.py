"""
Schließt Budget-Lücken in SciFi- und Fantasy-Archetypen durch zusätzliche Aufstiege.

Lädt jeden gespeicherten Archetyp, vergleicht Skills+Attribute gegen den PDF-Bogen
und hebt Defizite per Aufstieg an — strikt im Seasoned-Cap (ausgegebene Aufstiege < 8).
Idempotent. Hebt NUR an (senkt nie, überschreitet nie den Bogenwert).

WICHTIG (Form-Feed-Falle): pdftotext setzt \\f an Seitenumbrüchen. Pythons splitlines()
trennt dort, grep -n nicht → Zeilennummern divergieren. Daher werden die Archetyp-Header
hier DYNAMISCH per splitlines()-Suche gefunden (kein hartkodierter grep-Index), und der
Stat-Block wird am "AdvAnces"/"RANK" begrenzt (kein Bleed aus Nachbarblöcken).
"""
import sys, re, os, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

LOG = open('/tmp/gapfill_report.txt', 'w', encoding='utf-8')
def w(x): LOG.write(str(x) + '\n'); LOG.flush()

DIE = [4, 6, 8, 10, 12]
def didx(v): return DIE.index(v) if v in DIE else 0

ATTR = {'agility': 'Geschicklichkeit', 'smarts': 'Verstand', 'spirit': 'Willenskraft',
        'strength': 'Stärke', 'vigor': 'Konstitution'}
SKILL = {
 'academics': 'Geisteswissenschaften', 'athletics': 'Athletik', 'battle': 'Kriegskunst',
 'boating': 'Seefahrt', 'com. knowledge': 'Allgemeinwissen', 'common knowledge': 'Allgemeinwissen',
 'driving': 'Fahren', 'electronics': 'Elektronik', 'faith': 'Glaube', 'fighting': 'Kämpfen',
 'focus': 'Fokus', 'gambling': 'Glücksspiel', 'hacking': 'Hacken', 'healing': 'Heilen',
 'intimidation': 'Einschüchtern', 'languages': 'Sprache', 'language': 'Sprache',
 'notice': 'Wahrnehmung', 'occult': 'Okkultismus', 'performance': 'Darbietung',
 'persuasion': 'Überreden', 'piloting': 'Pilot', 'psionics': 'Psionik', 'repair': 'Reparieren',
 'research': 'Recherche', 'riding': 'Reiten', 'science': 'Naturwissenschaften',
 'shooting': 'Schießen', 'spellcasting': 'Zaubern', 'stealth': 'Heimlichkeit',
 'survival': 'Überleben', 'taunt': 'Provozieren', 'thievery': 'Diebeskunst',
 'weird science': 'Verrückte Wissenschaft',
}

# DE-Build-Name -> englischer PDF-Header (Suchbegriff)
FK_EN = {
 'Akrobatin':'ACROBAT','Alchemist':'ALCHEMIST','Amazone':'AMAZON','Aristokrat':'ARISTOCRAT',
 'Assassinin':'ASSASSIN','Barbarin':'BARBARIAN','Barde':'BARD','Bogenschuetze':'ARCHER',
 'Champion':'CHAMPION','Diebin':'THIEF','Drachenkmpf':'DRAGON','Druidin':'DRUID','Hexe':'WITCH',
 'Klerikerin':'CLERIC','Krieger':'WARRIOR','Loremaster':'LOREMASTER','Magier':'MAGE','Moench':'MONK',
 'Narr':'JESTER','Paladin':'PALADIN','Ritter':'KNIGHT','Ruepel':'BRUTE','Schamane':'SHAMAN',
 'Schwerttzn':'BLADE DANCER','Tiermeister':'BEASTMASTER','Totemkmpf':'TOTEM',
 'Tueftler':'TINKERER','Verteidiger':'DEFENDER','Waldlaeuf':'RANGER','Zauberer':'SORCERER','Soldat':'SOLDIER',
 'Piratenkpt':'SWASHBUCKLER','Titanentgr':'TITAN SLAYER','Schwertmag':'SWORDMAGE',
 'Walkuere':'VALKYRIE','Schatzjgr':'TREASURE HUNTER',
}
def scifi_en(name):  # JSON-Name -> PDF-Header (engl. Namen, Sonderfall Controller)
    return 'CONTROLLER' if name == 'AI_Controller' else name.replace('_', ' ').upper()

def find_header(lines, en):
    """Findet die Header-Zeile (Index) eines Archetyps: passende Großbuchstaben-Zeile,
    validiert durch eine 'ATTRIBUTES'-Zeile innerhalb der nächsten 15 Zeilen
    (schließt z.B. das Kleriker-Edge 'Champion:' aus)."""
    for i, ln in enumerate(lines):
        if re.match(rf'^\s*{re.escape(en)}\b', ln) and ':' not in ln.split(en, 1)[-1][:3]:
            if any('ATTRIBUTES' in lines[j] for j in range(i, min(i + 16, len(lines)))):
                return i
    return None

def parse_sheet(lines, hi):
    """Liest Attribut-/Fertigkeitswürfel ab Header-Index hi bis zum Block-Ende
    (erste 'dvances'/'RANK:'-Zeile, max. +42 Zeilen)."""
    attrs, skills = {}, {}
    for ln in lines[hi:hi + 42]:
        if 'dvances' in ln or 'RANK:' in ln:
            break
        low = ln.lower()
        for en, de in ATTR.items():
            if de not in attrs:
                m = re.search(rf'\b{en}\s+d(\d+)', low)
                if m: attrs[de] = int(m.group(1))
        for en in sorted(SKILL, key=len, reverse=True):
            de = SKILL[en]
            if de in skills: continue
            pat = en.replace('.', r'\.').replace(' ', r'\s+')
            m = re.search(rf'\b{pat}\s+d(\d+)', low)
            if m: skills[de] = int(m.group(1))
    return attrs, skills

def parse_german_sheets(path):
    """Deutscher Bogen (Deadlands US85040): {HEADER_UPPER: (attrs, skills)}.
    Würfel als 'Name W8'. Trennt Blöcke an 40-`=`-Linien (NICHT 27-`=` Titel → {35,}).
    Normalisiert 'Sprache (Englisch)'→'Sprache' (Setting hat nur generisches Sprache)."""
    text = open(path, encoding='utf-8').read()
    parts = re.split(r'={35,}\n', text)
    blocks = {}
    i = 1
    while i < len(parts) - 1:
        header = parts[i].strip().splitlines()[0].strip().upper()
        body = parts[i + 1]
        attrs, skills = {}, {}
        section = None
        for ln in body.splitlines():
            s2 = ln.strip()
            if s2 in ('ATTRIBUTE', 'FERTIGKEITEN', 'HANDICAPS', 'TALENTE', 'AUSRÜSTUNG'):
                section = s2; continue
            if s2.startswith('AUFSTIEGE'):
                section = None; continue
            if not s2:
                continue
            mm = re.match(r'(.+?)\s+W(\d+)', s2)
            if not mm:
                continue
            nm, val = mm.group(1).strip(), int(mm.group(2))
            if section == 'ATTRIBUTE':
                attrs[nm] = val
            elif section == 'FERTIGKEITEN':
                if nm.startswith('Sprache'): nm = 'Sprache'
                skills[nm] = val
        blocks[header] = (attrs, skills)
        i += 2
    return blocks

def fill(setting, name, jsonpath, lines, en):
    hi = find_header(lines, en)
    if hi is None:
        w(f"  {name:22} KEIN PDF-Header für '{en}' gefunden"); return
    sheet_a, sheet_s = parse_sheet(lines, hi)
    if not sheet_a:
        w(f"  {name:22} kein Attributblock geparst (Header Z~{hi+1})"); return
    apply_gaps(setting, name, jsonpath, sheet_a, sheet_s)

def apply_gaps(setting, name, jsonpath, sheet_a, sheet_s):
    """Hebt Attribute/Fertigkeiten per Zusatz-Aufstieg auf Bogenwerte an (Seasoned-Cap <8)."""
    s = d.Sitzung(setting, name)
    if not s.controller.lade_charakter_von_json(jsonpath):
        w(f"  {name}: LADEN FEHLGESCHLAGEN"); return
    ch = s.ch
    def ausgeg(): return round(ch.aufstiege_gesamt - ch.verbleibende_aufstiege, 2)
    start_rang, start_aus = ch.rang, ausgeg()
    filled, skipped = [], []

    for de, tgt in sheet_a.items():
        while didx(ch.attribute[de].wert) < didx(tgt):
            if ausgeg() + 1.0 >= 8.0: skipped.append(f"Attr {de}->d{tgt}(Cap)"); break
            if ch.verbleibende_aufstiege < 1.0: increase_aufstiege(ch)
            b = ch.attribute[de].wert
            s.attribut(de, nur_freie_punkte=False)
            if ch.attribute[de].wert == b: skipped.append(f"Attr {de} stuck@d{b}"); break
            filled.append(f"{de} d{b}->d{ch.attribute[de].wert}")

    for de, tgt in sheet_s.items():
        if de not in ch.fertigkeiten: continue
        f = ch.fertigkeiten[de]; guard = 0
        while guard < 8:
            guard += 1
            untrained = f.wuerfel.modifier < 0
            cur_idx = -1 if untrained else didx(f.wuerfel.value)
            if cur_idx >= didx(tgt): break
            if ausgeg() + 0.5 >= 8.0: skipped.append(f"Skill {de}->d{tgt}(Cap)"); break
            if ch.verbleibende_aufstiege < 0.5: increase_aufstiege(ch)
            nxt = 4 if untrained else DIE[min(didx(f.wuerfel.value) + 1, 4)]
            b = (f.wuerfel.value, f.wuerfel.modifier)
            s.fertigkeit_mit_aufstieg(de, nxt)
            if (f.wuerfel.value, f.wuerfel.modifier) == b: skipped.append(f"Skill {de} stuck"); break
            akt = '(akt)' if b[1] < 0 and f.wuerfel.modifier == 0 else ''
            filled.append(f"{de}{akt}->d{f.wuerfel.value}")

    if filled or skipped:
        s.speichern(jsonpath)
    tag = '' if ch.rang == start_rang else f'  <<{start_rang}->{ch.rang}'
    w(f"  {name:22} aus {start_aus}->{ausgeg()} rang={ch.rang}{tag}")
    if filled:  w(f"      + {filled}")
    if skipped: w(f"      ~ offen: {skipped}")

PDF = {'SciFi Kompendium': 'Texte/Science_Fiction_Companion_Archetypes_(SWADE).txt',
       'Fantasy Kompendium': 'Texte/SW Fantasy Kompendium Archetypen.txt'}
PREFIX = {'SciFi Kompendium': 'SciFi_Kompendium', 'Fantasy Kompendium': 'Fantasy_Kompendium'}
import glob
for setting in ['SciFi Kompendium', 'Fantasy Kompendium']:
    w(f"\n===== {setting} =====")
    lines = open(PDF[setting], encoding='utf-8').read().splitlines()
    pref = PREFIX[setting]
    files = sorted(glob.glob(f'chars/Archetypen/Archetyp_{pref}_*.json'))
    for jp in files:
        if '_backup' in jp: continue
        name = os.path.basename(jp).replace(f'Archetyp_{pref}_', '').replace('_A.json', '')
        en = FK_EN.get(name) if setting == 'Fantasy Kompendium' else scifi_en(name)
        if not en:
            w(f"  {name}: kein EN-Mapping"); continue
        try:
            fill(setting, name, jp, lines, en)
        except BaseException as e:
            w(f"  {name}: CRASH {e!r}"); w(traceback.format_exc())

# ── Deadlands (deutscher Bogen, Header = Name in Großbuchstaben) ──
DL_PDF = 'Texte/US85040PDF_Deadlands_Archetypen-Set_meta.txt'
w("\n===== Deadlands =====")
dl_blocks = parse_german_sheets(DL_PDF)
for jp in sorted(glob.glob('chars/Archetypen/Archetyp_Deadlands_*.json')):
    if '_backup' in jp: continue
    name = os.path.basename(jp).replace('Archetyp_Deadlands_', '').replace('_A.json', '')
    block = dl_blocks.get(name.upper())
    if not block:
        w(f"  {name}: kein PDF-Block"); continue
    try:
        apply_gaps('Deadlands', name, jp, block[0], block[1])
    except BaseException as e:
        w(f"  {name}: CRASH {e!r}"); w(traceback.format_exc())

LOG.close()
print("GAPFILL DONE")
