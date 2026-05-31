import sys, json, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
import functions.superkraft_funktionen as sf

out = {}
try:
    s = d.Sitzung('Superkräfte Kompendium', 'Probe')
    ch = s.ch
    # real key lists
    for k in ['handicaps', 'talente', 'fertigkeiten', 'voelker']:
        try:
            json.dump(sorted(getattr(ch, k)), open(f'/tmp/r_{k}.json', 'w'), ensure_ascii=False)
        except Exception as e:
            out[f'{k}_ERR'] = repr(e)
    out['attribute'] = list(getattr(ch, 'attribute', {}).keys())
    out['has_superkraefte_attr'] = hasattr(ch, 'superkraefte')
    out['superkraefte_len_after_new'] = len(getattr(ch, 'superkraefte', {}) or {})
    out['has_skp_verbraucht'] = hasattr(ch, 'superkraft_punkte_verbraucht')
    out['has_skp_gesamt'] = hasattr(ch, 'superkraft_punkte_gesamt')
    out['machtstufe_default'] = getattr(ch, 'machtstufe', '<none>')
    out['Superkraefte_in_talente'] = 'Superkräfte' in getattr(ch, 'talente', [])
    out['AH_Superkraefte_in_talente'] = 'Arkaner Hintergrund (Superkräfte)' in getattr(ch, 'talente', [])
    out['rang'] = getattr(ch, 'rang', None)

    # init powers from setting if needed
    setting = json.load(open('settings/Superkräfte Kompendium.json', encoding='utf-8'))
    if not getattr(ch, 'superkraefte', None):
        sf.initialisiere_superkraefte(ch, setting.get('krafte'))
    out['superkraefte_len_after_init'] = len(getattr(ch, 'superkraefte', {}) or {})

    # set power level III
    out['setze_machtstufe_III'] = sf.setze_machtstufe(ch, 'III')
    out['skp_gesamt'] = getattr(ch, 'superkraft_punkte_gesamt', None)
    out['kraftobergrenze'] = getattr(ch, 'kraftobergrenze', None)
    out['skp_verbraucht_start'] = getattr(ch, 'superkraft_punkte_verbraucht', None)

    # try selecting a couple powers
    for nm, ko in [('Schutz', 4), ('Nahkampfangriff', 3), ('Zähigkeit erhöhen', 3)]:
        try:
            out[f'waehle[{nm},{ko}]'] = sf.waehle_superkraft(ch, nm, ko)
        except Exception as e:
            out[f'waehle[{nm},{ko}]_EXC'] = repr(e)
    out['verbleibende_skp'] = sf.get_verbleibende_skp(ch)
    out['selected_superkraefte'] = list(getattr(ch, 'selected_superkraefte', []))

    # one variable-cost check
    kraft = ch.superkraefte.get('Nahkampfangriff')
    out['Nahkampf_hat_variable'] = kraft.hat_variable_kosten() if kraft else None
    out['Nahkampf_feste_kosten'] = kraft.get_feste_kosten() if kraft else None
except BaseException as e:
    out['CRASH'] = repr(e) + '\n' + traceback.format_exc()

json.dump(out, open('/tmp/probe_real.json', 'w'), ensure_ascii=False, indent=1)
print('DONE')
