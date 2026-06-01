# -*- coding: utf-8 -*-
"""Test fuer 'Der Beste' Edge: muss Kraftobergrenze 1/3 -> 1/2 der SKP heben."""
import sys
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
import functions.superkraft_funktionen as sf

PASS, FAIL = [], []

def check(name, actual, expected):
    ok = actual == expected
    (PASS if ok else FAIL).append(f"{name}: actual={actual!r} expected={expected!r}")
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {actual!r} == {expected!r}")

# ---------------------------------------------------------------
# Test 1: Stufe III ohne Der Beste -> OG = 15 (1/3 von 45)
# ---------------------------------------------------------------
s = d.Sitzung('Superkräfte Kompendium', 'Test_DB_1')
sf.setze_machtstufe(s.ch, 'III')
check("T1.1 machtstufe", s.ch.machtstufe, 'III')
check("T1.2 SKP gesamt", s.ch.superkraft_punkte_gesamt, 45)
check("T1.3 OG ohne Der Beste (Stufe III)", s.ch.kraftobergrenze, 15)
check("T1.4 selected_talente leer", s.ch.selected_talente, [])

# ---------------------------------------------------------------
# Test 2: 'Der Beste' hinzufuegen -> OG 15 -> 22 (1/2 von 45)
# ---------------------------------------------------------------
s.ch.selected_talente.append('Der Beste')
check("T2.1 Der Beste in selected_talente", 'Der Beste' in s.ch.selected_talente, True)
check("T2.2 OG nach Hinzufuegen", s.ch.kraftobergrenze, 22)

# ---------------------------------------------------------------
# Test 3: 'Der Beste' entfernen -> OG 22 -> 15
# ---------------------------------------------------------------
s.ch.selected_talente.remove('Der Beste')
check("T3.1 Der Beste entfernt", 'Der Beste' in s.ch.selected_talente, False)
check("T3.2 OG nach Entfernen", s.ch.kraftobergrenze, 15)

# ---------------------------------------------------------------
# Test 4: setze_machtstufe() mit Der Beste bereits gesetzt
#         (Reihenfolge: Edge erst, dann Stufe) -> OG = 22
# ---------------------------------------------------------------
s2 = d.Sitzung('Superkräfte Kompendium', 'Test_DB_4')
s2.ch.selected_talente.append('Der Beste')
sf.setze_machtstufe(s2.ch, 'III')
check("T4.1 OG nach setze_machtstufe (Der Beste bereits da)", s2.ch.kraftobergrenze, 22)

# ---------------------------------------------------------------
# Test 5: alle 5 Stufen mit Der Beste (1/2 der SKP)
# ---------------------------------------------------------------
expected_og = {'I': 7, 'II': 15, 'III': 22, 'IV': 30, 'V': 37}
for stufe, want in expected_og.items():
    s3 = d.Sitzung('Superkräfte Kompendium', f'Test_DB_5_{stufe}')
    s3.ch.selected_talente.append('Der Beste')
    sf.setze_machtstufe(s3.ch, stufe)
    check(f"T5.{stufe} OG mit Der Beste (Stufe {stufe})", s3.ch.kraftobergrenze, want)

# ---------------------------------------------------------------
# Test 6: alle 5 Stufen ohne Der Beste (1/3 der SKP) — Regression
# ---------------------------------------------------------------
expected_og_default = {'I': 5, 'II': 10, 'III': 15, 'IV': 20, 'V': 25}
for stufe, want in expected_og_default.items():
    s4 = d.Sitzung('Superkräfte Kompendium', f'Test_DB_6_{stufe}')
    sf.setze_machtstufe(s4.ch, stufe)
    check(f"T6.{stufe} OG ohne Der Beste (Stufe {stufe})", s4.ch.kraftobergrenze, want)

# ---------------------------------------------------------------
# Test 7: jetzt kann Fernkampfangriff 20 SKP bei Stufe III gewaehlt werden
#         (Feuervogel-Bogen Workaround)
# ---------------------------------------------------------------
s5 = d.Sitzung('Superkräfte Kompendium', 'Test_DB_7')
sf.setze_machtstufe(s5.ch, 'III')
res_ohne = sf.waehle_superkraft(s5.ch, 'Fernkampfangriff', 20)
check("T7.1 20 SKP ohne Der Beste (erwartet ueber_obergrenze)", res_ohne, 'ueber_obergrenze')

s5.ch.selected_talente.append('Der Beste')
res_mit = sf.waehle_superkraft(s5.ch, 'Fernkampfangriff', 20)
check("T7.2 20 SKP mit Der Beste (erwartet True)", res_mit, True)

# ---------------------------------------------------------------
# Zusammenfassung
# ---------------------------------------------------------------
print()
print(f"== {'ALLE TESTS OK' if not FAIL else f'{len(FAIL)} FEHLER'} ==")
print(f"  Pass: {len(PASS)}, Fail: {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print(f"  FAIL: {f}")
    sys.exit(1)
