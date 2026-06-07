# Deep Review — Mächte & DSA-Trappings (Savage Aventurien)

Stand: 2026-06-07 · Quelle: `settings/Savage Aventurien.json` (66 Mächte)
Ziel: Sind die Trapping→Macht-Zuordnungen stimmig? Wo nötig einem Trapping eine
passende **SW-Modifikation** oder **Einschränkung** zuordnen.

---

## A. Datenmodell-Befund

- Jede Macht hat im `beschreibung`-Feld einen **SW-Regelabschnitt** (Grundeffekt + offizieller
  `Modifikatoren:`-Block), darunter je eine **Flavor-Zeile pro Trapping** (`Name: Beschreibung`).
- Trappings tragen **aktuell keine eigene Mechanik** — sie sind reine Flavor-Namen. Ein Spieler
  bildet einen DSA-Zauber ab, indem er die Grundmacht wählt und ggf. offizielle Modifikatoren kauft.
- **Konsequenz:** Um einem Trapping eine Mechanik zuzuordnen, ergänzen wir seine Flavor-Zeile um
  einen kurzen Hinweis **„(SW-Modifikator: … )"** bzw. **„(Einschränkung: … )"**. Das nutzt nur
  SW-Begriffe (regelkonform) und taucht **nicht** in der Übersichts-MD auf (der Generator schneidet
  Trapping-Zeilen ab → kein Zusatzlärm im Überblick).

---

## B. Doppelzuordnungen (16 Trappings unter mehreren Mächten)

| Trapping | aktuell unter | Bewertung | Empfehlung |
|---|---|---|---|
| **Exorzismus** | Aufheben, Verbannen | Austreiben von Geistern = Verbannen; Aufheben ist Magie-Negation | **Aus Aufheben entfernen** |
| **Dämonenbann** | Aufheben, Verbannen | dito | **Aus Aufheben entfernen** |
| **Machtvoller Exorzismus** | Aufheben, Verbannen | dito | **Aus Aufheben entfernen** |
| **Reinigung des Bösen** | Aufheben, Segen | Gebiet entweihen/reinigen = Segen/Heiligtum; nicht Effekt-Negation | **Aus Aufheben entfernen** (bleibt bei Segen) |
| **Speer des Athleten** | Geschoss, Strahl | Einzelnes geworfenes Geschoss, kein Kegel | **Aus Strahl entfernen** (bleibt Geschoss) |
| **Erinnern** | Gedankenleere, Gedankenlesen | Erinnerung *abrufen* = Lesen; Gedankenleere = Löschen | **Aus Gedankenleere entfernen** |
| **Bannzone** | Heiligtum, Mystisches Eingreifen | kleine geweihte Zone = Heiligtum (A,2 MP); ME ist L/20 MP | **Aus Mystisches Eingreifen entfernen** |
| **Welle der Reinigung** | Flächenschlag, Schadensfeld | sofortiger Flächen-Schlag gegen Schwärme, kein anhaltendes Feld | **Aus Schadensfeld entfernen** |
| **Bannstrahl** | Strahl, Verbannen | echte Doppelnutzung: Schaden *und* Bannung | **beide behalten** + Einschränkung „nur Dämonen/Geister/Paktierer" |
| **Kleiner Bannstrahl** | Strahl, Verbannen | dito | **beide behalten** + gleiche Einschränkung |
| **Pestodem** | Fluch, Strahl | Krankheits-/Giftwolke: als Fluch (Krankheit) *und* als Strahl (Kegel-Gas) plausibel | **behalten**, beide legitim |
| **Giftbann** | Aufheben, Heilung | magisches Gift = Aufheben, körperliches = Heilung | **behalten** (echte Doppelnutzung) |
| **Tierleid lindern** | Heilung, Linderung | Heilen vs. Schmerz/Furcht-Abbau | **behalten** (echte Doppelnutzung) |
| **Ausnüchtern** | Aufheben, Linderung | Rausch ist kein magischer Effekt → Linderung; Aufheben nur falls magisch | **Aus Aufheben entfernen** (bleibt Linderung) |
| **Brennender Hass** | Kriegersegen, Marionette | erzwungene Aggression = Zwang (Marionette); Kampfrausch = Buff (Kriegersegen) | **behalten**, aber prüfen (Tendenz Marionette) |
| **Zauberpferd herbeirufen** | Tier Beschwören, Verbündeten beschwören | Pferd = Tier; steuerbarer Verbündeter = Verbündeter | **behalten** (Geschmacksfrage) |

**Kern-Cleanup (eindeutig):** 6 Entfernungen aus *Aufheben* (Exorzismus, Dämonenbann, Machtvoller
Exorzismus, Reinigung des Bösen, Ausnüchtern) + *Strahl* (Speer des Athleten) + *Gedankenleere*
(Erinnern) + *Mystisches Eingreifen* (Bannzone) + *Schadensfeld* (Welle der Reinigung).
Danach behält *Aufheben* nur echte Negations-Trappings (Merkmalsbann, Befreiung des Geistes,
Dämonenpakt beenden/brechen, Giftbann, Invercano umgekehrt, Klarum Purum).

