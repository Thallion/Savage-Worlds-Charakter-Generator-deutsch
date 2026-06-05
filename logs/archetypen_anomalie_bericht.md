# Archetypen Anomalie-Bericht

**Stand:** 2026-06-04 · **Zweck:** Offizielle Archetypen headless wie ein User nachbauen
(`archetyp-erstellen`-Skill, `driver.py` → echte Controller-Pfade), um **Code-/Daten-Bugs** zu
finden. Builds müssen nicht perfekt sein — Abweichungen werden klassifiziert, nicht erzwungen.

**Bestand:** **193 gespeicherte Archetypen, 0 korrupt** (`chars/Archetypen/Archetyp_*.json`).

| Setting | Chars | ✓ ohne Abw. | Status |
|---|---|---|---|
| Horror Kompendium | 36 | 26 | +3 Setting-Bug-Fix (Volk-auto-HCs), +4 Mächte-Nachschiebungen 2026-06-05 |
| SciFi Kompendium | 36 | 15 | Phase G komplett (12+14+6+4); Setting 207 Talente/101 HC/286+ Items/20 Völker |
| Fantasy Kompendium | 32 | 27 | viele GELDMANGEL-FORCE-Käufe (FK-Preise > Startkapital) |
| Savage Pathfinder | 30 | 26 | inkl. Sets 2+3; 1 Bug + 6 Nachschiebungen 2026-06-04 |
| Deadlands | 24 | 17 | Rang Fortgeschritten; D-Advance-Limitierungen (s. u.); +6 rebuilds 2026-06-04 |
| SWAE | 13 | 11 | +9 Worlds-of-Ulisses (2026-06-04); 2 Abw. = Shroud Wahrn (Provoz>V-Doppelkosten), Sozius Aufmerksamkeit-Talent (Pilot W10 frisst HP) |
| Superkräfte Kompendium | 11 | 11 | SKP-System, Stufe III=45 SKP; alle 11 summieren exakt |
| HeXXen 1773 | 6 | 4 | +4 Worlds-of-Ulisses; 2 Abw. = Klaas/Klara Bogen-Budget-Engpässe |
| Savage Aventurien | 4 | 4 | NEU 2026-06-04: Leomara, Hesindian, Romoxosch, Angrond (Worlds of Ulisses, DSA-Set) |

---

## 1 · SOLL/IST je Archetyp — Budget & Diff

Generiert: `logs/gen_soll_ist_tabelle.py` (Budget aus Char-JSON, Diff aus Build-Bericht `SOLL/IST-DIFF`, Ausrüstung aus `soll_ist_ausruestung.py`).

**Spalten:** genutzt/verfügbar — **Attr 5 · Fert 12 · Aufstiege rang-abhängig** (Anfänger 0 / Fortgeschritten 4 / Veteran 8…). **HP = ausgegebene/erworbene Handicap-Punkte** (erworben max 4; Nenner = was die Bogen-Handicaps einbringen). `⚠` = ungenutztes Budget (Rest > 0; bei HP oft bogenbedingt: Handicaps bringen mehr HP als der Bogen verausgabt). *Fehlende SOLL-Elemente* = Attribute/Fertigkeiten/Talente/Mächte unter Bogen-Soll. *Fehlende Ausrüstung* = FEHLT_KATALOG, durchweg **bewusste Flavor-/Quest-Items ohne Spielwerte** (echter Ausrüstungsmangel laut Analyzer = **0**, FEHLT_OFFEN = 0).

**176 Archetypen** · **105 ohne jede SOLL-Abweichung** (Budget voll genutzt, kein fehlendes SOLL-Element). Die übrigen 71 weichen ab — fast ausschließlich durch **Budget-Überzug des Bogens** (Bogen verlangt mehr als 5/12/4 hergeben → einzelne Skills/Talente unter Soll), kein Code-Bug.


## Deadlands (24 Chars · 17 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Agent | 5/5 | 12/12 | 4/4 | 4/4 | — | Marke der Agency (+1 Überreden bei gesetzestreuen Typen); Ersatz-GatlingTrommel |
| Chi-Meisterin | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | Seidenfächer; Umhängetasche; Mantel; Deine Fäuste (Stä+W4) |
| Cowgirl | 5/5 | 12/12 | 4/4 | 2.5/4 ⚠ | — | Gepanzerte Beinschützer (+1 Beine, +1 Reiten vs. Erschöpfung) |
| **Eingeborenen-Kundschafterin** † | 5/5 | 12/12 | 4/4 | 3.5/4 ⚠ | — | — |
| Entdecker | 5/5 | 12/12 | 4/4 | 4/4 | — | Jägerkleidung und -hut; Pfeife; Vergrößerungsglas; elegantes Monokel |
| Gepeinigter | 5/5 | 12/12 | 4/4 | 5/5 | — | Nadel und Faden |
| Gesegneter | 5/5 | 12/12 | 4/4 | 4/4 | — | Heiliges Kreuz und Ornat; abgewetzte Bibel |
| Hexe | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| **Investigativer Journalist** † | 5/5 | 12/12 | 4/4 | 4/4 | — | verschiedene Stifte und Griffel; Notizbuch; Tasche für Equipment |
| **Kopfgeldjäger** † | 5/5 | 12/12 | 4/4 | 4/4 | — | Bandelier; Stapel Steckbriefe |
| Krieger | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Medizinfrau | 5/5 | 12/12 | 2/3 ⚠ | 5/5 | — | Medizinbeutel; Knochenhalskette |
| Metallmagier | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | Smith & Robards Katalog |
| **Revolverheldin** † | 5/5 | 12/12 | 4/4 | 3.5/4 ⚠ | — (Wahrn+Ruhige Hände korrigiert via hp_talente+HP-Fallback) | — |
| **Salonschönheit** † | 5/5 | 12/12 | 4/4 | 4/4 | — (Überreden+Wahrn korrigiert via HP-Fallback) | — |
| Schamane | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| **Taschenspieler** † | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | Hoyles Buch der Spiele; zusätzliche in den Ärmeln versteckte Karten |
| Territorialer Ranger | 5/5 | 12/12 | 4/4 | 4/4 | — | Buch „Flüchtige vor der Justiz in den US-Territorien"; Rangerabzeichen (+1 Überreden bei gesetzestreuen Typen) |
| US-Marshal | 5/5 | 12/12 | 4/4 | 4/4 | — | US Marshal Marke |
| Vaquero | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | Gepanzerte Beinschützer (+1 Beine, +1 Reiten vs. Erschöpfung) |
| Verrückte Wissenschaftlerin | 5/5 | 12/12 | 2/3 ⚠ | 3.5/4 ⚠ | — | diverse Notizbücher und Schreibutensilien; verschiedene Spielereien; Laborkittel |
| Voodoopraktikerin | 5/5 | 12/12 | 2/3 ⚠ | 4/4 | — | Talisman; Voodooausrüstung |
| Wundarzt | 5/5 | 12/12 | 4/4 | 3.5/4 ⚠ | — | 2× dehydrierte Luft-Tabletten (10 Min. Luft im Mund); 2× taktiler Desensibilisator (–2 Wundabzüge, 10 Min.) |
| Zauberschützin | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | Groschenroman „Die Abenteuer von Doc Holliday"; Munitionspresse |

