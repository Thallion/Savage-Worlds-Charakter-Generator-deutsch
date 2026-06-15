# -*- coding: utf-8 -*-
"""
Phase 2 der Savage-Pathfinder-Sanierung — VOLLSTÄNDIGER Seasoned-Build der 18 Set-2/3-Archetypen.

Basis: committete NOVICE-JSONs (= Novice-Karte, verifiziert). Es werden die Novice->Seasoned-
DELTAS als Aufstiege angewandt:
  1. char_gen abschließen
  2. Trait-Anhebungen auf Seasoned-Werte  (Texte/SWPF_Archetype_Cards_target.json)
  3. neue Seasoned-EDGES                    (Texte/SWPF_Archetype_Cards_edges.json, EN->DE unten)
  4. neue Seasoned-MÄCHTE                   (freier Slot, sonst 'Neue Mächte'-Aufstieg)
Unsichere EN->DE-Begriffe werden NICHT substituiert, sondern als MISSING gemeldet.
Idempotent (fügt nur hinzu / hebt nur an), Seasoned-Cap < 8 Aufstiege.
"""
import sys, json, glob, re
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

TRAITS = json.load(open('Texte/SWPF_Archetype_Cards_target.json', encoding='utf-8'))
EDGES = json.load(open('Texte/SWPF_Archetype_Cards_edges.json', encoding='utf-8'))

EDGE_MAP = {
 'arcane archer': 'Arkaner Bogenschütze', 'assassin': 'Assassine', 'banner': 'Banner',
 'brawler': 'Schläger', 'champion': 'Heiliger Champion', 'channeling': 'Kanalisieren',
 'command': 'Anführer', 'common bond': 'Lebensband', 'deadly blow': 'Tödlicher Hieb',
 'discovery': 'Entdeckung', 'dragon disciple': 'Drachenjünger', 'duelist': 'Duellant',
 'extraction': 'Rückzug', 'first strike': 'Erstschlag', 'great luck': 'Großes Glück',
 'holy warrior': 'Heiliger/Unheiliger Krieger', 'loremaster': 'Wissenshüter',
 'menacing': 'Bedrohlich', 'mystic power': 'Mystische Kräfte', 'mystic powers': 'Mystische Kräfte',
 'powerful blow': 'Kraftvoller Schlag', 'revelation': 'Offenbarung', 'trademark weapon': 'Lieblingswaffe',
 # unsicher -> bewusst NICHT gemappt (MISSING): bane, enhance, hex, trapping
}
POWER_MAP = {
 'boost/lower trait': 'Eigenschaft erhöhen/senken', 'burst': 'Flächenschlag',
 'detect/conceal arcana': 'Arkanes entdecken/verbergen', 'dispel': 'Aufheben',
 'environmental': 'Schutz vor Naturgewalten', 'fear': 'Furcht', 'protection': 'Schutz',
 'smite': 'Kriegersegen', 'stun': 'Betäuben', 'deflection': 'Abwehren', 'healing': 'Heilung',
 'burrow': 'Graben', 'beast friend': 'Tierfreund', 'entangle': 'Verstricken',
 'bolt': 'Geschoss', 'summon ally': 'Verbündeten beschwören', 'light/darkness': 'Licht/Dunkelheit',
 'sloth/speed': 'Trägheit/Beschleunigung', 'relief': 'Linderung', 'sound/silence': 'Geräusch/Stille',
 'speak language': 'Sprachen sprechen',
}

# Feiya: Seasoned-Karte pdftotext-korrupt -> manuell aus Render+Crop (Set 3, Seite 7 unten).
# Korrekte Seasoned-Werte überschreiben die korrupte Auto-Extraktion.
TRAITS.setdefault('Feiya', {})['Seasoned'] = {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 4, 'Allgemeinwissen': 6, 'Kämpfen': 6, 'Heilen': 6, 'Einschüchtern': 6,
                     'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 4, 'Zaubern': 8, 'Heimlichkeit': 4},
}
EDGES.setdefault('Feiya', {})['Seasoned'] = {'powers': ['boost/lower trait', 'burst',
    'detect/conceal arcana', 'dispel', 'protection', 'speak language']}
