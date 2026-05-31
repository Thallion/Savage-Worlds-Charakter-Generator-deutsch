import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/seoni_trace.txt','w',encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()
soll = {
 'attribute':{'Geschicklichkeit':6,'Konstitution':6,'Stärke':4,'Verstand':8,'Willenskraft':8},
 'fertigkeiten':{'Allgemeinwissen':6,'Athletik':6,'Heimlichkeit':4,'Kämpfen':4,'Okkultismus':6,
                 'Provozieren':4,'Reiten':4,'Überreden':4,'Wahrnehmung':6,'Zaubern':8},
 'handicaps':['Neugierig','Zögerlich','Loyal',
             'Behindernde Rüstung_jede'],  # auto durch AH(Zauberer)/Blutlinie
 'talente':['AH (Zauberer) Arkane Blutlinie','Berechnend','Glück','Neue Mächte'],
 'maechte':['Geschoss','Abwehren','Arkanes entdecken/verbergen','Aufheben'],
}
try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder','Seoni', protokoll='logs/seoni.log')
    m('1 Klassentalent: %s | MP=%d verf_maechte=%d'%(s.pathfinder_klassentalent('AH (Zauberer) Arkane Blutlinie', ignore_voraussetzungen=True)['ok'], s.ch.machtpunkte, s.ch.verfuegbare_maechte))
    # Behindernde Rüstung_jede kommt auto von AH(Zauberer)/Blutlinie → nicht manuell hinzufügen
    for h in ['Neugierig','Zögerlich','Loyal']:
        s.handicap(h)
    s.volk('Mensch')
    s.volk_freies_attribut('Mensch','Verstand')
    s.volk_freies_talent('Mensch','Berechnend', ignore_voraussetzungen=True)
    for a,z in soll['attribute'].items(): s.attribut_auf(a,z)
    for a,z in soll['attribute'].items():
        while s.ch.attribute[a].wuerfel.value<z and s.ch.verbleibende_handicap_punkte>0:
            vor=s.ch.attribute[a].wuerfel.value; s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value==vor: break
    for f,z in soll['fertigkeiten'].items(): s.fertigkeit_auf(f,z)
    for t in ['Glück','Neue Mächte']:
        s.talent(t, ignore_voraussetzungen=True)
    for mm in soll['maechte']:
        s.macht(mm, ignore_rang_check=True)
    s.ch.profil_daten['Sprachen']='Drakonisch, Elfisch, Gemeinsprache, Goblinisch, Sylvanisch'
    s.ch.profil_daten['Konzept']='Zauberer'
    # Ausrüstung
    for n in ['Kampfstab','Dolch','Alchemistenfeuer','Gegengift, Phiole','Abenteurerausrüstung',
              'Schriftrolle: Geschoss','Schriftrolle: Eigenschaft senken']:
        if n in s.ch.ausruestung: s.kaufen(n)
        else: s.notiz('Ausrüstung "%s" nicht im Katalog'%n)
    s.ch.berechne_abgeleitete_werte()
    m('ERGEBNIS: MP=%d Mächte=%s'%(s.ch.machtpunkte, list(s.ch.selected_maechte)))
    m('  Bennys=%s Parade=%s Robustheit=%s Bewegung=%s'%(s.ch.bennys,s.ch.parade,s.ch.robustheit,s.ch.bewegungsweite))
    m('  (Bogen: MP20, 4 Mächte, Bennys4, Parade4(5 Stab), Robustheit5, Bew6)')
    diff=s.diff(soll); m('DIFF: '+str(diff['abweichungen']))
    m('SPEICHERN: '+str(s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Zauberer_Seoni_A.json')))
    b=s.bericht('logs/seoni_bericht.json'); m('punkte=%s anomalien=%d'%(b['endzustand']['punkte'],b['anomalien_anzahl']))
except BaseException as e:
    m('CRASH: %r\n%s'%(e,traceback.format_exc()))
tlog.close()