---

## C. Modifikator-/Einschränkungs-Konventionen (elementare Schadens-Trappings)

Die vom Nutzer gelisteten allgemeinen Modifikatoren lassen sich sauber auf die elementaren
Schadens-Trappings von **Geschoss / Strahl / Flächenschlag / Schadensfeld** abbilden. Vorschlag
für eine **einheitliche Konvention** (als Hinweis-Zeile am Trapping):

| Element | Trappings (Beispiele) | empfohlener SW-Modifikator | Begründung |
|---|---|---|---|
| **Feuer** | Feuerpfeil, Ignifaxius, Ignisphaero, Pech und Schwefel, Brandform | **Anhaltender Schaden (+2)** | Feuer brennt weiter |
| **Kälte/Eis** | Corpofrigo, Eispfeil, Frigifaxius, Frigisphaero, Froststurm, Kälteexplosion, Caldofrigo | **Bremsen (+1)** | Kälte verlangsamt (Corpofrigo verursacht in DSA Erstarrung) |
| **Blitz** | Fulminictus, Kulminatio, Blitzball, Blitzschlag, Blitz dich find | **Panzerbrechend (+1)** | Blitz schlägt durch Rüstung |
| **Säure/Gift** | Hexengalle | **Panzerbrechend (+1)** | Säure ätzt Rüstung |
| **Wucht/Erde groß** | Erdbeben, Lawinenfall und Trümmerfeld | **Schwere Waffe** (über epischen Mod.) | Masse/Fels |
| **Sturm/Druck** | Orcanofaxius, Sturmwand, Angriffswelle | **Bremsen (+1)** o. Stoßen | Wind drückt zurück |

> Diese Hinweise sind **Empfehlungen** an den Spieler („welcher Mod. passt zum Element"), kein
> Zwang. Sie kosten regulär Machtpunkte über die Grundmacht — wir codieren sie als Flavor-Hinweis,
> nicht als automatische Mechanik.

**Einschränkungen (Restriction) statt Bonus** bei zielgebundenen Trappings:
- **Bannstrahl / Kleiner Bannstrahl** (Strahl/Verbannen): „nur gegen Dämonen, Geister, Untote, Paktierer".
- **Bann wider Untote** (Verbannen): „nur gegen Untote".
- **Welle der Reinigung** (Flächenschlag): „nur gegen Schwarm-/Kleintiere".
- **Pestodem** (Fluch): wirkt als Krankheit (langsam), nicht als Sofortschaden.

---

## D. Sekundärbefund (separater Cleanup, nicht Teil dieses Tasks)

Viele Trapping-Texte enthalten noch **DSA-Regelbegriffe**, die laut Projektregel raus sollen:
`Stufen Betäubung`, `Zustand Schmerz/Furcht/Verwirrung`, `Status Fixiert/Eingeengt/Bewusstlos`.
Beispiele: Friedvoller Rausch, Invinculo, Numinorus Fesseln, Schmerzen lindern, Klarer Geist,
Höllenpein, Welle des Schmerzes. → Vorschlag: in einem **eigenen Durchgang** auf SW-Begriffe
umschreiben (Angeschlagen, Erschüttert, Gebunden/Festgehalten, Abgelenkt, Wunden).

---

## E. Umsetzungs-Status (✅ alle vier umgesetzt 2026-06-07)

1. **✅ Cleanup B** — 9 Fehl-Trappings entfernt: Aufheben (Exorzismus, Dämonenbann, Machtvoller
   Exorzismus, Reinigung des Bösen, Ausnüchtern), Strahl (Speer des Athleten), Gedankenleere
   (Erinnern), Mystisches Eingreifen (Bannzone), Schadensfeld (Welle der Reinigung). Es bleiben
   nur noch 7 *bewusste* Doppelnutzungen (Bannstrahl, Kleiner Bannstrahl, Giftbann, Tierleid
   lindern, Pestodem, Brennender Hass, Zauberpferd herbeirufen).
2. **✅ Modifikator-Konvention C** — Elementar-Block ("Elementare Ausprägung (empfohlener
   Modifikator)") in Geschoss/Strahl/Flächenschlag eingefügt (erscheint im SW-Regelabschnitt der
   Übersichts-MD). Zusätzlich gezielte `(SW-Modifikator: …)`-Hinweise an Einzel-Trappings
   (Corpofrigo, Fulminictus, Hexengalle, Kulminatio, Pech und Schwefel, Blitzball, Blitzschlag,
   Erdbeben, Froststurm, Kälteexplosion, Lawinenfall).