EDGES['Feiya']['delta'] = {'edges': ['Hex (Cackle)'], 'powers': []}  # Hex(Cackle) bleibt MISSING
DIE = [4, 6, 8, 10, 12]
def didx(v): return DIE.index(v) if v in DIE else 0
def ausgeg(ch): return round(ch.aufstiege_gesamt - ch.verbleibende_aufstiege, 2)
def skill_step_kosten(f):
    """Aufstiegskosten des NÄCHSTEN Fertigkeitsschritts: 1.0 wenn Fertigkeit das regierende
    Attribut erreicht/übersteigt (doppelt), sonst 0.5."""
    fe = f.wuerfel.value + f.wuerfel.modifier
    ae = (f.attribut.wuerfel.value + f.attribut.wuerfel.modifier) if f.attribut else 0
    return 1.0 if fe >= ae else 0.5
def norm(s): return re.sub(r'\s+', ' ', re.sub(r'\(.*?\)', '', s).strip(' .,').lower())

def jpath(stub):
    f = glob.glob(f'chars/Archetypen/Archetyp_Savage_Pathfinder_{stub}_A.json')
    return f[0] if f else None

log = open('logs/spf_seasoned_trace.txt', 'w', encoding='utf-8')
def m(x): log.write(str(x) + '\n'); flush=log.flush()

# Feiya: korrupte Karten-Auto-Extraktion oben durch Render+Crop-Daten ersetzt -> nicht mehr geskippt.
SKIP = set()

