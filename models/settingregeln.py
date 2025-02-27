# data/settingregeln.py

from kivy.properties import BooleanProperty
from kivy.event import EventDispatcher

class SettingRegeln(EventDispatcher):
    dynamischer_rueckschlag = BooleanProperty(False)
    entschlossenheit = BooleanProperty(False)
    fanatiker = BooleanProperty(False)
    fertigkeitsspezialisierungen = BooleanProperty(False)
    fieser_schaden = BooleanProperty(False)
    geborener_held = BooleanProperty(False)
    grosse_abenteuer = BooleanProperty(False)
    helden_sterben_nie = BooleanProperty(False)
    keine_machtpunkte = BooleanProperty(False)
    kreativer_kampf = BooleanProperty(False)
    mehr_fertigkeitspunkte = BooleanProperty(False)
    mehr_sprachen = BooleanProperty(False)
    narrenglueck = BooleanProperty(False)
    schnelle_genesung = BooleanProperty(False)
    schwere_entscheidungen = BooleanProperty(False)
    ungepanzerter_held = BooleanProperty(False)
    wundobergrenze = BooleanProperty(False)
    strahlschablone = BooleanProperty(False)
    große_hoehen = BooleanProperty(False)
    verrat = BooleanProperty(False)
    schwierige_heilung = BooleanProperty(False)
    freizeit = BooleanProperty(False)
    riesige_feinde = BooleanProperty(False)
    schurkische_entschlossenheit = BooleanProperty(False)

    def to_dict(self):
        return {
            'dynamischer_rueckschlag': self.dynamischer_rueckschlag,
            'entschlossenheit': self.entschlossenheit,
            'fanatiker': self.fanatiker,
            'fertigkeitsspezialisierungen': self.fertigkeitsspezialisierungen,
            'fieser_schaden': self.fieser_schaden,
            'geborener_held': self.geborener_held,
            'grosse_abenteuer': self.grosse_abenteuer,
            'helden_sterben_nie': self.helden_sterben_nie,
            'keine_machtpunkte': self.keine_machtpunkte,
            'kreativer_kampf': self.kreativer_kampf,
            'mehr_fertigkeitspunkte': self.mehr_fertigkeitspunkte,
            'mehr_sprachen': self.mehr_sprachen,
            'narrenglueck': self.narrenglueck,
            'schnelle_genesung': self.schnelle_genesung,
            'schwere_entscheidungen': self.schwere_entscheidungen,
            'ungepanzerter_held': self.ungepanzerter_held,
            'wundobergrenze': self.wundobergrenze,
            'strahlschablone': self.strahlschablone,
            'große_hoehen': self.große_hoehen,
            'verrat': self.verrat,
            'schwierige_heilung': self.schwierige_heilung,
            'freizeit': self.freizeit,
            'riesige_feinde,': self.riesige_feinde,
            'schurkische_entschlossenheit': self.schurkische_entschlossenheit
        }

    def from_dict(self, data):
        self.dynamischer_rueckschlag = data.get('dynamischer_rueckschlag', False)
        self.entschlossenheit = data.get('entschlossenheit', False)
        self.fanatiker = data.get('fanatiker', False)
        self.fertigkeitsspezialisierungen = data.get('fertigkeitsspezialisierungen', False)
        self.fieser_schaden = data.get('fieser_schaden', False)
        self.geborener_held = data.get('geborener_held', False)
        self.grosse_abenteuer = data.get('grosse_abenteuer', False)
        self.helden_sterben_nie = data.get('helden_sterben_nie', False)
        self.keine_machtpunkte = data.get('keine_machtpunkte', False)
        self.kreativer_kampf = data.get('kreativer_kampf', False)
        self.mehr_fertigkeitspunkte = data.get('mehr_fertigkeitspunkte', False)
        self.mehr_sprachen = data.get('mehr_sprachen', False)
        self.narrenglueck = data.get('narrenglueck', False)
        self.schnelle_genesung = data.get('schnelle_genesung', False)
        self.schwere_entscheidungen = data.get('schwere_entscheidungen', False)
        self.ungepanzerter_held = data.get('ungepanzerter_held', False)
        self.wundobergrenze = data.get('wundobergrenze', False)
        self.strahlschablone = data.get('strahlschablone', False)
        self.große_hoehen = data.get('große_hoehen', False)
        self.verrat = data.get('verrat', False)
        self.schwierige_heilung = data.get('schwierige_heilung', False)
        self.freizeit = data.get('freizeit', False)
        self.riesige_feinde = data.get('riesige_feinde,', False)
        self.schurkische_entschlossenheit = data.get('schurkische_entschlossenheit', False)