3. **✅ Einschränkungs-Hinweise** — `(Einschränkung: …)` an Bannstrahl (Strahl+Verbannen),
   Bann wider Untote (Verbannen), Welle der Reinigung (Flächenschlag).
4. **✅ Sekundär-Cleanup D** — 34 Trapping-Zeilen von DSA-Regelbegriffen auf SW-Begriffe
   umgeschrieben (Stufen/Zustands-Stufen/Status/Paralyse/LeP → Angeschlagen, Betäubt, Festgehalten,
   Gebunden, Geblendet, Abgelenkt, Wunden, Furchtprobe). Re-Scan: 0 verbleibende DSA-Begriffe.

Setting-Tests grün (69+102). Übersicht neu generiert (66 Mächte unverändert in Zahl).

---

## F. Traditionen-/Liturgien-Mapping & Liturgie-Trappings (2026-06-07)

Aufbauend auf dem Trapping-Mapping wurden zwei Übersichts-Docs + eine Daten-Erweiterung erstellt:

- **`docs/Savage_Aventurien_Traditionen_Zauber_Mapping.md`** — pro Tradition/Kult: DSA-Zauber →
  SW-Macht. Magische Haupttraditionen datengetrieben aus Grimorum-*Verbreitung*
  (`scripts/extract_grimorum_verbreitung.py` → `grimorum_verbreitung.json`), Geweihte datengetrieben
  aus Liber-*Herkunft* (`scripts/extract_liber_herkunft.py` → `liber_herkunft.json` +
  `liber_beschreibung.json`).
- **`docs/Savage_Aventurien_Tradition_SWMacht_Trappings.md`** — Spiegeltabelle: pro Tradition je
  **SW-Macht** die Liste der DSA-Trappings (nur Namen).
- **Liturgie-Trappings in JSON ergänzt:** Die 199 mechanisch abbildbaren Liturgien (Mapping
  `LITURGIE_SW` in `gen_traditionen_zauber.py`) wurden via `scripts/add_liturgien_trappings.py` als
  Trappings + Kurzbeschreibung (aus Liber, DSA-Begriffe gescrubbt) in die jeweilige SW-Macht
  eingefügt. Trappings gesamt 690 → 889. „Narrativ" zunächst von 179 auf 60 gesenkt.
- **Mirakel-Mächte je Gott (2026-06-07):** Für die rein narrativen Liturgien wurde via
  `scripts/add_mirakel_maechte.py` pro Gottheit eine Macht **`Mirakel (<Gott>)`** angelegt (z.B.
  `Mirakel (Travia)`, `Mirakel (Zwölfgötter)`) und die jeweiligen Liturgien als Trappings +
  Kurzbeschreibung einsortiert (shared Liturgien in jede zugehörige Mirakel-Macht). Der Doc-Generator
  zeigt je Gott die passende `Mirakel (Gott)` (gott-bewusste `lit_sw`).
- **Narrativ-Reduktion 2 (2026-06-07):** Nach Volltext-Prüfung im Liber 22 vermeintlich narrative
  Liturgien doch konkreten Mächten zugeordnet (Jagdglück→Aufspüren, Golgaris Zwielicht→Dunkelsicht,
  Marbos Geleit→Ebenenwechsel, Praios' Mahnung→Blenden, …) → 16 Mirakel-Mächte / 17 narrative.
  `add_liturgien_trappings.py` **re-synct** bestehende Liturgie-Beschreibungen aus dem Cache;
  Scrubber + Override (12 handgeschriebene Kurzbeschreibungen) → DSA-Begriff-Scan inkl.
  SP/RS/LkP*/`*`-Reste: **0**.
- **Mirakel AUFGELÖST (2026-06-07, final):** Alle restlichen 17 narrativen Liturgien echten Mächten
  zugeordnet; `Mirakel (<Gott>)`-Mächte entfernt. Zwei **neue Mächte**: **`Einfluss`** (Suggestion;
  bekam Ehrenhafter Zweikampf + aus Marionette verschoben Wille zur Wahrheit / Revolution der
  Gedanken / Siegel Borons) und **`Vision`** (Weissagung: Prophezeiung, Visionssuche, Kleine Liturgie
  des heiligen Nemekath, Wandeln in Hesindes Hain). Rest: Angroschs Opfergabe→Gegenstand verbessern/
  schaden, Gebet des kristallklaren Blicks→Fernsicht, Graues Siegel/Sternenspur/Sprechende Symbole/
  Phexens Elsterflug→Arkanes entdecken/verbergen, Kirschblütenregen→Illusion, mehrere→Segen.
  **narrativ = 0**, Mächte **68**, DSA-Scan **0**, Suite 951/952 (1 vorbestehender KivyMD-UI-Fehler).
  `add_mirakel_maechte.py` ist dormant (nicht mehr Teil der Pipeline).
