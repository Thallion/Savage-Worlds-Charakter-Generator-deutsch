#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generiert docs/Savage_Aventurien_Traditionen_Zauber_Mapping.md.

Für jede magische Tradition und jeden Geweihten-Kult: typische DSA-Zauber/Liturgien und die in
diesem Setting zugeordnete SW-Macht. So sehen DSA-Spieler, welche SW-Mächte für sie sinnvoll sind.

Datenquellen:
- SW-Zuordnung: `dsa_trappings` der Mächte in `settings/Savage Aventurien.json` (DSA-Zauber→SW-Macht).
- Traditions-Zuordnung der Zauber: `scripts/grimorum_verbreitung.json` (aus Grimorum Cantiones, Feld
  „Verbreitung"; erzeugt von `extract_grimorum_verbreitung.py`). Datengetrieben für die acht
  Haupttraditionen mit Verbreitungs-Token; „allgemein" → eigene Sektion.
- Sub-Schulen ohne eigenes Verbreitungs-Token (Elementarist, Nekromant, …) und Geweihte/Liturgien
  (im Liber Liturgium göttergebunden ohne Verbreitungs-Feld): kuratierte Signatur-Listen.

Aufruf:  python scripts/gen_traditionen_zauber.py
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "settings", "Savage Aventurien.json")
GRIM = os.path.join(ROOT, "scripts", "grimorum_verbreitung.json")
LIBER = os.path.join(ROOT, "scripts", "liber_herkunft.json")
OUT = os.path.join(ROOT, "docs", "Savage_Aventurien_Traditionen_Zauber_Mapping.md")
OUT2 = os.path.join(ROOT, "docs", "Savage_Aventurien_Tradition_SWMacht_Trappings.md")

# Haupttraditionen mit Grimorum-Verbreitungs-Token (datengetrieben)
TOKEN_TRAD = [
    ("Gildenmagier (Magier)", "Gildenmagier"),
    ("Elfen (Fey)", "Elfen"),
    ("Druiden", "Druiden"),
    ("Hexen", "Hexen"),
    ("Geoden", "Geoden"),
    ("Kristallomanten", "Kristallomanten"),
    ("Scharlatane (Illusionisten)", "Scharlatane"),
    ("Goblinzauberinnen", "Goblinzauberinnen"),
]

# Sub-Schulen / Traditionen ohne eigenes Verbreitungs-Token: kuratierte Signatur-Zauber
SUB_TRAD = {
    "Elementarist": [
        "Ignifaxius", "Aquasphaero", "Brandform", "Gletscherform", "Wirbelform",
        "Elementarer Diener", "Diener der Flammen", "Diener der Erde", "Diener der Wellen",
        "Diener der Wolken", "Meister der Elemente",
    ],
    "Illusionist": [
        "Manus Illusionis", "Oculus Illusionis", "Auris Illusionis", "Aromatis Illusionis",
        "Chamaelioni", "Reflectimago", "Projectimago", "Halluzination", "Doppelgänger",
    ],
    "Nekromant": [
        "Skelettarius", "Untote erschaffen", "Untotenerhebung", "Nekropathia",
        "Pestodem", "Heptagramma", "Bann wider Untote", "Gespräch mit den Toten",
    ],
    "Dämonologe": [
        "Invocatio Maior", "Invocatio Minor", "Invocatio Maxima", "Heptagramma",
        "Pentagramma", "Oktagramma", "Horriphobus", "Pandaemonium",
    ],
    "Schamane": [
        "Befehl des Schamanen", "Furchteinflößende Tiergeister", "Geisterbeschwörung",
        "Tiergestalt (Druide)", "Tiergedanken", "Tiersprache",
    ],
    "Zibilja": [
        "Sandfigur", "Wüstenlauf", "Brandform", "Wirbelform",
    ],
    "Zaubertänzer": [
        "Satuarias Herrlichkeit", "Heiliges Liebesspiel", "Berauschen", "Levthans Feuer",
    ],
    "Alchemist": [
        "Arcanovi", "Sumus Elixiere", "Adamantium", "Manifesto",
    ],
    "Golembauer / Artefaktmagier": [
        "Animatio (Belebung)", "Arcanovi", "Talismanruf", "Custodosigil", "Adamantium",
    ],
    "Barde": [
        "Mondsilberzunge", "Bannbaladin", "Seidenzunge", "Bann der Furcht", "Moralstärkung",
        "Verstecktes Begehren",
    ],
    "Runenschöpfer": [
        "Custodosigil", "Talismanverankerung", "Adamantium", "Talismanruf",
    ],
}