† = **2026-06-04 rebuild:** HP-Fallback für Fert & hp_talente-Mechanismus in `deadlands_build.py` ergänzt.
6 Chars (Eingeborenen-Kundschafterin, Investigativer Journalist, Kopfgeldjäger, Revolverheldin, Salonschönheit, Taschenspieler)
von Budget-Engpass bereinigt. Kern: Ungenutzte HP fließen in CharGen-Talente (2 HP = 1 Talent)
und Fert-Steigerungen (fehlende Skill-Schritte werden mit HP nachgekauft).

## Fantasy Kompendium (32 Chars · 27 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Akrobatin | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Alchemist | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Amazone | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Angrond, der Streuner † | 5/5 | 12/12 | 3/3 | 0/0 | — | — |
| Aristokrat | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Assassinin | 5/5 | 12/12 | 2/4 ⚠ | 3.5/4 ⚠ | — | — |
| Barbarin | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Barde | 5/5 | 12/12 | 4/4 | 4/5 ⚠ | — | — |
| Bogenschütze | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Champion | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Diebin | 5/5 | 12/12 | 4/4 | 4/5 ⚠ | — | — |
| Drachenkämpfer | 5/5 | 12/12 | 3/3 | 4/4 | — | — |
| Druidin | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Hexe | 5/5 | 12/12 | 4/4 | 4/4 | — | two prepared powers in chicken bones |
| Klerikerin | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Krieger | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Loremaster | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Magier | 5/5 | 12/12 | 0/4 ⚠ | 4/4 | — | — |
| Mönch | 5/5 | 12/12 | 4/4 | 4/4 | — | Bite/claws (Str+d8) |
| Narr | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Paladin | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Ritter | 5/5 | 12/12 | 4/4 | 4/5 ⚠ | — | — |
| Romoxosch, der Zwerg † | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Rüpel | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Schamane | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Schwerttänzerin | 5/5 | 12/12 | 2/4 ⚠ | 4/4 | — | — |
| Tiermeister | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Totemkrieger | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Tüftler | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Verteidiger | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Waldläufer | 5/5 | 12/12 | 4/4 | 4/5 ⚠ | — | — |
| Zauberer | 5/5 | 12/12 | 4/4 | 4/4 | — | — |

## Savage Pathfinder (30 Chars · 26 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Alahazra | 5/5 | 12/12 | 2/4 ⚠ | 0/0 | — | — |
| Alain | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Archetyp_Savage_Pathfinder_Barbarin_Amiri.json † | 5/5 | 7/12 ⚠ | 0/0 | 0/0 | — | — |
| **Balazar** † | 5/5 | 12/12 | 3/4 ⚠ | 0/0 | — | — |
| Brokar | 5/5 | 12/12 | 2/4 ⚠ | 0/0 | — | — |
| **Damiel** † | 5/5 | 12/12 | 4/4 | 0/0 | — (Bevorzugte Klasse_schwer ergänzt + Diebeskunst W6 via HP-Fallback) | — |
| **Darla** † | 5/5 | 12/12 | 2/4 ⚠ | 0/0 | — (AH (Magie)→AH (Magier) fix + pathfinder_klassentalent-Pfad) | — |
| **Darla_ohneKlasse** †† | 5/5 | 12/12 | 4/4 | 4/4 | — (AH (Magier) per Klassentalent nachgeholt, Mächte manuell ergänzt) | — |
| Ezren | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Fariel** † | 5/5 | 12/12 | 4/4 | 0/0 | — (Überleben W6 via HP-Fallback erreicht) | — |
| **Feiya** † | 5/5 | 12/12 | 4/4 | 0/0 | — (Wachsam→Aufmerksamkeit fix + HP-Fallback) | — |
| **Gnor** †† | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — (Zaubern W8 per Aufstieg nachgeholt, Doppelkosten 1 Aufst.) | — |
| Harsk | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Imrijka** †† | 5/5 | 12/12 | 4/4 | 3.5/4 ⚠ | — (Überleben W4 per Aufstieg nachgeholt) | — |
| Kira | 5/5 | 12/12 | 2/4 ⚠ | 0/0 | — | — |
| Korva | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Kyra | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Lem | 5/5 | 11/12 ⚠ | 4/4 | 0/0 | — | — |
| Lini | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Madda** †† | 5/5 | 12/12 | 4/4 | 3.5/4 ⚠ | — (Heimlichkeit W6 per Aufstieg nachgeholt) | — |
| **Marn** †† | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — (Rundumschlag per Aufstieg nachgeholt) | — |
| Merisiel, die Schurkin † | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Paelie** † | 5/5 | 12/12 | 4/4 | 0/0 | — (Zaubern W8 via HP-Fallback erreicht) | — |
| Sajan | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Seelah, die Paladinin † | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Seoni | 5/5 | 11/12 ⚠ | 4/4 | 0/0 | — | — |
| Sil | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Teller** †† | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — (Schießen+Heimlichkeit per Aufstieg nachgeholt) | — |
| Valeros, der Kämpfer † | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Zyril | 5/5 | 12/12 | 4/4 | 0/0 | — | — |

† = Build-Script-Fix 2026-06-04 (HP-Fallback + Namenskorrektur).
†† = D-Advance-Nachschiebung 2026-06-04 (Rang Fortgeschritten, fehlende Skills/Talente per Aufstiege bezahlt).