for stub in sorted(TRAITS):
    if 'Seasoned' not in TRAITS[stub] or stub in SKIP:
        continue
    jp = jpath(stub)
    if not jp:
        m(f"{stub}: KEINE _A.json"); continue
    s = d.Sitzung('Savage Pathfinder', stub)
    if not s.controller.lade_charakter_von_json(jp):
        m(f"{stub}: LADEN FEHLGESCHLAGEN"); continue
    ch = s.ch
    sea_t = TRAITS[stub]['Seasoned']
    delta = EDGES.get(stub, {}).get('delta', {'edges': [], 'powers': []})
    filled, missing = [], []

    # ── Phase 0: Seasoned-Trait-Lücken ZUERST aus freier Chargen-Währung schließen ──
    # Solange char_gen noch offen ist (Novice-Basis): übrige Attribut-/Fertigkeitspunkte und
    # ungenutzte Handicap-Punkte einsetzen (2 HP/Attribut, 1–2 HP/Fertigkeit), BEVOR Aufstiege
    # fließen. Sonst werden Handicap-Punkte verschenkt (nach char_gen eingefroren).
    if not ch.char_gen_completed:
        for de, tgt in sea_t['attribute'].items():
            while didx(ch.attribute[de].wert) < didx(tgt):
                if ch.verbleibende_attributsteigerungen <= 0 and ch.verbleibende_handicap_punkte < 2:
                    break
                b = ch.attribute[de].wert; s.controller.steigere_attribut(de)
                if ch.attribute[de].wert == b: break
                filled.append(f"{de}(chg)W{ch.attribute[de].wert}")
        for de, tgt in sea_t['fertigkeiten'].items():
            if de not in ch.fertigkeiten: continue
            f = ch.fertigkeiten[de]; g0 = 0
            while g0 < 6:
                g0 += 1
                unt = f.wuerfel.modifier < 0
                cur = -1 if unt else didx(f.wuerfel.value)
                if cur >= didx(tgt): break
                if ch.verbleibende_fertigkeitssteigerungen <= 0 and ch.verbleibende_handicap_punkte < 1:
                    break
                b = (f.wuerfel.value, f.wuerfel.modifier)
                s.controller.steigere_fertigkeit(de, confirm_double_cost=True)
                if (f.wuerfel.value, f.wuerfel.modifier) == b: break
                filled.append(f"{de}(chg)W{f.wuerfel.value}")
        ch.char_gen_completed = True

    # 2. Trait-Anhebungen — verbleibende Lücken per Aufstieg (Seasoned-Cap <8)
    for de, tgt in sea_t['attribute'].items():
        while didx(ch.attribute[de].wert) < didx(tgt) and ausgeg(ch) + 1.0 < 8.0:
            while ch.verbleibende_aufstiege < 1.0: increase_aufstiege(ch)
            b = ch.attribute[de].wert; s.attribut(de, nur_freie_punkte=False)
            if ch.attribute[de].wert == b: break
            filled.append(f"{de}W{ch.attribute[de].wert}")
    for de, tgt in sea_t['fertigkeiten'].items():
        if de not in ch.fertigkeiten: continue
        f = ch.fertigkeiten[de]; g = 0
        while g < 6:
            g += 1
            unt = f.wuerfel.modifier < 0
            cur = -1 if unt else didx(f.wuerfel.value)
            kosten = skill_step_kosten(f)   # 0.5 oder 1.0 (doppelt wenn Fert >= Attribut)
            if cur >= didx(tgt) or ausgeg(ch) + kosten >= 8.0: break
            while ch.verbleibende_aufstiege < kosten: increase_aufstiege(ch)
            nxt = 4 if unt else DIE[min(didx(f.wuerfel.value) + 1, 4)]
            b = (f.wuerfel.value, f.wuerfel.modifier); s.fertigkeit_mit_aufstieg(de, nxt)
            if (f.wuerfel.value, f.wuerfel.modifier) == b: break
            filled.append(f"{de}W{f.wuerfel.value}")

    # 3. neue Seasoned-Edges
    for e in delta.get('edges', []):
        key = EDGE_MAP.get(norm(e))
        if not key:
            missing.append(f"EDGE:{e}"); continue
        if key in ch.selected_talente: continue
        if ausgeg(ch) + 1.0 >= 8.0: missing.append(f"EDGE:{key}(Cap)"); continue
        if ch.verbleibende_aufstiege < 1.0: increase_aufstiege(ch)
        r = s.talent(key, ignore_rang_check=True, ignore_voraussetzungen=True)
        if isinstance(r, dict) and r.get('ok') and key in ch.selected_talente: filled.append(f"E:{key}")
        else: missing.append(f"EDGE:{key}(fail)")

    # 4. Mächte: VOLLE Seasoned-Liste (backfillt auch Novice-Lücken wie fehlendes 'burst')
    sea_powers = EDGES.get(stub, {}).get('Seasoned', {}).get('powers', [])
    for p in sea_powers:
        key = POWER_MAP.get(norm(p))
        if not key:
            missing.append(f"POW:{p}"); continue
        if key in ch.selected_maechte: continue
        if len(ch.selected_maechte) >= (ch.anzahl_maechte or 0):
            if ausgeg(ch) + 1.0 < 8.0:
                if ch.verbleibende_aufstiege < 1.0: increase_aufstiege(ch)
                s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
            if len(ch.selected_maechte) >= (ch.anzahl_maechte or 0):
                missing.append(f"POW:{key}(Slot)"); continue
        r = s.macht(key, ignore_rang_check=True)
        if isinstance(r, dict) and r.get('ok') and key in ch.selected_maechte: filled.append(f"P:{key}")
        else: missing.append(f"POW:{key}(fail)")

    s.speichern(jp)
    m(f"{stub:10} aus={ausgeg(ch):<4} rang={ch.rang:14} +[{', '.join(filled)}]"
      + (f"  MISSING[{', '.join(missing)}]" if missing else ""))

log.close()
print("SPF SET2/3 SEASONED (voll) DONE — siehe logs/spf_seasoned_trace.txt")
