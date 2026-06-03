#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fügt die DSA-spezifischen Talente und Handicaps aus den Fan-Konversionen
"Wildes Aventurien" (V2.3 + Ver. 3.0) in das Setting "Savage Aventurien" ein.

Nur Elemente, die NICHT bereits durch das Fantasy Kompendium abgedeckt sind,
werden ergänzt (siehe logs/wildes_aventurien_abgleich.md).

Idempotent: bereits vorhandene Namen werden übersprungen.
"""
import json
import sys
from pathlib import Path

SETTING = Path("settings/Savage Aventurien.json")


def talent(name, kategorie, rang, vor, beschreibung, neue_maechte=0, machtpunkte=0):
    return name, {
        "name": name,
        "kategorie": kategorie,
        "rang": rang,
        "voraussetzungen": vor,
        "beschreibung": beschreibung,
        "neue_maechte": neue_maechte,
        "machtpunkte": machtpunkte,
        "ausgewaehlt": False,
        "aktiv": True,
    }


def handicap(key, name, stufe, punkte, beschreibung):
    return key, {
        "name": name,
        "stufe": stufe,
        "punkte": punkte,
        "beschreibung": beschreibung,
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    }


# --- Neue Talente (Wildes Aventurien) ---------------------------------------
NEUE_TALENTE = [
    # Machttalente
    talent("Kraftlinienmagie", "Magier", "H",
           ["AH (Magie)", "WIL W8", "Okkultismus W8"],
           "Auf einer Kraftlinie sind Zaubernproben um +2 erleichtert, auf einer "
           "Kreuzung zweier Linien um +4 (je weitere Linie +1). Dafür tritt der "
           "Rückschlag auf einer Kraftlinie schon bei 1–2 auf dem Zaubern-Würfel "
           "ein (egal, was der Wild Die zeigt). Erst dieses Talent erlaubt es, "
           "Kraftlinien mit Arkanes entdecken aufzuspüren."),
    talent("Kugelzauber", "Magier", "A",
           ["AH (Magie)", "Zaubern W6"],
           "Der Magier kann eine Kristallkugel verzaubern: als Brennglas nutzen, "
           "Bilder der Umgebung aufnehmen und wiedergeben oder im Umkreis von "
           "VER × 10 m vor Untoten warnen (rotes Aufleuchten – je intensiver, "
           "desto näher die Untoten)."),
    talent("Mirakel", "Kleriker", "A",
           ["AH (Wunder)", "Glaube W6"],
           "Durch ein kurzes Stoßgebet kann der Geweihte nach einem Wurf einen "
           "Bennie ausgeben und erhält den bei seiner Gottheit unter „Mirakel“ "
           "angegebenen Bonus, um die Probe nachträglich zu seinen Gunsten zu "
           "drehen."),
    talent("Magischer Alltag", "Macht", "A",
           ["AH (Magie)", "Zaubern W8"],
           "Der Zauberer erledigt alltägliche Tätigkeiten (Kleidung reinigen, "
           "schneidern, Haare schneiden u.ä.) auf magische Weise. Deckt Zauber "
           "wie Sapefacta oder Accuratum ab; der SL entscheidet im Einzelfall, "
           "ob ein oder zwei Machtpunkte fällig werden."),
    talent("Knochenkeule", "Schamane", "F",
           ["AH (Schamane)", "Glaube W8", "WIL W8"],
           "Der Schamane versieht seine Knochenkeule mit besonderen Fähigkeiten; "
           "sie zählt fortan als magische Waffe und erleichtert das Einstimmen auf "
           "die Geister. Die Auswirkungen einer leichten Sünde treten nur noch bei "
           "einer 1 auf, die einer schweren nur bei kritischem Fehlschlag. Solange "
           "er die Keule nutzt, kann er seine Kräfte nicht verlieren."),
    talent("Elfenlieder", "Macht", "A",
           ["Zaubern W6", "Elf oder Halbelf"],
           "Mit seinem Seeleninstrument spielt der Elf magische Lieder, die +1 auf "
           "eine bestimmte Eigenschaft verleihen, solange das Lied gehört wird. "
           "Elfenlieder lösen stets positive Gefühle und Verbundenheit aus. Das "
           "Wirken erfordert eine erfolgreiche Verstandsprobe. (DSA: Arkaner "
           "Hintergrund Fey.)"),
    talent("Hexenflüche", "Hexe", "A",
           ["AH (Hexe)", "Zaubern W8"],
           "Die Hexe spricht lang anhaltende Flüche aus. Ein Hexenfluch kostet "
           "keine Machtpunkte, der Zauberwurf ist aber um −2 erschwert. Für einen "
           "Bennie kann sie die Wirkungsdauer von Eigenschaft schwächen oder "
           "Fesseln beliebig lange aufrechterhalten; dafür muss sie zu Beginn "
           "jeder Sitzung je aufrechterhaltenem Fluch einen Bennie ausgeben."),
    talent("Dolch des Druiden", "Druide", "A",
           ["AH (Druide)", "Zaubern W8"],
           "Der Vulkanglasdolch wird kalt bei dämonischer Präsenz, weist den Weg "
           "zu seinem Weiheort und zu günstigen Orten der Wildnis (+1 auf "
           "Überleben) und zeigt Kraftlinien an. Einmal pro Tag kann der Druide "
           "eine Erschöpfungsstufe heilen, wenn er den Dolch in die Erde steckt "
           "und ein kurzes Ritual ausführt."),
    # Stab-Talentbaum (Ver. 3.0)
    talent("Bindung des Stabes", "Magier", "A",
           ["AH (Magier)", "Okkultismus W4"],
           "Der Magier bindet sich rituell an seinen Magierstab. Der Stab wird so "
           "stabil wie eine gleich große Eisenstange. Mit einer Aktion "
           "Konzentration und einer Zaubernprobe kann er den Stab in ein 20 m "
           "langes Seil oder eine Fackel verwandeln (kostet 1 MP); die "
           "Rückverwandlung ist kostenlos."),
    talent("Fokus des Stabes", "Magier", "F",
           ["Bindung des Stabes", "Okkultismus W8"],
           "Mit einer Aktion und einer Zaubernprobe halbiert oder verdoppelt der "
           "Magier die Länge seines Stabes. Der Stab zählt in jeder Form als "
           "Erweiterung der Reichweite Berührung. Zudem kann er ihn aus bis zu "
           "100 m zu sich rufen – außer er wird mit mindestens der Kraft einer "
           "erwachsenen Hand festgehalten."),
    talent("Flammenschwert", "Magier", "V",
           ["Fokus des Stabes", "Okkultismus W10"],
           "Der Magier verwandelt seinen Stab in ein Flammenschwert (VE+W8, "
           "Angriff über den Kämpfen-Wert des Magiers). Verwandlung über Zaubern: "
           "1 Aktion, 2 Machtpunkte, hält 5 Runden, danach 1 MP pro weiterer "
           "Runde. Das Schwert kann geführt oder schwebend genutzt werden (eigene "
           "Bewegungsaktion mit Standardgeschwindigkeit des Magiers)."),
    talent("Zauberspeicher", "Magier", "V",
           ["AH (Magier)", "Zaubern W8", "VER W10"],
           "Der Magier speichert bis zu fünf Machtpunkte in seinem Zauberstab. "
           "Sie sind an eine bei der Talentwahl bestimmte Macht gebunden und nur "
           "verfügbar, solange er den Stab berührt; er kann sie mit seinen eigenen "
           "kombinieren. Sie regenerieren gemeinsam mit den Machtpunkten des "
           "Magiers."),
    talent("Kraftfokus", "Magier", "V",
           ["AH (Magier)", "Zaubern W8"],
           "Solange der Magier seinen Zauberstab in der Hand hält, würfelt er einen "
           "W8 statt einen W6 als Wild Die auf seine Zaubernproben."),
    # Hintergrundtalente
    talent("Eisenaffine Aura", "Hintergrund", "A",
           ["AH"],
           "Halbiert sämtliche Einschränkungen durch das Tragen von Eisen am "
           "Körper (Bann des Eisens). Einschränkungen werden erst zusammengezählt, "
           "dann halbiert (bei ungeraden Zahlen aufgerundet). Nicht für "
           "Alchemisten oder Geweihte wählbar."),
    talent("Schelm", "Hintergrund", "A",
           [],
           "Als Säugling von Kobolden entführt und aufgezogen, beherrscht der "
           "Schelm allerlei magische Späße: Er kann per Zauberei Menschen nackt "
           "dastehen lassen, Kobolde rufen, Illusionen hervorrufen u.ä. – ganz "
           "ohne Arkanen Hintergrund oder Machtpunkte. Die Fähigkeit dient nur der "
           "Erheiterung, niemals der Schädigung, lässt sich aber für Tricks und "
           "geistige Duelle einsetzen."),
    # Expertentalente
    talent("Prophezeien", "Experte", "A",
           ["VER W6", "WIL W8"],
           "Sterndeuter, Zahori und thorwalsche Godi erhaschen einen Blick in die "
           "Zukunft. Funktioniert exakt wie die Macht Weissagung. Prophezeien ist "
           "auch ohne Arkanen Hintergrund erlernbar und benötigt keine "
           "Machtpunkte."),
]

# --- Neue Handicaps (Wildes Aventurien) -------------------------------------
NEUE_HANDICAPS = [
    handicap("Artefaktgebunden_leicht", "Artefaktgebunden", "leicht", 1,
             "Der Zauberer ist besonders stark an sein Traditionsartefakt "
             "(Magierstab, Druidendolch) gebunden. Hält er es beim Wirken von "
             "Mächten nicht in der Hand, erhält er −4 auf Zaubernproben. Wird das "
             "Artefakt zerstört, kann der Spieler seinen nächsten Aufstieg opfern, "
             "um dieses Handicap zu streichen. Nur mit AH (Magie) wählbar."),
    handicap("Novize_leicht", "Novize/Eleve", "leicht", 1,
             "Der Charakter ist Schüler einer Magierakademie oder Novize einer "
             "Kirche und hat seine Lehre vorzeitig beendet. Seine Machtfertigkeit "
             "kann während der Charaktererschaffung nicht höher als W6 gesteigert "
             "werden. Nur mit arkanem Hintergrund wählbar."),
    handicap("Novize_schwer", "Novize/Eleve", "schwer", 2,
             "Wie die leichte Form: Die Machtfertigkeit kann während der "
             "Charaktererschaffung nicht höher als W6 gesteigert werden. "
             "Zusätzlich startet der Charakter mit einer Macht weniger als normal."),
    handicap("Stigma_leicht", "Stigma", "leicht", 1,
             "Der Charakter ist durch Unfall, Fluch, Pakt o.ä. körperlich "
             "gezeichnet. Ist das Mal sichtbar, sind Überredenproben um −2 "
             "erschwert (je nach Bedeutung des Mals SL-Entscheid). Leichte "
             "Stigmata lassen sich üblicherweise einfach verbergen."),
    handicap("Stigma_schwer", "Stigma", "schwer", 2,
             "Wie die leichte Form, jedoch sind Überredenproben um −4 erschwert, "
             "wenn das Mal sichtbar ist, und es lässt sich schwerer verbergen."),
    handicap("Laestige_Mindergeister_leicht", "Lästige Mindergeister", "leicht", 1,
             "Bei jeder 1 auf dem Zaubern-Würfel (nicht dem Wild Die) erscheint "
             "eine Handvoll Mindergeister und ärgert den Zauberer. Welche "
             "Elementarwesen auftauchen, hängt von den Elementen in der Nähe ab; "
             "sie verhalten sich auffällig und können in ungünstigen Situationen "
             "auch Schaden anrichten. Nicht für Alchemisten oder Geweihte."),
]


def main():
    if not SETTING.exists():
        print(f"FEHLER: {SETTING} nicht gefunden (cwd={Path.cwd()})", file=sys.stderr)
        return 1
    data = json.loads(SETTING.read_text(encoding="utf-8"))
    talente = data["talente"]
    handicaps = data["handicaps"]

    added_t, skipped_t = [], []
    for name, eintrag in NEUE_TALENTE:
        if name in talente or any(v.get("name") == name for v in talente.values()):
            skipped_t.append(name)
        else:
            talente[name] = eintrag
            added_t.append(name)

    added_h, skipped_h = [], []
    for key, eintrag in NEUE_HANDICAPS:
        if key in handicaps:
            skipped_h.append(key)
        else:
            handicaps[key] = eintrag
            added_h.append(key)

    SETTING.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Talente:  +{len(added_t)} neu, {len(skipped_t)} übersprungen")
    for n in added_t:
        print(f"   + {n}")
    if skipped_t:
        print(f"   (übersprungen: {', '.join(skipped_t)})")
    print(f"Handicaps: +{len(added_h)} neu, {len(skipped_h)} übersprungen")
    for n in added_h:
        print(f"   + {n}")
    if skipped_h:
        print(f"   (übersprungen: {', '.join(skipped_h)})")
    print(f"\nGesamt jetzt: {len(talente)} Talente, {len(handicaps)} Handicaps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