## SciFi Kompendium (36 Chars · 15 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| AIController | 4/5 ⚠ | 12/12 | 4/4 | 3.5/4 ⚠ | — | — |
| Ambassador | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Analyst | 4/5 ⚠ | 11/12 ⚠ | 2/4 ⚠ | 3.5/4 ⚠ | — | — |
| BountyHunter | 5/5 | 12/12 | 0/0 | 4/4 | — | — |
| Chronomancer | 5/5 | 12/12 | 0/4 ⚠ | 3.5/4 ⚠ | — | — |
| Commander | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Commando | 5/5 | 12/12 | 2/2 | 4/4 | — | — |
| Cyborg | 5/5 | 12/12 | 0/2 ⚠ | 3.5/4 ⚠ | — | — |
| Enforcer | 5/5 | 12/12 | 0/0 | 3.5/4 ⚠ | — | — |
| Engineer | 5/5 | 11/12 ⚠ | 0/4 ⚠ | 2.5/4 ⚠ | — | — |
| Envoy | 5/5 | 11/12 ⚠ | 0/3 ⚠ | 4/4 | — | — |
| Gladiator | 5/5 | 8/12 ⚠ | 0/4 ⚠ | 4/4 | — | — |
| Gravlock | 5/5 | 12/12 | 2/4 ⚠ | 4/4 | — | — |
| Grunt | 5/5 | 9/12 ⚠ | 2/4 ⚠ | 4/4 | — | — |
| Hacker | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| HardlightConjurer | 5/5 | 12/12 | 0/1 ⚠ | 4/4 | — | — |
| Infiltrator | 5/5 | 12/12 | 3/4 ⚠ | 3.5/4 ⚠ | — | — |
| Influencer | 5/5 | 12/12 | 2/4 ⚠ | 4/4 | — | — |
| Medic | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | — |
| Mercenary | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Morpher | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Mystic | 5/5 | 12/12 | 4/4 | 3.5/4 ⚠ | — | — |
| Pilot | 5/5 | 12/12 | 2/4 ⚠ | 2.5/4 ⚠ | — | — |
| Psyker | 5/5 | 11/12 ⚠ | 4/4 | 4/4 | — | — |
| RoadWarrior | 5/5 | 11/12 ⚠ | 0/0 | 4/4 | — | — |
| Roughneck | 5/5 | 11/12 ⚠ | 4/4 | 4/4 | — | — |
| Scavenger | 5/5 | 12/12 | 0/4 ⚠ | 4/4 | — | — |
| Scrapper | 5/5 | 10/12 ⚠ | 0/3 ⚠ | 4/4 | — | — |
| Shepherd | 5/5 | 12/12 | 0/4 ⚠ | 3/4 ⚠ | — | — |
| Smuggler | 4/5 ⚠ | 12/12 | 2/4 ⚠ | 2/4 ⚠ | — | — |
| Spacer | 5/5 | 12/12 | 3/4 ⚠ | 4/4 | — | — |
| SquadLeader | 5/5 | 12/12 | 2/4 ⚠ | 4/4 | — | — |
| StarKnight | 5/5 | 12/12 | 0/0 | 1.5/4 ⚠ | — | — |
| Surveyor | 5/5 | 12/12 | 4/4 | 4.5/5 ⚠ | — | — |
| Technomancer | 5/5 | 12/12 | 0/2 ⚠ | 4/4 | — | — |
| Warper | 5/5 | 12/12 | 0/4 ⚠ | 4/4 | — | — |

## Horror Kompendium (36 Chars · 23 ✓)

> **Update 2026-06-05 (Rebuild nach Völker-Fix + PDF-Content-Integration):** Die SOLL liest
> auto-Handicaps/-Talente jetzt zur Laufzeit aus `settings/Horror Kompendium.json`
> (`_load_volk_auto()` in `build_horror_all.py`) → keine veralteten Völker-Diffs mehr.
> Demon/Revenant/Phantom/Werewolf jetzt **diff=0**. Verbleibende Diffs = 3 Klassen:
> (a) **HP-Limit** (Mummy `Schwerzüngig`, Patchwork `Rachsüchtig_schwer` — 4. Handicap passt nicht in 4 HP);
> (b) **Mächte-Slot-Limit** (Demonologist `Bannung`/`Flächenschlag`, Mummy `Eigenschaft erhöhen/senken`/`Heilung`,
> Witch `Fluchwort`/`Geisterruf` — Keys existieren; `neue_maechte` der AHs ggf. zu knapp);
> (c) **Punktebudget** (Doctor Stärke, Vampire Willenskraft/Einschüchtern/Überreden, Angel Einschüchtern).
> Die SOLL-Spalte der Tabelle ist teils aus früheren Läufen; maßgeblich sind die 3 Klassen oben.

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Angel | 5/5 | 12/12 | 4/4 | 7/7 | fertigkeiten: Einschüchtern soll W6, ist W8 (überzählig) | — |
| Aristocrat | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Burglar | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Constable | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Demon | 5/5 | 12/12 | 3/3 | 6.5/7 ⚠ | — | — |
| Demonologist (Monstrous) | 5/5 | 12/12 | 3/3 | 13/13 | — (4 Mächte via 2× Neue Mächte + Aufstiege nachgeholt) | — |
| Doctor | 5/5 | 12/12 | 4/4 | 5/5 | attribute: Stärke soll W4, ist W6 | — |
| Exorcist | 5/5 | 12/12 | 4/4 | 4/4 | handicaps: "Schwur_schwer" FEHLT (Budget: nur Schwur_leicht, bräuchte 1 HP mehr) | — |
| Explorer | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Gamer | 5/5 | 12/12 | 4/4 | 5/5 | — | — |
| Ghost Hunter | 5/5 | 12/12 | 3/4 ⚠ | 4.5/5 ⚠ | — | — |
| Gumshoe | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Jock | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Journalist | 5/5 | 12/12 | 4/4 | 5/5 | — | — |
| Librarian | 5/5 | 12/12 | 4/4 | 5/5 | — | — |
| Magician | 5/5 | 12/12 | 4/4 | 5/5 | — (Bannung via Neue Mächte +1 Aufstieg nachgeholt) | — |
| Mambo | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Mummy | 5/5 | 12/12 | 4/4 | 7.5/8 ⚠ | — (Setting-Bug: Volk-auto-HCs hatten falsche Keys) | — |
| Nemesis | 5/5 | 12/12 | 3/3 | 11/11 | handicaps: "Geheimnis_leicht" FEHLT | — |
| Nerd | 5/5 | 12/12 | 4/4 | 5/5 | — | — |
| Occultist | 5/5 | 12/12 | 2/2 | 4/4 | — | — |
| Party Animal | 5/5 | 12/12 | 3/4 ⚠ | 4.5/5 ⚠ | — | — |
| Patchwork Man | 5/5 | 12/12 | 4/4 | 7/7 | handicaps: "Rachsüchtig_schwer" FEHLT | — |
| Phantom | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Psychic | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — | — |
| Revenant | 5/5 | 12/12 | 4/4 | 7/7 | — (Setting-Bug: Schwur_schwer jetzt korrekt auto vom Volk) | — |
| Runner | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Sailor | 5/5 | 12/12 | 4/4 | 5/5 | — | — |
| Slayer | 5/5 | 12/12 | 4/4 | 10.5/11 ⚠ | — | — |
| Socialite | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Soldier | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Survivor | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Swamp Freak | 5/5 | 12/12 | 3/3 | 8.5/9 ⚠ | — | — |
| Vampire | 5/5 | 12/12 | 4/4 | 5/5 | handicaps: "Angewohnheit_schwer" FEHLT | — |
| Werewolf | 5/5 | 12/12 | 4/4 | 11/11 | — | — |
| Witch | 5/5 | 12/12 | 3/3 | 5.5/6 | — (Fluchwort+Geisterruf via Neue Mächte +1 Aufstieg nachgeholt) | — |

