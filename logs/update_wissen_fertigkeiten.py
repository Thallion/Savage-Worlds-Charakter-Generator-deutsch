"""Savage Aventurien: Wissens-Fertigkeiten umstellen.

Loescht: Geisteswissenschaften, Naturwissenschaften, Verrueckte Wissenschaft, Okkultismus
Hinzufuegt: Wissen (Geschichtswissen), Wissen (Goetter & Kulte),
            Wissen (Sagen & Legenden), Wissen (Magie & Sphaerenkunde),
            Wissen (Rechtskunde)

Mappings:
  - Geisteswissenschaften -> Wissen (Geschichtswissen)  (DSA: Wissen-Geist)
  - Naturwissenschaften  -> Wissen (Magie & Sphaerenkunde)  (DSA: Wissen-Magie)
  - Okkultismus          -> Wissen (Magie & Sphaerenkunde)  (DSA: Wissen-Magie)
  - Verrueckte Wissenschaft -> LOESCHEN (kein DSA-Konzept)
"""
import json
import os

SETTING_PFAD = 'settings/Savage Aventurien.json'


def main():
    with open(SETTING_PFAD, 'r', encoding='utf-8') as f:
        s = json.load(f)

    fd = s.get('fertigkeiten_daten', {})

    # Neue Wissens-Fertigkeiten anlegen (alle regierendes Attribut: Verstand)
    neue_wissen = {
        'Wissen (Geschichtswissen)':     ['Verstand'],
        'Wissen (Götter & Kulte)':       ['Verstand'],
        'Wissen (Sagen & Legenden)':     ['Verstand'],
        'Wissen (Magie & Sphärenkunde)': ['Verstand'],
        'Wissen (Rechtskunde)':          ['Verstand'],
    }
    for n, attr in neue_wissen.items():
        if n not in fd:
            fd[n] = attr
            print(f'  + {n}: {attr}')
        else:
            print(f'  = {n} bereits vorhanden')

    # Loeschen
    zu_loeschen = ['Geisteswissenschaften', 'Naturwissenschaften',
                   'Okkultismus', 'Verrückte Wissenschaft']
    for n in zu_loeschen:
        if n in fd:
            del fd[n]
            print(f'  - {n} entfernt')
        else:
            print(f'  - {n} war nicht vorhanden')

    # Voraussetzungen und Beschreibungen in Talenten aktualisieren
    # Reihenfolge wichtig: Erst Okkultismus -> Wissen (Magie), dann Geisteswiss. -> Wissen (Gesch.)
    mapping = {
        'Okkultismus': 'Wissen (Magie & Sphärenkunde)',
        'Geisteswissenschaften': 'Wissen (Geschichtswissen)',
        'Naturwissenschaften': 'Wissen (Magie & Sphärenkunde)',
    }
    talente = s.get('talente', {})
    counts = {'Okkultismus': 0, 'Geisteswissenschaften': 0, 'Naturwissenschaften': 0}
    for tname, tdaten in talente.items():
        if not isinstance(tdaten, dict):
            continue
        # Voraussetzungen (Liste)
        v = tdaten.get('voraussetzungen', [])
        if isinstance(v, list):
            for i, eintrag in enumerate(v):
                for old, new in mapping.items():
                    if old in eintrag:
                        v[i] = eintrag.replace(old, new)
                        counts[old] += 1
        # Beschreibungen (Strings)
        for feld in ('beschreibung', 'auswirkung'):
            text = tdaten.get(feld, '')
            if isinstance(text, str):
                for old, new in mapping.items():
                    if old in text:
                        text = text.replace(old, new)
                        counts[old] += 1
                tdaten[feld] = text

    print()
    print('Voraussetzungs-Ersetzungen:')
    for k, c in counts.items():
        print(f'  {k} -> {mapping[k]}: {c}x')

    # Speichern
    with open(SETTING_PFAD, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    print()
    print(f'Gespeichert: {SETTING_PFAD}')

    # Verifikation
    print()
    print('Verifikation:')
    text = json.dumps(s, ensure_ascii=False)
    for old in mapping:
        rest = text.count(old)
        print(f'  Rest-Referenzen auf "{old}": {rest}x')
    for n in neue_wissen:
        c = text.count(n)
        print(f'  Referenzen auf "{n}": {c}x')


if __name__ == '__main__':
    main()