# Anzeige-Reihenfolge & Labels der Götter/Kulte (Liber-Token -> Label)
GOTT_LABELS = [
    ("Praios", "Praios (Sonne, Ordnung, Magieabwehr)"),
    ("Rondra", "Rondra (Kampf, Ehre)"),
    ("Efferd", "Efferd (Meer, Wasser, Wind)"),
    ("Travia", "Travia (Heim, Gastrecht, Treue)"),
    ("Boron", "Boron (Tod, Schlaf, Vergessen)"),
    ("Hesinde", "Hesinde (Wissen, Magie)"),
    ("Firun", "Firun (Winter, Jagd)"),
    ("Tsa", "Tsa (Leben, Wandel, Wiedergeburt)"),
    ("Phex", "Phex (Diebe, Händler, List)"),
    ("Peraine", "Peraine (Heilung, Ackerbau)"),
    ("Ingerimm", "Ingerimm (Feuer, Schmiedekunst)"),
    ("Rahja", "Rahja (Liebe, Rausch, Freude)"),
    ("Aves", "Aves (Reise, Wege)"),
    ("Ifirn", "Ifirn (Barmherzigkeit, Eis)"),
    ("Kor", "Kor (Kampf, Söldner)"),
    ("Nandus", "Nandus (Wissen, Lehre)"),
    ("Swafnir", "Swafnir (Wale, Thorwal, Meer)"),
    ("Angrosch", "Angrosch (Zwergengott)"),
    ("Gravesh", "Gravesh (Orkische Schmiedeglut)"),
    ("Himmelswölfe", "Himmelswölfe (Nivesen-Kult)"),
    ("H’Szint", "H’Szint (Echsen-Kult)"),
    ("Kamaluq", "Kamaluq (Tulamidischer Totenkult)"),
    ("Tairach", "Tairach (Echsen-Blutkult)"),
    ("Zsahh", "Zsahh (Echsen-Kult)"),
    ("H’Ranga", "H’Ranga (Achaz-Kult)"),
    ("Riva", "Riva"),
    ("Namenlos", "Namenloser (Verbotener Kult)"),
]

