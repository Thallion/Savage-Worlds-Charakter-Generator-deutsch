"""Fix verbliebene SPF-Anomalien: Chars abschließen, Aufstiege vergeben, Fehlstellen bezahlen.

Chars: Imrijka, Madda, Marn, Teller, Darla_ohneKlasse, Gnor
Quelle: build_spf_set23_v2.py Berichte + PDF-Primärquellen-Abgleich (Werte bestätigt).
"""
import sys, os, traceback, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
from controllers.charakter_controller import CharakterController
from functions.character_advancement import increase_aufstiege

LOG = open('logs/spf_fix_advance.txt', 'w', encoding='utf-8')
def log(x): LOG.write(str(x)+'\n'); LOG.flush()

FIXES = {
    'Imrijka': {
        'file': 'chars/Archetypen/Archetyp_Savage_Pathfinder_Imrijka_A.json',
        'advances': [
            ('fertigkeit', 'Überleben', 4),   # activation only (W0→W4)
        ],
    },
    'Madda': {
        'file': 'chars/Archetypen/Archetyp_Savage_Pathfinder_Madda_A.json',
        'advances': [
            ('fertigkeit', 'Heimlichkeit', 6),  # W4→W6
        ],
    },
    'Marn': {
        'file': 'chars/Archetypen/Archetyp_Savage_Pathfinder_Marn_A.json',
        'advances': [
            ('talent', 'Rundumschlag'),
        ],
    },
    'Teller': {
        'file': 'chars/Archetypen/Archetyp_Savage_Pathfinder_Teller_A.json',
        'advances': [
            ('fertigkeit', 'Schießen', 4),      # activation (W0→W4)
            ('fertigkeit', 'Heimlichkeit', 6),   # W4→W6
        ],
    },
    'Darla_ohneKlasse': {
        'file': 'chars/Archetypen/Archetyp_Savage_Pathfinder_Darla_ohneKlasse_A.json',
        'advances': [
            ('klassentalent', 'AH (Magier)'),
        ],
    },
    'Gnor': {
        'file': 'chars/Archetypen/Archetyp_Savage_Pathfinder_Gnor_A.json',
        'advances': [
            ('fertigkeit', 'Zaubern', 8),
        ],
    },
    # ── Worlds of Ulisses ──
    'Klara (HeXXen)': {
        'file': 'chars/Archetypen/Archetyp_HeXXen_1773_Klara_A.json',
        'advances': [
            ('fertigkeit', 'Schießen', 6),
            ('fertigkeit', 'Wahrnehmung', 6),
        ],
    },
}

for name, fix in FIXES.items():
    log(f'\n{"="*60}\n{name}\n{"="*60}')
    try:
        ctrl = CharakterController()
        ok = ctrl.lade_charakter_von_json(fix['file'])
        if not ok:
            log(f'  LOAD FAILED: {fix["file"]}')
            continue
        ch = ctrl.charakter
        log(f'  Geladen: AP={ch.verbleibende_attributsteigerungen} FP={ch.verbleibende_fertigkeitssteigerungen} HP={ch.verbleibende_handicap_punkte}/{ch.gesamt_handicap_punkte}')

        # CharGen abschließen (falls noch nicht)
        if not ch.char_gen_completed:
            ch.char_gen_completed = True
            log(f'  char_gen_completed = True')

        # 4 Aufstiege vergeben
        for _ in range(4):
            increase_aufstiege(ch)
        log(f'  Aufstiege: gesamt={ch.aufstiege_gesamt} verbleibend={ch.verbleibende_aufstiege} Rang={ch.rang}')

        # D-Advances anwenden
        for adv in fix['advances']:
            typ = adv[0]
            if typ == 'fertigkeit':
                fname, ziel = adv[1], adv[2]
                w = ch.fertigkeiten[fname].wuerfel
                while w.value < ziel or w.modifier < 0:
                    vor = (w.value, w.modifier)
                    r = ctrl.steigere_fertigkeit(fname, confirm_double_cost=True)
                    log(f'    fertigkeit {fname}: value={w.value} mod={w.modifier} (vor={vor}) rest_auf={ch.verbleibende_aufstiege}')
                    if (w.value, w.modifier) == vor:
                        log(f'    → KEIN Fortschritt, breche ab')
                        break
            elif typ == 'talent':
                tname = adv[1]
                r = ctrl.waehle_talent(tname, ignore_rang_check=True, ignore_voraussetzungen=True)
                log(f'    talent {tname}: ok={bool(r)} rest_auf={ch.verbleibende_aufstiege}')
            elif typ == 'klassentalent':
                tname = adv[1]
                r = ctrl.waehle_pathfinder_kostenloses_talent(tname, ignore_voraussetzungen=True)
                log(f'    klassentalent {tname}: ok={bool(r)} rest_auf={ch.verbleibende_aufstiege}')

        log(f'  Final: Aufst={ch.verbleibende_aufstiege}/{ch.aufstiege_gesamt} Rang={ch.rang}')
        log(f'  Talente: {sorted(ch.selected_talente)}')
        log(f'  Handicaps: {sorted(ch.selected_handicaps)}')

        # Speichern (gleicher Pfad)
        ctrl.speichere_charakter_als_json(fix['file'])
        log(f'  GESPEICHERT: {fix["file"]}')
    except BaseException as e:
        log(f'  CRASH: {e!r}\n{traceback.format_exc()}')

LOG.close()
print('LOG written to logs/spf_fix_advance.txt')
