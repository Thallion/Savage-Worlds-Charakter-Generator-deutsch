import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/sajan_final_trace.txt','w',encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()
soll = {'attribute':{'Geschicklichkeit':8,'Konstitution':8,'Stärke':6,'Verstand':6,'Willenskraft':6},
        'fertigkeiten':{'Athletik':8,'Heimlichkeit':8,'Kämpfen':8,'Einschüchtern':6,'Wahrnehmung':6,'Heilen':4,'Reiten':4,'Allgemeinwissen':4,'Überreden':4},
        'handicaps':['Heroisch','Loyal','Schwur_leicht',
                     'Rüstungsbeschränkung_jede'],  # auto durch Mönch-Klassentalent
        'talente':['Mönch','Flink','Lieblingswaffe',
                   'Waffenloser Schlag','Betäubende Fäuste','Kämpferische Disziplin','Beweglichkeit'],  # auto durch Mönch
        'maechte':[]}
try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder','Sajan', protokoll='logs/sajan.log')
    s.pathfinder_klassentalent('Mönch', ignore_voraussetzungen=True)
    # Rüstungsbeschränkung_jede kommt auto vom Mönch-Klassentalent → nicht manuell hinzufügen
    for h in ['Heroisch','Loyal','Schwur_leicht']:
        s.handicap(h)
    s.volk('Mensch')
    s.volk_freies_attribut('Mensch','Stärke')
    s.volk_freies_talent('Mensch','Flink', ignore_voraussetzungen=True)
    for a,z in soll['attribute'].items(): s.attribut_auf(a,z)
    for a,z in soll['attribute'].items():
        while s.ch.attribute[a].wuerfel.value<z and s.ch.verbleibende_handicap_punkte>0:
            vor=s.ch.attribute[a].wuerfel.value; s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value==vor: break
    for f,z in soll['fertigkeiten'].items(): s.fertigkeit_auf(f,z)
    s.talent('Lieblingswaffe', ignore_voraussetzungen=True)

    # --- PROFIL (Freitext) ---
    s.ch.profil_daten['Sprachen'] = 'Elfisch, Gemeinsprache, Goblinisch, Riesisch'
    s.ch.profil_daten['Konzept']  = 'Mönch'      # Annahme: "Konzept: Klasse" -> Klasse = Mönch
    m('Profil: Sprachen=%r Konzept=%r' % (s.ch.profil_daten.get('Sprachen'), s.ch.profil_daten.get('Konzept')))

    # --- AUSRÜSTUNG ---
    m('Vermögen vor Kauf: %d' % s.ch.vermoegen)
    kaeufe = [('Kurzschwert',1,'= Tempelschwert (Stä+W6)'), ('Shuriken',6,''), ('Krähenfüße',1,''), ('Alchemistenfeuer',3,'')]
    for name, anz, note in kaeufe:
        if name in s.ch.ausruestung:
            r = s.kaufen(name, anzahl=anz)
            m('kaufen %dx %s: ok=%s %s' % (anz, name, r['ok'], note))
        else:
            s.notiz('Ausrüstung "%s" (%dx) nicht im Katalog' % (name, anz)); m('FEHLT: %s'%name)
    # Abenteurerausrüstung direkt kaufen (war zuvor Tippfehler als "Abenteuerausrüstung" notiert)
    if 'Abenteurerausrüstung' in s.ch.ausruestung:
        r = s.kaufen('Abenteurerausrüstung')
        m('kaufen Abenteurerausrüstung: ok=%s' % r['ok'])
    if 'Trank: schwache Heilung' in s.ch.ausruestung:
        r = s.kaufen('Trank: schwache Heilung')
        m('kaufen Trank: schwache Heilung: ok=%s' % r['ok'])
    fehlend = [
        'Tempelschwert (Original-Name; hier als Kurzschwert/Stä+W6 gekauft)',
        'Sonnenstab (nur "Sonnenzepter" im Katalog vorhanden, anderer Gegenstand)',
    ]
    for fx in fehlend:
        s.notiz('FEHLENDE AUSRÜSTUNG (bitte separat anlegen): %s' % fx)
    m('Vermögen nach Kauf: %d (Bogen-Soll Restgeld: 21 GM)' % s.ch.vermoegen)

    s.ch.berechne_abgeleitete_werte()
    m('PARADE=%s BEWEGUNG=%s ROBUSTHEIT=%s' % (s.ch.parade, s.ch.bewegungsweite, s.ch.robustheit))
    diff=s.diff(soll); m('DIFF: '+str(diff['abweichungen']))
    m('SPEICHERN: '+str(s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Mönch_Sajan_A.json')))
    b=s.bericht('logs/sajan_bericht.json'); m('FERTIG anomalien=%d punkte=%s'%(b['anomalien_anzahl'],b['endzustand']['punkte']))
except BaseException as e:
    m('CRASH: %r\n%s'%(e,traceback.format_exc()))
tlog.close()