# Wirkungs-Mapping Liturgie -> SW-Macht (nur die mechanisch abbildbaren; Rest = narrativ).
# SW-Macht-Namen müssen exakt einem Eintrag in d['maechte'] entsprechen (wird geprüft).
LITURGIE_SW = {
    "Aller Welt Freund": "Empathie",
    "Allmacht der Lohe": "Flächenschlag",
    "Anathema": "Fluch",
    "Anrufung der Erdkraft": "Elementarmanipulation",
    "Arcanum Interdictum": "Heiligtum",
    "Argelions Mantel": "Arkaner Schutz",
    "Argelions Spiegel": "Arkaner Schutz",
    "Argelions bannende Hand": "Aufheben",
    "Auge Xeledons, Xeledons helles Licht": "Licht/Dunkelheit",
    "Auge des Händlers": "Arkanes entdecken/verbergen",
    "Auge des Mondes": "Dunkelsicht",
    "Bannfluch des Heiligen Khalid": "Fluch",
    "Begehen der Heiligen Wasser": "Schutz vor Naturgewalten",
    "Bindung der Schlange": "Tierfreund",
    "Birkenzweig": "Heilung",
    "Blendstrahl aus Alveran": "Blenden",
    "Blick in die Flammen": "Ausspähung",
    "Borons süsse Gnade": "Linderung",
    "Das schwarze Fell durch das rote Blut": "Kriegersegen",
    "Des Einen bezaubernder Sphärenklang": "Marionette",
    "Die goldene Hand": "Illusion",
    "Daradors Bann der Schatten": "Licht/Dunkelheit",
    "Eherne Kraft, Lodernder Zorn": "Kriegersegen",
    "Eidechsenhaut": "Schutz",
    "Ein Bild für die Ewigkeit": "Eigenschaft erhöhen/senken",
    "Elementwandlung": "Elementarmanipulation",
    "Entzug von Nandus’ Gaben": "Gedankenleere",
    "Erneuerung des Geborstenen": "Gegenstand verbessern/schaden",
    "Ewige Jugend": "Zeitstopp",
    "Ewiger Wächter": "Untoten Beschwören",
    "Exkommunikation": "Mystisches Eingreifen",
    "Exorzismus": "Verbannen",
    "Feuersegen": "Licht/Dunkelheit",
    "Firuns Zorn": "Flächenschlag",
    "Fluch wider die Ungläubigen": "Fluch",
    "Freundliche Aufnahme": "Empathie",
    "Frieden der Melodie": "Empathie",
    "Fürbitten des heiligen Therbûn": "Heilung",
    "Garafans gleissende Schwingen": "Fliegen",
    "Gebieter der Lava": "Elementarmanipulation",
    "Geburtssegen": "Segen",
    "Geläutert sei Erz und Goldgestein": "Elementarmanipulation",
    "Geschlechterwandel": "Gestaltwandeln",
    "Geteiltes Leid": "Heilung",
    "Gleichklang des Geistes": "Gedankenverbindung",
    "Glückssegen": "Segen",
    "Goldene Rüstung": "Schutz",
    "Grabsegen": "Segen",
    "Grosse Weihe des Heimsteins": "Heiligtum",
    "Grosser Weihesegen der Waffe": "Waffe verbessern",
    "Göttliche Strafe": "Strahl",
    "Göttliche Verständigung": "Gedankenverbindung",
    "Göttliches Zeichen": "Mystisches Eingreifen",
    "Hammer rufen": "Telekinese",
    "Harmoniesegen": "Segen",
    "Hauch Borons": "Schlummer",
    "Hausfrieden": "Heiligtum",
    "Heiliger Befehl": "Marionette",
    "Heiliges Liebesspiel": "Empathie",
    "Heilungssegen": "Heilung",
    "Herbeirufung der Diener des Herrn": "Monster Beschwören",
    "Herbeirufung der Heerscharen des Rattenkindes": "Tier Beschwören",
    "Herr über Feuer und Glut": "Elementarmanipulation",
    "Hilfe in der Not": "Aufspüren",
    "Hoftag der Sprachen": "Sprachen sprechen",
    "Ingerimms Zorn verschone uns": "Schutz vor Naturgewalten",
    "Initiation": "Wiederauferstehung",
    "Innere Ruhe": "Gedankenleere",
    "Khablas Jugend": "Zeitstopp",
    "Khablas makelloser Leib": "Verkleiden",
    "Kleine Segnung des Heimsteins": "Heiligtum",
    "Kleiner Giftbann": "Heilung",
    "Konsekration": "Heiligtum",
    "Kräftigung der Schwachen und Versehrten": "Eigenschaft erhöhen/senken",
    "Levthans Fesseln": "Verstricken",
    "Licht des Herrn": "Licht/Dunkelheit",
    "Licht des verborgenen Pfades": "Licht/Dunkelheit",
    "Mikailspfeil": "Geschoss",
    "Mondsilberzunge": "Empathie",
    "Namenlose Kälte": "Flächenschlag",
    "Namenlose Raserei": "Kriegersegen",
    "Namenloser Zweifel, Namenlose Erleuchtung": "Verwirrung",
    "Namenloses Vergessen": "Gedankenleere",
    "Nemekaths Zwiesprache": "Zwiesprache",
    "Neun Streiche in einem": "Kriegersegen",
    "Objektsegen": "Segen",
    "Objektweihe": "Segen",
    "Peraines Pflanzengespür": "Aufspüren",
    "Phexens Meisterschlüssel": "Verriegeln/Entriegeln",
    "Phexens Nebelleib": "Gestaltwandeln",
    "Phexens Schatten": "Unsichtbarkeit",
    "Phexens Sternenwurf": "Geschoss",
    "Phexens Verteidigung": "Schutz",
    "Phexens wunderbare Verständigung": "Sprachen sprechen",
    "Praios’ Magiebann": "Aufheben",
    "Purgation": "Machtpunkte entziehen",
    "Rahjalinas Farbenspiel": "Illusion",
    "Rahjas Begehren": "Empathie",
    "Rahjas Fest der Freude": "Segen",
    "Rahjas Freiheit": "Linderung",
    "Rahjas Rauschsegen": "Linderung",
    "Rahjas Sinnlichkeit": "Empathie",
    "Ritus der Schlachthilfe": "Kriegersegen",
    "Rondras wundersame Rüstung": "Schutz",
    "Ruf zum Bund wider die Mächte der Finsternis": "Kriegersegen",
    "Ruf zur Ruhe": "Empathie",
    "Schattenlarve": "Illusion",
    "Schlachtgesang": "Kriegersegen",
    "Schlaf des Gesegneten": "Schlummer",
    "Schlangenstab": "Tier Beschwören",
    "Schleichende Fäulnis": "Fluch",
    "Schneesturm": "Flächenschlag",
    "Schnell wie eine Eidechse": "Trägheit/Beschleunigung",
    "Schrifttum ferner Lande": "Sprachen sprechen",
    "Schutzsegen": "Mystisches Eingreifen",
    "Schwindende Zauberkraft": "Machtpunkte entziehen",
    "Seelenbannung": "Verbannen",
    "Seelengefährte": "Tierfreund",
    "Seelenprüfung": "Aufspüren",
    "Segen des heiligen Hlûthar": "Kriegersegen",
    "Segnung der Schlacht": "Kriegersegen",
    "Segnung der stählernen Stirn": "Eigenschaft erhöhen/senken",
    "Segnung des Heims": "Mystisches Eingreifen",
    "Sichere Wanderung im Schnee": "Schutz vor Naturgewalten",
    "Sicht auf Madas Welt": "Arkanes entdecken/verbergen",
    "Sippenfluch": "Fluch",
    "Sternenglanz": "Illusion",
    "Teilung der Wasser": "Elementarmanipulation",
    "Tierempathie": "Tierfreund",
    "Tiergestalt": "Gestaltwandeln",
    "Tranksegen": "Segen",
    "Travias Gebet der sicheren Zuflucht": "Mystisches Eingreifen",
    "Travinians Segen der Schwelle": "Heiligtum",
    "Tsas Lebensschutz": "Heilung",
    "Tsas ewige Jugend": "Zeitstopp",
    "Tsas heiliges Lebensgeschenk": "Wiederauferstehung",
    "Tsas wunderbare Erneuerung": "Heilung",
    "Tsas wundersame Fruchtbarkeit": "Segen",
    "Unverstellter Blick": "Arkanes entdecken/verbergen",
    "Verborgen wie der Neumond": "Unsichtbarkeit",
    "Vertrauter der Flamme": "Verbündeten beschwören",
    "Vertrauter des Felsens": "Verbündeten beschwören",
    "Vertreibung des Dunkelsinns": "Linderung",
    "Wachsamkeit der Gänse": "Mystisches Eingreifen",
    "Waffenfluch": "Fluch",
    "Waliburias Wehr": "Schutz",
    "Weg des Fuchses": "Gestaltwandeln",
    "Weisheitssegen": "Segen",
    "Winterschlaf": "Betäuben",
    "Wundersames Teilen des Martyriums": "Heilung",
    "Wundsegen": "Heilung",
    "Zerschmetternder Bannstrahl": "Verbannen",
    "Zuflucht finden": "Mystisches Eingreifen",
    "Über die Wolken": "Fliegen",
    # --- Nachtrag 2026-06-07: zuvor narrativ, per Auswirkung doch mechanisch abbildbar ---
    "Alte Schuppen": "Gestaltwandeln",
    "Anrufung der Winde": "Elementarmanipulation",
    "Ascandears Hingabe": "Betäuben",
    "Aura der Form": "Aufspüren",
    "Aura des Regenbogens": "Mystisches Eingreifen",
    "Azilas Quellgesang": "Elementarmanipulation",
    "Bishdariels Auge": "Gedankenlesen",
    "Blick der Weberin": "Arkanes entdecken/verbergen",
    "Buchprüfung": "Aufspüren",
    "Canyzeths Weisheit": "Eigenschaft erhöhen/senken",
    "Flagge des Regenbogens": "Mystisches Eingreifen",
    "Fünfte Lobpreisung des Frühlings": "Zeitstopp",
    "Gemeinschaft der treuen Gefährten": "Tierfreund",
    "Gesang der Delphine": "Tierfreund",
    "Gift der Erkenntnis": "Gedankenlesen",
    "Goldener Blick": "Aufspüren",
    "Gott der Götter": "Aufheben",
    "Handwerkssegen": "Eigenschaft erhöhen/senken",
    "Hashnabiths Flehen": "Aufspüren",
    "Heilige Schmiedeglut": "Elementarmanipulation",
    "Lidaris Herz": "Schutz",
    "Lohn der Unverzagten": "Eigenschaft erhöhen/senken",
    "Mannschaftssegen": "Eigenschaft erhöhen/senken",
    "Märtyrersegen": "Eigenschaft erhöhen/senken",
    "Nemekaths Geisterblick": "Arkanes entdecken/verbergen",
    "Nimmermüde Wanderschaft": "Eigenschaft erhöhen/senken",
    "Phexens Augenzwinkern": "Gedankenleere",
    "Reichung des Amethyst": "Linderung",
    "Revolution der Gedanken": "Einfluss",
    "Ruf der Gefährten": "Tier Beschwören",
    "Ruf in Borons Arme": "Schlummer",
    "Schlachtfeld schreitet": "Furcht",
    "Segen der heiligen Ardare": "Verbündeten beschwören",
    "Segen der heiligen Noiona": "Linderung",
    "Segen der heiligen Theria": "Heilung",
    "Segen der heiligen Velvenya": "Eigenschaft erhöhen/senken",
    "Segen des Plättlings": "Elementarmanipulation",
    "Speisung der hungernden Seelen": "Gegenstand beschwören",
    "Sulvas Gnade": "Tierfreund",
    "Swafnirs Fluke": "Elementarmanipulation",
    "Swafnirs Ruhelied": "Empathie",
    "Ucuris Geleit": "Aufspüren",
    "Weihe der letzten Ruhestatt": "Heiligtum",
    "Weisung des Himmels": "Aufspüren",
    "Wille zur Wahrheit": "Einfluss",
    # --- Nachtrag 2: Segen-Sammelmacht + Talisman-Anrufungen (Gegenstand beschwören) ---
    "Bootssegen": "Segen",
    "Dreifacher Saatsegen": "Segen",
    "Efferdsegen": "Segen",
    "Gesegneter Fang": "Segen",
    "Grosser Speisesegen": "Segen",
    "Kälbchensegen": "Segen",
    "Quellsegen": "Segen",
    "Reiches Land": "Segen",
    "Reisesegen": "Segen",
    "Speisesegen": "Segen",
    "Speisung der Bedürftigen": "Segen",
    "Wegzehrung der Heiligen Selma": "Segen",
    "Parinors Vermächtnis": "Segen",
    "Eidsegen": "Segen",
    "Grosser Eidsegen": "Segen",
    "Schutz des Geleges": "Segen",
    "Unterpfand des Heiligen Rhÿs": "Segen",
    "Tsas segensreicher Neuanfang": "Segen",
    "Conagas Ruf": "Heiligtum",
    "Firuns Einsicht": "Gegenstand beschwören",
    "Rahjalinas Kuss": "Gegenstand beschwören",
    "Rahjas Schoss": "Gegenstand beschwören",
    "Rahjas geheiligter Wein": "Gegenstand beschwören",
    "Segenreiches Wasser": "Gegenstand beschwören",
    "Sicherer Weg durch Fels": "Gegenstand beschwören",
    "Ingalfs Alchimie": "Gegenstand beschwören",
    "Seelenschatten": "Arkanes entdecken/verbergen",
    "Runjensweisung": "Aufspüren",
    # --- Nachtrag 3: vermeintlich narrativ, per Volltext doch SW-Macht ---
    "Jagdglück": "Aufspüren",
    "Urischars ordnender Blick": "Aufspüren",
    "Ruf der Ferne": "Aufspüren",
    "Golgaris Zwielicht": "Dunkelsicht",
    "Marbos Geleit": "Ebenenwechsel",
    "Sechs Leben des Mungos": "Trägheit/Beschleunigung",
    "Sternenstaub": "Blenden",
    "Praios’ Mahnung": "Blenden",
    "Bishdariels Warnung": "Furcht",
    "Erzieherische Massnahme der Heiligen Yalsicena": "Fluch",
    "Etilias Gnade": "Fluch",
    "Dorlens Verbrüderung": "Empathie",
    "Vaês Tränen": "Heilung",
    "Therbûns Erkenntnis": "Eigenschaft erhöhen/senken",
    "Blick für das Handwerk": "Eigenschaft erhöhen/senken",
    "Gruss des Versunkenen": "Schutz vor Naturgewalten",
    "Anrufung Nuiannas": "Elementarmanipulation",
    "Belemans Hochzeit": "Elementarmanipulation",
    "Trophäe erhalten": "Gegenstand verbessern/schaden",
    "Wundersame Blütenpracht": "Mystisches Eingreifen",
    "Siegel Borons": "Einfluss",
    "Weihe der ewigen Flamme": "Licht/Dunkelheit",
    # --- Nachtrag 4: restliche „narrative" Liturgien zugeordnet, Mirakel-Kategorie aufgelöst ---
    "Angroschs Opfergabe": "Gegenstand verbessern/schaden",
    "Ehrenhafter Zweikampf": "Einfluss",
    "Ein Freund in Zeiten der Not": "Segen",
    "Ewiges Wissen": "Segen",
    "Gebet des kristallklaren Blicks": "Fernsicht",
    "Graues Siegel": "Arkanes entdecken/verbergen",
    "Indoktrination": "Segen",
    "Kirschblütenregen": "Illusion",
    "Kleine Liturgie des heiligen Nemekath": "Vision",
    "Ordination": "Segen",
    "Phexens Elsterflug": "Arkanes entdecken/verbergen",
    "Prophezeiung": "Vision",
    "Sprechende Symbole": "Arkanes entdecken/verbergen",
    "Sterne funkeln immerfort": "Segen",
    "Sternenspur": "Arkanes entdecken/verbergen",
    "Visionssuche": "Vision",
    "Wandeln in Hesindes Hain": "Vision",
}


