#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrahiert je Liturgie die 'Herkunft' (Gottheit/Kult) aus dem Liber Liturgium.

Schreibt den Cache `scripts/liber_herkunft.json` ({Liturgiename: [Gott, ...]}).
Liturgien haben kein 'Verbreitung'-Feld wie Zauber, aber ein Feld 'Herkunft:' das die
Gottheit(en) nennt. Der Liturgiename steht als Überschrift direkt vor der 'Grad:'-Zeile.

Aufruf:  python scripts/extract_liber_herkunft.py
"""
import os
import re
import subprocess
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "Texte", "Liber_Liturgium.pdf")
OUT = os.path.join(ROOT, "scripts", "liber_herkunft.json")
OUT_BESCH = os.path.join(ROOT, "scripts", "liber_beschreibung.json")

TERM = ("Varianten:", "Anmerkungen:", "Liturgiestil:", "Grad:", "Herkunft:",
        "Reichweite:", "Symbole", "Ritualdauer:", "Wirkungsdauer:", "Art:", "Ziel:")


# Handgeschriebene Kurzbeschreibungen für Liturgien, deren Auswirkung sich nicht sauber
# automatisch von DSA-Wertformeln (SP, RS, LkP*, …) befreien lässt.
BESCHREIBUNG_OVERRIDE = {
    "Ruf zur Ruhe": "Der Geweihte beruhigt eine Zielperson; widersteht sie nicht, verliert sie ihre Aggression.",
    "Bannfluch des Heiligen Khalid": "Der Geweihte bettet mehrere Untote oder verirrte Seelen zur ewigen Ruhe.",
    "Entzug von Nandus’ Gaben": "Der Geweihte bestraft eine Person mit Dummheit und getrübten Sinnen.",
    "Wundersames Teilen des Martyriums": "Die Geweihte nimmt einmalig die Hälfte des Schadens auf sich, den eine ihr nahestehende Person erleidet.",
    "Das schwarze Fell durch das rote Blut": "Die Haut des Geweihten wird fester und widerstandsfähiger und gewährt zusätzliche Panzerung.",
    "Daradors Bann der Schatten": "In der Zone werden alle Schatten aufgehoben sowie magische Licht-/Schattenmanipulationen und optische Illusionen unterdrückt.",
    "Rondras wundersame Rüstung": "Die Geweihte ruft eine wundersame Rüstung herbei, die sie schwer schützt.",
    "Schrifttum ferner Lande": "Die Geweihte kann vorübergehend eine fremde oder alte Schrift lesen.",
    "Tsas heiliges Lebensgeschenk": "Der Empfänger erhält einen Teil seiner Lebenskraft zurück und kann dem sicheren Tod entrissen werden.",
    "Flagge des Regenbogens": "Wer im Wirkungsbereich weiter angreifen oder kämpfen will, muss eine Willenskraftprobe bestehen.",
    "Efferdsegen": "Binnen weniger Tage wird es über den Feldern sanft, aber ausgiebig regnen.",
    "Ewiger Wächter": "Der Schamane verwandelt sich dauerhaft in einen Jaguar, der den zu beschützenden Ort kaum verlässt.",
}


def scrub(s):
    """Entfernt DSA-Regelbegriffe aus einer Kurzbeschreibung (SW-konform halten)."""
    # Regel-Klauseln nach Doppelpunkt mit Stat-Boni abschneiden (": KL +1, +3 auf …")
    s = re.sub(r":\s*[A-ZÄÖÜ]{2}\s*[+\-–].*$", ".", s)
    s = re.sub(r"\(siehe[^)]*\)", "", s)
    s = re.sub(r"\bLkP\*?(?:/2|x ?3|x ?2)?\b", "", s)
    s = re.sub(r"\bLkW\*?\b", "", s)
    s = re.sub(r"\bAsP\b", "Machtpunkte", s)
    s = re.sub(r"\bKaP\*?\b", "Machtpunkte", s)
    s = re.sub(r"\bQS\b", "", s)
    s = re.sub(r"[+\-–]\d+\s*auf\s+\w+\s*Leittalente", "", s)
    s = s.replace("Selbstbeherrschungs-Probe", "Willenskraftprobe")
    s = s.replace("Mutproben", "Furchtproben").replace("Mutprobe", "Furchtprobe")
    s = re.sub(r"\bKO-Probe(n)?\b", "Robustheitsprobe", s)
    s = re.sub(r"\b(?:der |des )?Stufe[n]? \w+", "", s)  # DSA-Zustandsstufen
    s = re.sub(r"\*\s*\+?\s*\d+", "", s)                 # *+5 / * 3 Reste von LkP*
    s = re.sub(r"(?<![\w*])\*(?![\w])", "", s)            # einzelne Sternchen
    s = re.sub(r"\b(SP|RS|AU|TaW|ZfW|Sikaryan)\b", "", s)  # weitere DSA-Werte
    s = re.sub(r"\b(MU|KL|IN|CH|FF|GE|KO|KK)\b", "", s)  # DSA-Attribut-Kürzel
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([.,;:])", r"\1", s)
    s = re.sub(r"\s+\.", ".", s)
    s = re.sub(r",\s*\.", ".", s)
    return s.strip()


def cap_words(s, limit=170):
    """Kürzt am Wortende auf <=limit Zeichen, hängt … an wenn gekürzt."""
    s = s.strip()
    if len(s) <= limit:
        return s
    cut = s[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + " …"

GODS = {
    "Praios", "Rondra", "Efferd", "Travia", "Boron", "Hesinde", "Firun", "Tsa", "Phex",
    "Peraine", "Ingerimm", "Rahja", "Aves", "Ifirn", "Kor", "Nandus", "Swafnir",
    "Angrosch", "Gravesh", "Himmelswölfe", "H’Szint", "Kamaluq", "Tairach", "Zsahh",
    "H’Ranga", "Namenlos", "Riva", "universell", "Zwölfgötterkult",
}


def main():
    if not os.path.exists(PDF):
        sys.exit(f"PDF nicht gefunden: {PDF}")
    txt = subprocess.run(["pdftotext", PDF, "-"], capture_output=True, text=True).stdout
    lines = txt.split("\n")
    N = len(lines)

    def clean_herk(s):
        s = s.split("Herkunft:")[-1]
        out = []
        for t in re.split(r"[,;]", s):
            t = t.split("(")[0]
            t = re.sub(r"\s+", " ", t).strip()
            if t in GODS:
                out.append(t)
        return out

    def reconstruct_name(grad_idx):
        parts = []
        k = grad_idx - 1
        while k >= 0 and len(parts) < 3:
            ln = lines[k].strip()
            if not ln:
                if parts:
                    break
                k -= 1
                continue
            if ln.isdigit() or ln.endswith(".") or ":" in ln or len(ln) > 38:
                break
            parts.append(ln)
            k -= 1
        return re.sub(r"\s+", " ", " ".join(reversed(parts))).strip()

    def kurzbeschreibung(herk_idx):
        a = next((k for k in range(herk_idx, min(N, herk_idx + 40))
                  if lines[k].startswith("Auswirkung:")), None)
        if a is None:
            return ""
        buf = [lines[a][len("Auswirkung:"):].strip()]
        for k in range(a + 1, min(N, a + 25)):
            s = lines[k].strip()
            if not s or s.startswith(TERM) or s.isdigit():
                break
            buf.append(s)
        txt = re.sub(r"\s+", " ", " ".join(buf)).strip()
        m = re.match(r"(.+?[.!])(\s|$)", txt)
        first = m.group(1) if m else txt
        return cap_words(scrub(first))

    herk = {}
    besch = {}
    for i in range(N):
        if lines[i].startswith("Herkunft:"):
            g = next((j for j in range(i - 1, max(0, i - 6), -1) if lines[j].startswith("Grad")), None)
            if g is None:
                continue
            nm = reconstruct_name(g)
            gods = clean_herk(lines[i])
            if nm and gods:
                herk.setdefault(nm, sorted(set(gods)))
                besch.setdefault(nm, BESCHREIBUNG_OVERRIDE.get(nm) or kurzbeschreibung(i))

    json.dump(herk, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    json.dump(besch, open(OUT_BESCH, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print(f"Geschrieben: {OUT}  ({len(herk)} Liturgien mit Herkunft)")
    print(f"Geschrieben: {OUT_BESCH}  ({sum(1 for v in besch.values() if v)} Kurzbeschreibungen)")


if __name__ == "__main__":
    main()
