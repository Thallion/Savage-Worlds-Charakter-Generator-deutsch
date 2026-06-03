# Abgleich: DSA-Regelwiki „Nachteile" ↔ Savage Aventurien Handicaps

**Stand:** 2026-06-03
**Quelle:** https://dsa.ulisses-regelwiki.de/nachteilauswahl.html (81 Nachteile)
**Implementierung:** `scripts/dsa_add_nachteile_wiki.py` (idempotent)
**Backup:** `backup/settings/Savage Aventurien_vor_nachteile_wiki_20260603.json`

**Vorgehen:** Inhaltlicher (nicht nur titelbasierter) Abgleich aller 81 Wiki-Nachteile
gegen die 124 bestehenden Handicap-Namen. Ergänzt wurden nur Nachteile **ohne**
SW-Äquivalent, die sich **sinnvoll nach Savage Worlds übersetzen** lassen.

---

## 1. NEU ergänzt (8)

| Handicap | Stufe | DSA-Vorlage | Begründung |
|----------|:-----:|-------------|------------|
| Hitzeempfindlich | leicht | Hitzeempfindlich I-II | distinkt zu `Brandempfindlich` (= Konzentration bei Flammen); stützt Volk Achaz/Wüste |
| Kälteempfindlich | leicht | Kälteempfindlich, Kältestarre | kein Pendant; stützt Volk Achaz |
| Farbenblind | leicht | Farbenblind | kein Pendant |
| Schlafwandler | leicht | Schlafwandler | kein Pendant (`Schlafmütze` = mehr Schlafbedarf) |
| Giftanfällig | leicht | Giftanfällig I-II | `Kränklich` ist breit (Krankheit/Umwelt), nicht gift-spezifisch |
| Unverträglichkeit gegenüber Alkohol | leicht | Unverträglichkeit gegenüber Alkohol | kein Pendant |
| Strenger Körpergeruch | leicht | Stechender Orkgeruch, Raubtiergeruch, Jagdwildgeruch | **konsolidiert** 3 DSA-Volksgerüche |
| Empfindlichkeit gegen Eisen | leicht | Empfindlichkeit (unedle Metalle) | Fey/Elfen-Schwäche; Gegenstück zum Talent `Eisenaffine Aura` |

---

## 2. Bereits abgedeckt (SW-Äquivalent vorhanden)

| DSA-Nachteil | SW-Handicap im Setting |
|--------------|------------------------|
| Angst vor … I-III | `Phobie` |
| Arm I-III | `Arm` |
| Artefaktgebunden | `Artefaktgebunden` (Wildes Aventurien) |
| Behäbig | `Langsam` |
| Blind | `Blind` |
| Blutrausch | `Blutrünstig` |
| Eingeschränkter Sinn | `Schwerhörig` / `Kurzsichtig` / `Schlechte Augen` |
| Fettleibig | `Fettleibig` |
| Friedlos | `Gesucht` / `Außenseiter` |
| Gläsern | `Zerbrechlich` (−1 Robustheit) |
| Hässlich I-II | `Hässlich` |
| Instabiler Zauberer | `Magischer Tollpatsch` |
| Körperliche Auffälligkeit | `Stigma` / `Hässlich` |
| Krankheitsanfällig I-II | `Kränklich` |
| Lästige Mindergeister | `Lästige Mindergeister` (Wildes Aventurien) |
| Lichtempfindlich I-II | `Lichtempfindlich` |
| Nachtblind | `Gewöhnliche Sicht` (verlorene Dämmersicht) |
| Niedrige Lebenskraft I-VII | `Verringerte Vitalität` / `Größe -1` |
| Niedrige Seelenkraft | `Selbstzweifel` (−1 Willenskraft) |
| Niedrige Zähigkeit | `Verringerte Vitalität` (−1 Robustheit) |
| Pech I-III / Pechmagnet | `Pech` |
| Persönlichkeitsschwäche | diverse (Tick, Zwanghaft, Angewohnheit) |
| Prinzipientreue I-III | `Ehrenkodex` / `Schwur` / `Pazifist` |
| Schlechte Angewohnheit | `Angewohnheit` |
| Schlechte Eigenschaft | `Tick` / `Zwanghaft` / `Angewohnheit` |
| Schlechtes Namensgedächtnis | `Vergesslich` |
| Sprachfehler | `Schwerzüngig` |
| Stigma | `Stigma` (Wildes Aventurien) |
| Stumm | `Stumm` |
| Taub | `Schwerhörig` (−4 Wahrnehmung Geräusche) |
| Unfrei | `Verpflichtung` / `Loyal` |
| Verpflichtungen I-III | `Verpflichtung` |
| Verstümmelt | `Einarmig` / `Einäugig` / `Hilflos` |
| Wilde Magie | `Magischer Tollpatsch` |
| Zauberanfällig I-II | `Arkane Empfindlichkeit` |
| Zerbrechlich | `Zerbrechlich` |

---

## 3. Bewusst NICHT übernommen — DSA-Ressourcen-Mechanik ohne SW-Pendant

In Savage Worlds gibt es keine getrennten Pools für Astral-/Karmalenergie, keine
AsP/KaP-Regeneration und keine DSA-Sonderfertigkeits-Stufen. Diese Nachteile haben
daher kein sinnvolles Gegenstück und werden weggelassen:

- Niedrige Astralkraft I-VII, Niedrige Karmalkraft I-VII
- Schwacher Astralkörper, Schwacher Karmalkörper
- Schlechte Regeneration (Astral-/Karma-/Lebensenergie) I-III
- Limbus-Medium I-II
- Wenige Predigten I-II, Wenige Visionen I-II
- Schwache/Verminderte Zaubermelodien I-III, Schwache/Verminderte Zaubertänze I-III
- Körpergebundene Kraft, Magische Einschränkung
- Kleine Zauberauswahl I-III (≈ `Novize/Eleve`)
- Misslungene Reifeprüfung (≈ `Novize/Eleve`)
- Wahrer Name, Kein Vertrauter, Keine Flugsalbe (DSA-Spezialmechaniken)
- Yurach (spezifische Sucht), Lästige Blütenfeen (≈ `Lästige Mindergeister`)

---

## 4. Bewusst NICHT übernommen — zu generisch / redundant / reine Namens-Mechanik

| DSA-Nachteil | Grund |
|--------------|-------|
| Böser Namensvetter, Lächerlicher Name, Schurkenname, Unpassender Name | DSA-Namens-Mechanik; sozial bereits via `Gesucht`/`Beschämt`/`Außenseiter` abbildbar |
| Unfähig, Lernfaul, Verweichlicht | zu generisch |
| Sensibler Geruchssinn | sehr klein, inverse zu `Strenger Körpergeruch` |
| Empfindlichkeit (unedle Metalle) → **doch übernommen** als `Empfindlichkeit gegen Eisen` | siehe Abschnitt 1 |

---

## 5. Validierung

- [x] JSON valide & lädt
- [x] Semantischer Diff gegen Backup: 0 alte Handicaps verloren/verändert
- [x] Talente & Mächte unverändert
- [x] Neue Einträge schema-identisch (`name`, `stufe`, `punkte`, `beschreibung`, `ausgewaehlt`, `aktiv`, `custom`)
- [ ] In-App-Test (offen, Phase 11)
- [ ] Volk-Verknüpfung: `Kälteempfindlich`/`Strenger Körpergeruch`/`Hitzeempfindlich` bei Achaz/Ork/Waldmensch hinterlegen (offen, Phase 4)