def base(n):
    return n.split(" (")[0].strip()


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    mae = d["maechte"]
    grim = json.load(open(GRIM, encoding="utf-8"))  # base-Zaubername -> Verbreitung-String
    liber = json.load(open(LIBER, encoding="utf-8"))  # Liturgiename -> [Gott, ...]

    # Validierung: jede LITURGIE_SW-Macht muss existieren
    unknown = {v for v in LITURGIE_SW.values() if v not in mae}
    if unknown:
        raise SystemExit(f"LITURGIE_SW verweist auf unbekannte Mächte: {sorted(unknown)}")

    # Trapping -> [SW-Macht]; und base-Name -> SW-Mächte (Union)
    sw_by_base = defaultdict(set)
    for nm, m in mae.items():
        for t in (m.get("dsa_trappings") or []):
            sw_by_base[base(t)].add(nm)
    have_bases = set(sw_by_base)

    def sw_cell(name):
        s = sw_by_base.get(base(name))
        return " / ".join(sorted(s)) if s else "— *(keine Zuordnung)*"

    # Verbreitung je base (nur für Zauber, die wir auch als Trapping haben)
    verbr = {}
    for b in have_bases:
        if b in grim:
            verbr[b] = grim[b]

    # Buckets: Token-Tradition -> set(base); plus allgemein
    buckets = defaultdict(set)
    allgemein = set()
    for b, v in verbr.items():
        toks = [x.strip() for x in re.split(r",\s*", v)]
        if toks == ["allgemein"] or v.strip() == "allgemein":
            allgemein.add(b)
            continue
        for tok in toks:
            buckets[tok].add(b)

    o = []
    W = o.append
    misses = []

    W("# Savage Aventurien — Traditionen & Zauber → SW-Mächte\n")
    W("> Automatisch generiert (`python scripts/gen_traditionen_zauber.py`). Pro Tradition/Kult: "
      "typische DSA-Zauber/Liturgien und die zugeordnete **SW-Macht** — damit DSA-Spieler sehen, "
      "welche Mächte für sie sinnvoll sind.\n")
    W("> **Magische Haupttraditionen** sind datengetrieben aus der *Verbreitung* des Grimorum "
      "Cantiones, **Geweihte** datengetrieben aus der *Herkunft* des Liber Liturgium (jeweils alle "
      "von uns abgebildeten Zauber/Liturgien). **Sub-Schulen** ohne eigenes Verbreitungs-Token sind "
      "kuratierte Signatur-Listen. **Allgemeine Zauber/Liturgien** stehen jeder Tradition bzw. jedem "
      "Zwölfgötter-Geweihten offen. Liturgien ohne mechanische Entsprechung sind *narrativ*.\n")
    W("---\n## Inhalt\n\n1. [Magische Haupttraditionen](#1-magische-haupttraditionen)\n"
      "2. [Magische Sub-Schulen](#2-magische-sub-schulen)\n"
      "3. [Allgemeine Zauber (alle Traditionen)](#3-allgemeine-zauber-alle-traditionen)\n"
      "4. [Geweihte (Götter-Kulte)](#4-geweihte-götter-kulte)\n\n---\n")

    # 1. Datengetriebene Haupttraditionen
    W("## 1. Magische Haupttraditionen\n")
    W("> Quelle: Grimorum-*Verbreitung*. Listet alle von uns unterstützten Zauber dieser Tradition.\n")
    for titel, tok in TOKEN_TRAD:
        bs = sorted(buckets.get(tok, set()), key=str.lower)
        W(f"### {titel} ({len(bs)})\n")
        W("| DSA-Zauber | SW-Macht |")
        W("|---|---|")
        for b in bs:
            W(f"| {b} | {sw_cell(b)} |")
        W("")

    # 2. Kuratierte Sub-Schulen
    W("---\n## 2. Magische Sub-Schulen\n")
    W("> Kuratierte Signatur-Zauber (keine eigene Grimorum-Verbreitung; meist Gildenmagier-Schulen "
      "oder Sondertraditionen).\n")
    for trad, zs in SUB_TRAD.items():
        W(f"### {trad}\n")
        W("| Typischer DSA-Zauber | SW-Macht |")
        W("|---|---|")
        for z in zs:
            cell = sw_cell(z)
            if "keine Zuordnung" in cell:
                misses.append((trad, z))
            W(f"| {z} | {cell} |")
        W("")

    # 3. Allgemeine Zauber
    W("---\n## 3. Allgemeine Zauber (alle Traditionen)\n")
    W("> Verbreitung „allgemein“ — jeder magischen Tradition zugänglich.\n")
    bs = sorted(allgemein, key=str.lower)
    W(f"**{len(bs)} Zauber**\n")
    W("| DSA-Zauber | SW-Macht |")
    W("|---|---|")
    for b in bs:
        W(f"| {b} | {sw_cell(b)} |")
    W("")

    # 4. Geweihte (datengetrieben aus Liber-Herkunft)
    def lit_sw(name, gott=None):
        # 1) Trapping-Index (Name == DSA-Zauber/Liturgie), 2) Wirkungs-Mapping, 3) narrativ
        s = sw_by_base.get(base(name))
        if s:
            if gott and f"Mirakel ({gott})" in s:
                return f"Mirakel ({gott})"  # gott-spezifische Mirakel-Macht bevorzugen
            return " / ".join(sorted(s))
        if name in LITURGIE_SW:
            return LITURGIE_SW[name]
        return "— *(narrativ)*"

    # Gott-Token -> [Liturgien]
    gott_lit = defaultdict(list)
    allg_lit = []  # universell / Zwölfgötterkult
    for lit, goetter in liber.items():
        ziele = [g for g in goetter if g not in ("universell", "Zwölfgötterkult")]
        if not ziele:  # nur universell/Zwölfgötterkult
            allg_lit.append(lit)
        for g in ziele:
            gott_lit[g].append(lit)

    narrativ_count = 0

    def lit_table(liturgien, gott=None):
        nonlocal narrativ_count
        W("| Liturgie | SW-Macht |")
        W("|---|---|")
        for lit in sorted(liturgien, key=str.lower):
            cell = lit_sw(lit, gott)
            if "narrativ" in cell:
                narrativ_count += 1
            W(f"| {lit} | {cell} |")
        W("")

    W("---\n## 4. Geweihte (Götter-Kulte)\n")
    W("> Datengetrieben aus dem Liber Liturgium (Feld *Herkunft*): vollständiges Liturgie-Roster je "
      "Gottheit. Jede Liturgie ist einer SW-Macht nach **Wirkung** zugeordnet (inkl. der Mächte "
      "*Einfluss* und *Vision* für Suggestion bzw. Weissagung).\n")

    # Allgemeine Liturgien (universell / Zwölfgötterkult)
    W("### Allgemeine Liturgien (Zwölfgötterkult / universell)\n")
    W("> Jedem Geweihten der Zwölfgötter zugänglich.\n")
    lit_table(allg_lit, "Zwölfgötter")

    for tok, label in GOTT_LABELS:
        lits = gott_lit.get(tok, [])
        if not lits:
            continue
        W(f"### {label} ({len(lits)})\n")
        lit_table(lits, tok)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(o))
    print(f"Geschrieben: {OUT}")

    # ===== Zweites Dokument: pro Tradition gruppiert nach SW-Macht =====
    o2 = []
    W2 = o2.append

    def gruppiere(eintraege, sw_func):
        g = defaultdict(list)
        narr = []
        for nm in sorted(eintraege, key=str.lower):
            cell = sw_func(nm)
            if "narrativ" in cell or "keine Zuordnung" in cell:
                narr.append(nm)
                continue
            for macht in cell.split(" / "):
                g[macht].append(nm)
        return g, narr

    def emit(titel, g, narr):
        W2(f"### {titel}\n")
        W2("| SW-Macht | DSA-Zauber/Liturgien |")
        W2("|---|---|")
        for macht in sorted(g):
            W2(f"| {macht} | {', '.join(g[macht])} |")
        if narr:
            W2(f"| — *(narrativ)* | {', '.join(narr)} |")
        W2("")

    W2("# Savage Aventurien — SW-Macht → DSA-Trappings je Tradition\n")
    W2("> Automatisch generiert (`python scripts/gen_traditionen_zauber.py`). Pro Tradition/Kult "
      "je **SW-Macht** die Liste der zugehörigen DSA-Zauber/Liturgien (nur Namen). Spiegelbild zu "
      "`Savage_Aventurien_Traditionen_Zauber_Mapping.md`.\n")
    W2("---\n## 1. Magische Haupttraditionen\n")
    for titel, tok in TOKEN_TRAD:
        g, narr = gruppiere(buckets.get(tok, set()), sw_cell)
        emit(titel, g, narr)
    W2("---\n## 2. Magische Sub-Schulen\n")
    for trad, zs in SUB_TRAD.items():
        g, narr = gruppiere(zs, sw_cell)
        emit(trad, g, narr)
    W2("---\n## 3. Allgemeine Zauber (alle Traditionen)\n")
    g, narr = gruppiere(allgemein, sw_cell)
    emit("Allgemein", g, narr)
    W2("---\n## 4. Geweihte (Götter-Kulte)\n")
    g, narr = gruppiere(allg_lit, lambda n: lit_sw(n, "Zwölfgötter"))
    emit("Allgemeine Liturgien (Zwölfgötterkult / universell)", g, narr)
    for tok, label in GOTT_LABELS:
        lits = gott_lit.get(tok, [])
        if not lits:
            continue
        g, narr = gruppiere(lits, lambda n, _t=tok: lit_sw(n, _t))
        emit(label, g, narr)

    open(OUT2, "w", encoding="utf-8").write("\n".join(o2))
    print(f"Geschrieben: {OUT2}")
    n_main = sum(len(buckets.get(t, set())) for _, t in TOKEN_TRAD)
    n_lit = sum(len(v) for v in gott_lit.values()) + len(allg_lit)
    print(f"Haupttraditionen-Einträge: {n_main} · allgemein (Zauber): {len(allgemein)} · "
          f"Sub-Schulen: {len(SUB_TRAD)} · Liturgie-Einträge: {n_lit} "
          f"(davon narrativ: {narrativ_count}) · Zauber ohne Zuordnung: {len(misses)}")
    for trad, z in misses:
        print(f"  OHNE ZUORDNUNG [{trad}] {z}")


if __name__ == "__main__":
    main()
