import sys, json
sys.path.insert(0,'logs')
from soll_ist_ausruestung import (parse_german_gear, find_archetype_in_bogen,
    resolve_item, SETTING_TO_BOGEN)
from check_fehlende_ausruestung import load_settings
from check_pdf_gear import split_gear_items
import re
from pathlib import Path

settings=load_settings()
keys=settings.get('Deadlands',{}).get('ausruestung_keys',set())
bogen=parse_german_gear(SETTING_TO_BOGEN['Deadlands'])

for f in sorted(Path('chars/Archetypen').glob('Archetyp_Deadlands_*.json')):
    data=json.load(open(f,encoding='utf-8'))
    name=data.get('profil_daten',{}).get('Name','?')
    inv=(data.get('selected_allgemeine_ausruestung',[])+data.get('selected_waffen',[])+
         data.get('selected_ruestungen',[])+data.get('selected_schilde',[])+
         [k for k,v in data.get('selected_elements',{}).get('ausruestung',{}).items() if v.get('ausgewaehlt')])
    inv_l={x.lower() for x in inv}
    ak=find_archetype_in_bogen(name,bogen)
    if not ak: 
        print(f"{name}: KEIN BOGEN"); continue
    items=set(split_gear_items(bogen[ak]))
    items={x for x in items if not re.match(r'^\$?\d+$',x.strip()) and x.lower() not in ('none','keine','—')}
    offen=set(); katalog=[]
    for it in items:
        st,key=resolve_item(it,keys,set(inv),inv_l)
        if st=='OFFEN': offen.add(key)
        elif st=='KATALOG': katalog.append(it)
    print(f"=== {name} ===")
    print("  OFFEN:", sorted(offen))
    if katalog: print("  KATALOG:", katalog)
