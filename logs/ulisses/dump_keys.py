import sys, os, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

OUT = 'logs/ulisses'
os.makedirs(OUT, exist_ok=True)

for setting in ['SWAE', 'HeXXen 1773', 'Savage Aventurien']:
    s = d.Sitzung(setting, 'KeyCheck')
    keys = {
        'handicaps':    sorted(s.ch.handicaps),
        'talente':      sorted(s.ch.talente),
        'maechte':      sorted(s.ch.maechte),
        'ausruestung':  sorted(s.ch.ausruestung),
        'voelker':      sorted(s.ch.voelker),
        'fertigkeiten': sorted(s.ch.fertigkeiten),
        'attribute':    sorted(s.ch.attribute),
    }
    fname = setting.replace(' ', '_') + '_keys.json'
    with open(f'{OUT}/{fname}', 'w', encoding='utf-8') as fh:
        json.dump(keys, fh, ensure_ascii=False, indent=1)
    print(f'WROTE {fname}: ha={len(keys["handicaps"])} t={len(keys["talente"])} '
          f'm={len(keys["maechte"])} g={len(keys["ausruestung"])} v={len(keys["voelker"])}')
