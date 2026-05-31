import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/harsk_trace.txt','w',encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()
soll = {
 'attribute':{'Geschicklichkeit':8,'Konstitution':8,'Stärke':6,'Verstand':6,'Willenskraft':6},
 'fertigkeiten':{'Allgemeinwissen':4,'Athletik':4,'Heilen':4,'Heimlichkeit':6,'Kämpfen':6,
                 'Schießen':8,'Überleben':8,'Überreden':4,'Wahrnehmung':6},
 'handicaps':['Angewohnheit_leicht','Dünnhäutig_leicht','Misstrauisch_leicht','Schwur_leicht',
             'Rüstungsbeschränkung_mittelschwer'],  # auto durch Waldläufer-Klassentalent
 'talente':['Waldläufer','Naturbursche',
            'Erzfeind','Bevorzugtes Gelände','Wildnis durchqueren'],  # auto durch Waldläufer
 'maechte':[],
}
try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder','Harsk', protokoll='logs/harsk.log')
    m('1 Waldläufer: %s'%s.pathfinder_klassentalent('Waldläufer', ignore_voraussetzungen=True)['ok'])
    # Rüstungsbeschränkung_mittelschwer kommt auto vom Waldläufer-Talent → nicht manuell hinzufügen
    for h in ['Angewohnheit_leicht','Dünnhäutig_leicht','Misstrauisch_leicht','Schwur_leicht']:
        s.handicap(h)
    m('2 hc gesamt=%d'%s.ch.gesamt_handicap_punkte)
    s.volk('Zwerg')
    m('3 Zwerg ok | Konstitution-Start=%d (Eiserne Konst.)'%s.ch.attribute['Konstitution'].wuerfel.value)
    for a,z in soll['attribute'].items(): s.attribut_auf(a,z)
    for a,z in soll['attribute'].items():
        while s.ch.attribute[a].wuerfel.value<z and s.ch.verbleibende_handicap_punkte>0:
            vor=s.ch.attribute[a].wuerfel.value; s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value==vor: break
    m('5 attribute rest-attr=%d rest-hc=%d'%(s.ch.verbleibende_attributsteigerungen,s.ch.verbleibende_handicap_punkte))
    for f,z in soll['fertigkeiten'].items(): s.fertigkeit_auf(f,z)
    m('6 rest-fert=%d rest-hc=%d'%(s.ch.verbleibende_fertigkeitssteigerungen,s.ch.verbleibende_handicap_punkte))
    r=s.talent('Naturbursche', ignore_voraussetzungen=True); m('7 Naturbursche ok=%s kostenart=%s rest-hc=%d'%(r['ok'],r['kostenart'],s.ch.verbleibende_handicap_punkte))
    m('   selected_talente=%s'%list(s.ch.selected_talente))
    # Profil
    s.ch.profil_daten['Sprachen']='Gemeinsprache, Goblinisch, Sylvanisch, Zwergisch'
    s.ch.profil_daten['Konzept']='Waldläufer'
    # Ausrüstung
    kauf=[('Handaxt',2),('Schwere Armbrust',1),('Bolzen (10)',2),('Ledertunika',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1),('Kletterausrüstung',1),('Verstrickungsbeutel',1)]
    for n,az in kauf:
        if n in s.ch.ausruestung: m('9 kaufen %dx %s: %s'%(az,n,s.kaufen(n,anzahl=az)['ok']))
        else: s.notiz('Ausrüstung "%s" nicht im Katalog'%n); m('9 FEHLT %s'%n)
    s.notiz('Handbeil = als "Handaxt" gekauft (Stä+W6); 2x = Handbeil + Sigurs Handbeil')
    for fx in ['beschlagene Lederrüstung (+2) – Katalog hat nur einfaches Leder']:
        s.notiz('FEHLENDE/ABWEICHENDE AUSRÜSTUNG: %s'%fx)
    s.ch.berechne_abgeleitete_werte()
    m('ERGEBNIS Parade=%s Robustheit=%s Bewegung=%s Bennys=%s Vermögen=%s'%(s.ch.parade,s.ch.robustheit,s.ch.bewegungsweite,s.ch.bennys,s.ch.vermoegen))
    m('  (Bogen: Parade5, Robustheit8(2), Bewegung5, Bennys3, 34GM)')
    diff=s.diff(soll); m('DIFF: '+str(diff['abweichungen']))
    m('SPEICHERN: '+str(s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Waldläufer_Harsk_A.json')))
    b=s.bericht('logs/harsk_bericht.json'); m('punkte=%s anomalien=%d'%(b['endzustand']['punkte'],b['anomalien_anzahl']))
except BaseException as e:
    m('CRASH: %r\n%s'%(e,traceback.format_exc()))
tlog.close()