## Superkräfte Kompendium (11 Chars · 11 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Bogenschuetze | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Detektiv | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Eismann | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Feuervogel | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Hexe | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Panzer | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Schlaeger | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Schuetze | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Sprinter | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Verteidiger | 5/5 | 12/12 | 4/4 | 4/4 | — | — |
| Walkuere | 5/5 | 12/12 | 4/4 | 4/4 | — | — |

## SWAE (13 Chars · 11 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Arthan, der Priester † | 5/5 | 12/12 | 4/4 | 0/0 | — | Kettenhemd |
| Elsiara | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Kenaken | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Nachtfinder | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Arthan (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Kettenhemd |
| **Beatriz (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | 9mm-Pistole, Polizeiauto |
| **Clementine (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Revolver, Van |
| **The Shroud (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | Wahrnehmung W4 statt W6 (Provoz W6 > Verstand W4 Doppelkosten frisst 1 FP) | Cape, Maske |
| **Aidan (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Machete, Lederjacke |
| **Sozius (Worlds of Ulisses)** | 5/5 | 12/12 | 3/3 | 0/0 | Aufmerksamkeit-Talent fehlt (Pilot W10 mit Geschick W8 Doppelkosten ab W8, nur 1 HP übrig statt 2) | Eruptor-Blaster, E-Schild (SciFi) |
| **Samael (Worlds of Ulisses)** | 5/5 | 12/12 | 3/3 | 0/0 | — (Diff fuzzy-match maskiert „Beidhändiger Fernkampf" – real geprüft alles da) | Eruptor-Blaster x2, MuSP-Anzug (SciFi) |
| **Asera (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Flammengewehr, Schockstab, Lederwams (SciFi) |
| **Zoetta (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Eruptor-Blaster, Lederwams (SciFi); Säbel |

**2026-06-04 Daten-Updates (User-Patch):**
- HC `Fies` (leicht, 1 HP) im SWAE-Setting ergänzt → Shroud nutzt jetzt vollen 4-HP-Pool.
- Fertigkeit `Fluggeräte lenken` = `Pilot` (Geschicklichkeit) im SWAE-Setting bestätigt → Sozius
  Bogen-Skill W10 jetzt mit Doppelkosten ab W8 korrekt abgebildet.

## HeXXen 1773 (6 Chars · 4 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Jeanne | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| Klara (alt) | 5/5 | 12/12 | 4/4 | 0/0 | — | — |
| **Raphael (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Plattenrüstung mit Helm (HeXXen hat nur Brustharnisch/Armschienen/Beinschienen Platte) |
| **Jeanne (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | — | Lederjacke (HeXXen hat nur „Lederkoller") |
| **Klaas (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 0/0 | Heimlichkeit W4 statt W6; Wahrnehmung W4 statt W6 (Kämpfen W12 + Geschick W8 frisst 7 FP via Doppelkosten ab W8) | Rapier (HeXXen hat „Fechtwaffen/Parierdolch"); Lederjacke |
| **Klara (Worlds of Ulisses)** | 5/5 | 12/12 | 4/4 | 3/4 ⚠ | — (Schießen+Wahrn per D-Advance nachgeholt, Rang Fortgeschritten) | — |

## HeXXen1773 (1 Chars · 1 ✓)

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Raphael, der Ordenskrieger † | 5/5 | 12/12 | 4/4 | 0/0 | — | — |

(Alter Tippfehler im Setting-Namen: `HeXXen1733` statt `HeXXen 1773`. Datei: `Archetyp_HeXXen1733_Ordenskrieger_Raphael.json`.)

## Savage Aventurien (4 Chars · 4 ✓ — NEU 2026-06-04)

DSA-Set aus „Worlds of Ulisses Archetypen" (4 von 20 Karten):

| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |
|---|---|---|---|---|---|---|
| Leomara, die Kriegerin | 5/5 | 12/12 | 2/4 ⚠ | 0/0 | — | Gambeson; Kriegerbrief (Flavor) |
| Hesindian, der Magier | 5/5 | 12/12 | 1/4 ⚠ | 0/0 | — | Magierstab (per Stab abgebildet); Reiserobe (Flavor) |
| Romoxosch, der Zwerg | 5/5 | 11/12 ⚠ | 4/4 | 0/0 | — | (Werkzeug zur Fallenentschärfung = Diebeswerkzeuge) |
| Angrond, der Streuner | 4/5 ⚠ | 12/12 | 3/3 | 0/0 | — | Lederweste (Aventurien hat nur Rüstung-Varianten) |

**Reload-Hinweis:** Romoxosch + Angrond existieren auch unter `Fantasy Kompendium`
(`Archetyp_DSA_*.json`, ältere Builds) — neuere Aventurien-Builds liegen unter
`Archetyp_Savage_Aventurien_*_A.json`. Beide sind valide; je nach Setting-Wahl des Users.

**AH-Auto-Cascade Aventurien (verifiziert mit Hesindian):** `AH (Magier)` legt automatisch
3 Talente (`Schule`, `Arkane Verbindung`, `Zauberbücher`) + 3 Handicaps (`Materialkomponenten`,
`Behindernde Rüstung_jede`, `Behindernde_Rüstung_schwer`) + 15 MP an. Die SWAE-Variante des
Bogens (PDF zeigt extra „Machtpunkte" für 15 MP) ist für Aventurien **doppelt** — Aventurien
liefert bereits 15 MP via AH.
---

## 2 · Echte Code-Bugs — BEHOBEN

| Bug | Datei | Fix |
|---|---|---|
| **Negatives Aufstiegsbudget**: Guard `> 0` statt `>= kosten` → Talent-Advance (Kosten 1) genehmigt bei `verbleibende_aufstiege == 0.5` (Skill-Advance kostet 0.5) → Saldo −0.5 in 9 gespeicherten Horror-Chars | `functions/talent_funktionen.py:1078` | Guard `>= aufstieg_kosten`. Regression: 0 negative Budgets, 0 Crashes |
| **Endlosschleife** Attribut-Advance-`while` ohne „Wert-unverändert"-Break (Swamp-Freak-Log 3.4 MB, 33 688× ok=False) | `logs/build_horror_all.py` | `attr_steps`-Cap + Break; Log danach 7 KB |
| **Force-Buy-Bug** Ausrüstung bei Geldmangel | `functions/ausruestung_funktionen.py:42/100/312` | behoben (User-Freigabe) |
| **`AH (Beschwörer)`** hatte `kategorie: Hintergrund` statt `Klasse` → nicht als Pathfinder-Klassentalent wählbar | `settings/Savage Pathfinder.json` | neues `Beschwörer`-Klassentalent (Klasse) + `Eidolon`-Talent |
| **`Der Beste`-Edge ohne Effekt**: Kraftobergrenze = halbe (nicht drittel) max. SKP nicht umgesetzt | `functions/superkraft_funktionen.py` | `_berechne_kraftobergrenze()` + Listener `_aktualisiere_kraftobergrenze()` |
| **(2026-06-05) Horror-Kompendium Volk-`auto_handicaps`: falsche Keys (ohne Stufen-Suffix)** → `'Schwur'` statt `'Schwur_schwer'`, `'Langsam'` statt `'Langsam_leicht'` → auto-apply schlug still fehl. Betroffen: Engel, Mumie, Wiedergänger (Angel, Mummy, Revenant). | `settings/Horror Kompendium.json` | Keys korrigiert: `Schwur_schwer`, `Langsam_leicht`. 3 Chars neu gebaut. |
| **Provozieren→Willenskraft** fälschlich gemappt (SciFi + Superkräfte; korrekt →Verstand) → vermeidbare Doppelkosten | `settings/SciFi Kompendium.json`, `settings/Superkräfte Kompendium.json` | →Verstand; betroffene Builds neu gebaut |
| **(2026-06-04) Freier AH ohne Klasse: `waehle_talent` returnt `"pathfinder_kostenlos_angeboten"`-String** → `bool(result)` = True, aber Talent nicht in `selected_talente` → Auto-Cascade ausbleibend, Mächte nicht wählbar | `controllers/charakter_controller.py:1063` / `functions/talent_funktionen.py:145` | Umgehung in Build-Skript: `s.pathfinder_klassentalent(freier_ah)` statt `s.talent(freier_ah)`. Betrifft Darla (SPF). |
| **(2026-06-04) Deadlands-Builds: HP ungenutzt in CharGen, Talente/Skills fehlen in D-Advances** → bei 6 Chars HP-Rest 2–4 ungenutzt wegen fehlender HP-Fallback-Logik für Fert & hp_talente-Mechanismus | `logs/deadlands_build.py` | `hp_talente`-Parameter ergänzt (2 HP = 1 Talent in CharGen) + HP-Fert-Fallback nach Talente-Fertig-Abschluss. 6 Chars korrigiert. |

## 3 · Echte Code-Bugs — OFFEN

Aus dem Deadlands-Lauf (2026-05-31); im Build umgangen, **Code-Fix steht aus** (alle Settings betroffen):

1. **AH-Talente als D-Advances scheitern** trotz `ignore_voraussetzungen=True`: Flag wird nur in
   `_waehle_mit_handicap_punkten` geprüft/zurückgesetzt, **nicht** in `_waehle_mit_aufstieg`
   (`charakter_controller.py:514` setzt Flag, `talent_funktionen.py:~1040` prüft es nur auf einer Route).
2. **Mächte als D-Advances** nach `char_gen_completed=True` nicht über `waehle_macht` wählbar.
   → Spätere Builds umgehen das per `('talent','Neue Mächte') + ('power',X)`-Advances.
3. **`rang` teils `None` in der JSON** für nicht abgeschlossene (Anfänger-)Builds; für abgeschlossene
   korrekt. ⇒ Rang ist kein verlässliches Korrektheitssignal (vgl. Tabellenspalte „Aufst").
4. **Loader verwirft Mächte mit nicht-int `machtpunkte` stillschweigend** (2026-06-05, Horror): Mächte,
   deren `machtpunkte` keine Zahl ist (z.B. PDF „Speziell" bei `Dämon beschwören`/`Exorzismus`), erscheinen
   nach dem Laden **gar nicht** in `ch.maechte` — kein Fehler, keine Warnung. Workaround im Setting: als `0`
   + Hinweis in der Beschreibung. → Loader sollte non-int MP abfangen/normalisieren statt zu droppen.

*Test-Treiber (kein App-Bug):* `driver.fertigkeit_auf()` wirft `KeyError` bei unbekanntem Skill statt
Anomalie → im Build mit `if name in ch.fertigkeiten` geguardet.

## 4 · Daten-Lücken (Setting-JSON)

**Behoben (2026-06-04):** Deadlands `Sprache`-Fertigkeit (jetzt 31) · Savage Pathfinder
`Beschwörer`/`Eidolon`/`Banner` · SciFi Phase G (2 Edges, 3 HC, 29 Items, 2 Völker).

**Behoben (2026-06-05) — Horror Kompendium gegen Kauf-PDF (US85083), Details in `logs/horror_setting_review.md`:**
- **Völker PDF-konform:** auto_handicaps korrigiert (Dämon → `Schwäche (Kaltes Eisen)`; −`Auffällig`/`Hässlich`
  und erfundene Keys bei Engel/Mumie/Flickenmonster/Wiedergänger), Attribut-Boni ergänzt, Dämon
  `panzerung_2`/`natuerliche_waffen`/`furchteinflössend` entfernt (sind Talente, keine Volkseigenart).
  Neues Handicap `Schwäche (Kaltes Eisen)`.
- **Integriert (Original-PDF-Namen):** Fertigkeit `Alchemie`; 14 Mächte (Exorzismus, Albträume, Kadaversinn,
  Seance, Boden weihen, Dämon beschwören, Aspekt/Zorn der Loa, Verriegeln/Entriegeln, …); 4 Edges (Courage,
  Final Girl/Guy, Betagt, Furchterregend); ~52 Race-Monster-Talente (Klauen, Panzerhaut, Nebelform,
  Bezaubern, Todesberührung, …). **Talente 174→230, Mächte 68→82, Fertigkeiten 33→34.**
- **Keys auf PDF-Namen umbenannt** (Horror + Rippers): `Unerschütterlich`→`Unerbittlich`, `Visionen`→`Seher`,
  `Stiller Wirker`→`Stillzauberer`, `Schreikönigin/Schreikönig`→`Scream Queen/King`.
- **Build-Stale-Fix:** `VOLK_AUTO` liest auto-HCs/-Talente jetzt zur Laufzeit aus dem Setting-JSON.

**Offen (Empfehlung):**
- **SWAE (~8):** Mobiltelefon, Glock 9mm, Beretta M92SB, Malaydoskop, Schnappmesser, Flachmann, Schalldämpfer.
- **SWAE Worlds-of-Ulisses (2026-06-04):** beim Bauen aller 9 Ulisses-SWAE-Bögen beobachtet:
  - ~~Handicap `Fies` fehlt~~ → **ergänzt 2026-06-04 vom User** (`Fies`, leicht=1HP).
  - ~~Fertigkeit `Fluggeräte lenken` fehlt~~ → **klar: SWAE-Skill heißt `Pilot`** (Geschick) — Build
    nutzt jetzt `Pilot`, Bogen-W10 mit Doppelkosten ab W8 korrekt abgebildet.
  - Handicap `Dünnhäutig_schwer`-Variante fehlt (SWAE hat nur `Dünnhäutig`=leicht; Sozius-Bogen sagt SCHWER) — **offen**.
  - Lederwaren-Item-Familie fehlt (`Lederjacke`, `Lederweste`, `Lederwams`, `Lederrüstung`) —
    relevant für Beatriz, Jeanne (HeXXen), Shroud, Aidan, Asera, Zoetta. SWAE hat nur Kevlar/Polymer.
  - SciFi-Items: `Eruptor-Blaster`, `E-Schild`, `MuSP-Anzug`, `Flammengewehr`, `Schockstab`, `Lederwams`
    fehlen — Sozius/Samael/Asera/Zoetta benötigen sie. Hinweis: SciFi Kompendium hat passende
    Alternativen (siehe Diskussion mit User).
  - `Kettenhemd` als kombiniertes Item fehlt (SWAE hat nur Einzelteile `Hemd (Kette)` / `Helm (Kette)` /
    `Beinlinge (Kette)`) — Arthan-Bogen.
  - `Machete`, `Cape/Maske`, `Polizeiauto`, `Van`, `Revolver` (im modernen Sinne) — diverse Items
    fehlen für die modernen Worlds-of-Ulisses-Karten (Beatriz, Clementine, Shroud).
- **HeXXen 1773 Worlds-of-Ulisses:** `Plattenrüstung mit Helm` als kombiniertes Item, `Rapier` (HeXXen
  hat nur `Fechtwaffen/Parierdolch`), `Lederjacke` (HeXXen hat nur `Lederkoller` — semantisch ähnlich,
  aber namentlich verschieden) — Raphael / Klaas / Jeanne.
- **Savage Aventurien Worlds-of-Ulisses:** `Gambeson` (Aventurien hat keine Tuchrüstung-Entsprechung
  unter diesem Namen), `Reiserobe`, `Lederweste` (nur Volltrucksysteme).
- **Sundered Skies (~6):** Eichendornrüstung, Schwebeöl, Schlafleintuch, Wasserschlauch, Kugeln mit Schießpulver.
- **SciFi (7):** Handbeil-Variante, Slugthrower, Plasmawerfer, Linienprojektor, Biolink, Schneidbrenner, Elektronisches Schloss.
- **FK / SPF:** diverse Tränke + Spezialitems (Flavor), ~15 FK-Archetypen + 2 SPF.

## 5 · Ausrüstung SOLL/IST — Endstand

`logs/soll_ist_ausruestung.py` (Deadlands/FK/SciFi/Superkräfte): **FEHLT_OFFEN = 0**,
**FEHLT_KATALOG = 39** — alle bewusst **keine** Katalog-Items (Flavor/Quest ohne Spielwerte; in der
Tabelle oben Spalte „Fehlende Ausrüstung"). **Echte Lücke: 0.**
- **Deadlands:** 7 Grundbuch-Waffen ergänzt (114→121), `EXTRA_GEAR`-Map, 24 Chars neu → OFFEN 0.
- **Superkräfte (2026-06-04):** Regelwerk-Kap. 2 vollständig außer Fahrzeuge (3/5) → **Peregrine-Sprungjet**
  + **Grizzly-Gefechtspanzer** ergänzt (Fahrzeuge 3→5, ausruestung 219→221).
- **Quirk:** Katalog-Key `Kugeln (mit Schwarzpulver) …` wird beim Hinzufügen **depluralisiert**
  (`Kugel …`) → bei Namens-Vergleichen Singular/Plural tolerieren.

## 6 · Dokumentierte Nicht-Bug-Anomalien (erwartet)

- **Budget-Überzug der Bögen:** viele Bögen verlangen mehr als 5 Attr + 12 Skill + 4 HP hergeben →
  `talent(...) ok=False` in CharGen (später per Advance/Topup), einzelne Skills/Attribute unter Soll
  (z. B. Wahrnehmung W4 statt W6). **Hauptursache der 71 Tabellen-Abweichungen. Kein Code-Bug.**
- **GELDMANGEL-FORCE-Käufe** (v. a. FK): Preise > Startkapital → `force_bei_geldmangel=True`.
- **Doppelkosten projektweit (`logs/check_doppelkosten.py`, 157 Archetypen):** 90 Doppelkosten,
  **90 inhärent / 0 vermeidbar** (Bogen gibt Skill > Attribut vor). 3 ehemals vermeidbare behoben.
  Skill→Attribut-Mapping ist **setting-spezifisch**.
- **HP-Limit-Rejections** (Druidin/Magier FK; Monster-Völker Horror): Major-HC korrekt abgelehnt;
  Volk-Auto-Handicaps zählen nicht zur 4-HP-Bilanz (`volk.py:291`).
- **Superkräfte-Kraftobergrenze:** Einzelkräfte > 15 SKP bei Stufe III abgelehnt — dokumentiert;
  per `Der Beste`-Edge auf halbe SKP anhebbar.

## 7 · Werkzeuge & Skripte

- **Tabelle oben:** `logs/gen_soll_ist_tabelle.py` (regenerierbar)
- **Builds:** `logs/deadlands_build.py`, `build_horror_all.py`, `build_scifi_batch1/2.py`,
  `build_sfc_phase_g.py`, `build_supers.py`, `build_spf_set23_v2.py`,
  **`logs/ulisses/build_swae.py`** (9 chars), **`build_hexxen.py`** (4 chars),
  **`build_aventurien.py`** (4 chars), **`dump_keys.py`** (3 keys.json)
- **Audits:** `soll_ist_ausruestung.py` (Ausrüstung), `check_fehlende_ausruestung.py` (Katalog-Lücken,
  EN→DE-Alias), `check_doppelkosten.py` (Doppelkosten)
- **Treiber:** `.claude/skills/archetyp-erstellen/driver.py` (immer `SDL_VIDEODRIVER=dummy`, **nie**
  `KIVY_WINDOW=mock`; Exit-Code ignorieren, JSON-Bericht maßgeblich)
- **PDF-Soll-Audit:** Render+Crop+Zoom (`pdftoppm` → PNG, visuell) statt `pdftotext` (Low-Res
  verwischt d4/d6/d8). Stichprobe 35/36 Horror-Attribute = Bogen.

## 8 · Worlds of Ulisses (2026-06-04) — 17 neue Builds aus Textvorlage

**Quelle:** `Texte/Worlds_of_Ulisses_Archetypen.txt` (20 Karten). Vorhanden: 5 (Elsiara, Kenaken,
Nachtfinder + DSA Romoxosch/Angrond unter Fantasy Kompendium). Neu gebaut: **15** (+2 als
Aventurien-Reload der DSA-Chars; gesamt 17).

**Setting-Zuordnung (per User):** SWAE für moderne/Standard-Karten (9 Chars), HeXXen 1773 für
historische Fantasy (4 Chars), Savage Aventurien für DSA-Set (2 neu + 2 Reload = 4 Chars).

**Ergebnis:** 15/17 ohne Abweichungen (nach User-Daten-Patches 2026-06-04: `Fies` + `Pilot`).
Verbliebene 2 Abweichungen sind **echte Bogen-Budget-Engpässe**, kein Code-/Daten-Bug:
- **Shroud:** Provozieren W6 vs. Verstand W4 = Doppelkosten ab dem 1. Schritt → 1 FP zu wenig
  für Wahrnehmung W6 (auch nur 1 Doppelkosten-Schritt). 4 HP nicht ausreichend.
- **Sozius:** Pilot W10 mit Geschick W8 = Doppelkosten ab W8 (2 FP für W8→W10 + 2 FP für W10
  würden 4 FP frisst) + V W4→W8 brauchte 2 HP — Aufmerksamkeit (2 HP) passt nicht in den
  3-HP-Pool. Trade-off: V W8 ✓ vs. Aufmerksamkeit ✓ — Bogen-Design.
- **Klaas (HeXXen):** Kämpfen W12 + Geschick W8 frisst durch Doppelkosten ab W8 ganze 7 FP →
  Heim+Wahrn bleiben W4 statt W6.
- **Klara (HeXXen):** Bogen verlangt 6 HP-Äquivalente bei 4 HP Bilanz — Machtpunkte-Talent
  priorisiert (MP=15 ✓), dafür Schießen+Wahrnehmung W4 statt W6.

**Keine echten Code-Bugs gefunden.** Reine Bogen-Budget-Trade-offs (Doppelkosten frisst Budget,
wenn Bogen Fert ≥ Attr verlangt).

**Helper-Priorisierung** (`logs/ulisses/build_swae.py`/`build_hexxen.py`):
`Attr regulär → Attr HP → Fert regulär → bezahlte Talente HP → Fert HP-Fallback`.
So bekommen Bogen-Attribute Vorrang vor Talenten, und Bogen-Talente Vorrang vor einzelnen
Skill-Pips — was die Bogen-Intention am besten trifft.

**PDF-Hinweis** (vom User): Karten-Vorderseite oben-links + Rückseite unten-rechts auf nächster
Seite. Beim Parsen des Textes mussten die 4 Handicap/Talent/Ausrüstung-Blöcke pro Doppelseite
korrekt den 4 Vorderseiten zugeordnet werden. Verifiziert über inhaltliche Marker (AH-Type,
Klassen-Talent, Volk-Bezug).

---

## Audit Horror Kompendium: Völker-Handicaps vs. Kauf-PDF (US85083, 2026-06-05)

Quelle: `logs/pdf_extracted/US85083_Horror-Kompendium_KaufPDF_250210_LZ_meta.pdf`
(Völker-Kapitel „Monströse Helden", Buchseiten 12–23). Verglichen mit
`settings/Horror Kompendium.json` (`effects.auto_handicaps`) und den
Archetyp-JSONs `chars/Archetypen/Archetyp_Horror_*.json`.

### A) Volks-Handicaps: PDF vs. Setting-JSON

| Volk | PDF-Handicaps (offiziell) | JSON auto_handicaps | Befund |
|------|---------------------------|---------------------|--------|
| Engel | Schwur (schwer) [Diener des Himmels] | Schwur_schwer, **Auffällig** | `Auffällig` erfunden — kein „himmlische Aura"-Handicap im PDF |
| Dämon | Schwäche (Kaltes Eisen) | **Böse**, **Schwäche (Geweihtes Wasser)** | Weakness FALSCH (PDF = Kaltes Eisen!); `Böse` ist im PDF nur empfohlen, nicht automatisch. JSON-intern widersprüchlich: `besonderheiten` listet korrekt „Schwäche: Kaltes Eisen", `auto_handicaps` aber „Geweihtes Wasser" |
| Mumie | Langsam, Schwäche (Feuer) | **Hässlich**, Langsam_leicht, Schwäche (Feuer) | `Hässlich` erfunden (PDF: „nicht mehr als andere Untote") |
| Flickwerk (Flickenmonster) | Phobie (Feuer, schwer) [Feuer schlecht!], Verpeilt [Todesdunst], Schwäche (Feuer) | **Hässlich, Außenseiter, Schwerfällig**, Schwäche (Feuer), **Schwäche (Elektrizität)** | FEHLEND: Phobie(schwer), Verpeilt. ERFUNDEN: Hässlich, Außenseiter, Schwerfällig, Schwäche(Elektrizität). Auch auto_talente falsch: PDF = Berserker + Arkane Resistenz; JSON = Zäh, Kräftig |
| Phantom | Schwäche (Salz) | Schwäche (Salz) | ✓ korrekt |
| Wiedergänger | Schwur (schwer) [Vergeltung] | Schwur_schwer, **Hässlich** | `Hässlich` erfunden (PDF: Gestank ist ein optionales Talent, kein Auto-Handicap) |
| Vampir | Hunger=Angewohnheit(schwer) + Schwächen-Menü (Sonnenlicht, Pflock, Weihwasser, Fließendes Wasser, Heiliges Symbol, Nur auf Einladung) | Abhängigkeit(Blut), Schwäche(Sonnenlicht), Schwäche(Pfahl), Schwäche(Geweihtes Wasser) | ✓ plausible Auswahl aus dem Menü |
| Werwolf | Schwäche (Silber), Stumm/„Kann nicht sprechen" (in Wolfsform) | Blutdurst, Schwäche (Silber) | Silber ✓; `Blutdurst` nicht explizit (PDF: Vollmond-Verwandlungszwang); „Stumm" fehlt |

### B) Archetypen-Konsistenz (Volks-Handicaps)

Alle monströsen Archetypen tragen exakt die `auto_handicaps` ihres Volks — mit zwei Ausnahmen:

- **Archetyp_Horror_Mummy**: trägt zusätzlich `Schwerfällig`, das die Mumie gar nicht gewährt
  (weder JSON-Volk noch PDF). → manuell hinzugefügt, inkonsistent.
- **Archetyp_Horror_Patchwork_Man**: trägt `Phobie_schwer` + `Verpeilt` — das sind die
  PDF-korrekten Flickwerk-Handicaps, die das Volk `Flickenmonster` im JSON aber NICHT auto-setzt.
  → Archetyp wurde von Hand korrigiert, Setting-Daten nicht nachgezogen. Wer im Tool frisch ein
  Flickenmonster baut, bekommt einen anderen Handicap-Satz als dieser Archetyp.

### C) Weitere Volk-Abweichungen (über Handicaps hinaus)

- **Attribut-Boni fehlen großteils**: PDF gewährt permanente Würfeltyp-Erhöhungen, JSON hat oft `attribute_bonuses: {}`:
  - Dämon: Konstitution +1 (Höllische Ausdauer), Willenskraft +1 (Mutig) — FEHLEN
  - Mumie: Stärke/Konstitution +2 Würfeltypen — FEHLEN
  - Phantom: Willenskraft +1 (Starker Wille) — FEHLT
  - Wiedergänger: Stärke/Konstitution +1 — FEHLEN
  - Vampir: Konstitution-Bonus fehlt; Stärke nur +1 statt +2 Würfeltypen; `bewegungsweite_bonus:2` ist im PDF nicht belegt
  - Engel/Flickwerk: +2 (=ein Würfeltyp) statt PDF +2 Würfeltypen (=+4)
  - Werwolf: alle Boni leer — evtl. bewusst, da „nur in Werwolfgestalt" (Designentscheidung)
- **Dämon-Besonderheiten über-gewährt**: „Natürliche Waffen", „Panzerung +2" sind im PDF
  TALENTE (Klauen/Biss/Panzerhaut), keine Basis-Rassenmerkmale; „Resistenz Feuer" statt PDF
  „Widerstand gegen Kälte/Elektrizität/Hitze".

### D) STATUS: BEHOBEN (2026-06-05)

Setting-JSON `settings/Horror Kompendium.json` + 5 Archetypen korrigiert, headless verifiziert:

- **Handicaps PDF-konform**: Engel −Auffällig; Dämon Böse/Geweihtes Wasser → **Schwäche (Kaltes Eisen)**
  (neues Handicap im Katalog angelegt); Mumie −Hässlich; Flickenmonster → **Phobie(schwer)+Verpeilt**
  (+Schwäche Feuer), erfundene Hässlich/Außenseiter/Schwerfällig/Schwäche(Elektrizität) entfernt;
  Wiedergänger −Hässlich. Phantom/Vampir/Werwolf unverändert (waren korrekt/plausibel).
- **Attribut-Boni nach PDF ergänzt** (Pips, 2=+1 Würfeltyp): Engel/Mumie/Flickenmonster/Vampir
  Stä+4 Kon+4; Dämon Kon+2 Wil+2; Phantom Wil+2; Wiedergänger Stä+2 Kon+2. Vampir
  `bewegungsweite_bonus` 2→0 (im PDF nicht belegt). Werwolf bewusst leer (Boni nur in Werwolfgestalt).
- **Flickenmonster auto_talente** Zäh/Kräftig → **Berserker/Arkane Resistenz** (PDF); Double-Counting
  der Str/Konst-Erhöhung über Edges beseitigt.
- **Archetypen angeglichen**: Angel, Demon (→Kaltes Eisen), Mummy (−Hässlich,−Schwerfällig),
  Patchwork_Man (−4 Handicaps, −Zäh/Kräftig), Revenant (−Hässlich). Archetyp-Attribute lagen
  bereits ≥ PDF-Floor → keine Attributänderung nötig.
- Verifiziert: frisches Volk-Wählen liefert korrekte auto_handicaps/auto_talente/Attribut-Floors;
  `test units/test_groesse.py` 16/16 grün.

#### OFFEN (nicht im Auftragsumfang „Handicaps/Attribute/Archetypen", bewusst belassen)
- **Dämon-Besonderheiten über-gewährt**: „Natürliche Waffen" + „Panzerung +2" sind im PDF TALENTE
  (Klauen/Biss/Panzerhaut), keine Basis; „Resistenz Feuer" statt PDF „Widerstand Kälte/Elektr./Hitze";
  „Furchteinflößend" nicht im PDF. (Kampfwerte-relevant → separate Entscheidung.)
- **Mumie/Wiedergänger/Vampir auto_talente** (Zäh/Nachtsicht): repräsentieren das UNTOT/Dunkelsicht-
  Paket, sind aber im PDF keine separaten Edges. Belassen, da Entfernen Archetyp-Punktebilanz berührt.
- **Werwolf** „Stumm/Kann nicht sprechen" (nur Wolfsform) nicht modelliert.
