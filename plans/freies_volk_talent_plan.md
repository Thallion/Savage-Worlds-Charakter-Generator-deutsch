❯ /plan                                                                                                                                                                                                                             
  ⎿  Current Plan                                                                                                                                                                                                                 
     /home/jean/.claude/plans/v-lker-view-mensch-goofy-elephant.md                                                                                                                                                                  
                                                                                                                                                                                                                                  
     Plan: Freies Talent im Völker-View (Mensch / Halbelf / Volkseigenarten)                                                                                                                                                        
                                                                                                                                                                                                                                
     Kontext                                                                                                                                                                                                                        
                                                                                                                                                                       
     Wenn der User ein Volk mit freiem Anfängertalent wählt (z. B. Mensch "Vielseitig", Halbelf-Erbe, oder ein Volk mit freies_talent-Zusatzelement), läuft die Auswahl aktuell über                                                
     views/voelker_auswahl_overlay.py::_show_talent_selection und anschließend über functions/volk_funktionen.py::waehle_freies_talent / waehle_mensch_talent. Dabei gibt es drei Probleme:

     1. AH-Talente aktivieren weder Mächte noch Machtpunkte. volk_funktionen.waehle_freies_talent setzt nur talent.ausgewaehlt = True und fügt den Namen in selected_talente ein. Die Aktivierungslogik aus
     talent_funktionen.TalentManager.talent_auswaehlen (erhöht verfuegbare_maechte, anzahl_maechte, ruft erhoehe_machtpunkte(talent.machtpunkte) sowie _apply_ah_auto_effects auf, das Auto-Handicaps und Auto-Talente setzt) wird
     nie ausgeführt. → Ein als freies Menschen-Talent gewähltes "Arkaner Hintergrund: Magie" bekommt 0 Mächte, 0 Machtpunkte, keine auto-Handicaps.
     2. Kein "Alle Talente"-Button. get_freie_talente(charakter) wird ohne zweites Argument aufgerufen → Voreinstellung nur_verfuegbare=True → Talente mit nicht erfüllten Voraussetzungen oder zu hohem Rang werden gefiltert und
     im Overlay nicht angezeigt. Die Haupt-Talente-Ansicht (views/talente_view.py, Property only_available_talents mit Toggle via toggle_only_available_talents) kann dagegen per Button umgeschaltet werden.
     3. "Trotzdem auswählen" fehlt. Die Haupt-Talente-Ansicht zeigt bei Voraussetzungs-Fehlern einen Bestätigungsdialog (_show_voraussetzungen_confirmation_dialog in views/talente_view.py:511) und erlaubt per Button "Trotzdem
     auswählen" die Auswahl. Das freie Volks-Talent-Popup hat diesen Fallback nicht.
     4. Das freie Talent kann nach der Auswahl nicht geändert werden. voelker_view.py::_update_zusatzelemente (ab Zeile 581) zeigt das gewählte Talent nur als MDChip an, ohne Bearbeiten-Möglichkeit.

     Ziel: Das Volk-Talent-Popup soll sich wie die reguläre Talente-Ansicht verhalten (Filter-Toggle + Voraussetzungs-Bestätigungsdialog), AH-Talente sollen korrekt das Macht-System aktivieren, und die Auswahl soll im
     Völker-View jederzeit änderbar sein.

     Betroffene Dateien

     - functions/volk_funktionen.py — Kernlogik waehle_freies_talent (Zeilen 478–549), waehle_mensch_talent (1478), waehle_halbelf_talent. Plus neue Variante mit ignore_voraussetzungen-Parameter.
     - views/voelker_auswahl_overlay.py — _show_talent_selection (517–669) bekommt Filter-Toggle-Button und Voraussetzungs-Bestätigungsdialog; _on_talent_chosen (698) und _apply_choice leiten ignore_voraussetzungen-Flag durch.
     - views/voelker_view.py — _on_overlay_volk_chosen (129–188) reicht das Flag an die waehle_*-Funktionen durch; _update_zusatzelemente (581–642) bekommt Edit-Icons neben den Chips, die die Auswahl erneut öffnen.
     - views/volk_popup.py — _show_talent_optionen_dialog (690–776, Volkseigenarten mit optionen.typ == 'freies_talent') bekommt dieselben zwei Ergänzungen (Filter-Toggle + "Trotzdem auswählen"-Dialog), damit das Muster
     konsistent bleibt.

     Wiederverwendete Funktionen / Muster

     - talent_funktionen.talent_auswaehlen(charakter, name, skip_prereq_check=...) (Modul-Wrapper in functions/talent_funktionen.py:1340, Manager-Methode in Zeile 350): führt die komplette Auswahl inkl.
     verfuegbare_maechte-/machtpunkte-/_apply_ah_auto_effects-Logik aus. Das ist der richtige Einstieg, um das freie Talent regulär zu setzen statt manuell talent.ausgewaehlt = True.
     - talent_funktionen.pruefe_voraussetzungen(charakter, talent) (Wrapper Zeile 1344) und is_talent_rang_hoeher_als_charakter — für den Toggle + das Konditional, wann der Bestätigungsdialog angezeigt wird.
     - get_freie_talente(charakter, nur_verfuegbare=False) (Zeile 355 in volk_funktionen.py) — der Parameter existiert bereits, wird aber von voelker_auswahl_overlay.py nie durchgereicht.
     - Bestätigungsdialog-Muster aus views/talente_view.py::_show_voraussetzungen_confirmation_dialog (Zeilen 511–591): Fehlermeldungen werden einzeln in MDLabel mit theme_text_color="Error" gerendert, zwei Buttons ("Abbrechen"
     / "Trotzdem auswählen"). Dieses Dialog-Layout 1:1 übernehmen.
     - Filter-Toggle-Muster aus views/voelker_view.py::_show_search_dialog (ab Zeile 890, filter_state = {'nur_verfuegbare': True}, Icon wechselt zwischen filter/filter-off, style zwischen tonal/outlined): sauberes Vorbild für
     das Overlay-Popup.
     - Edit-Chip-Muster aus _create_zusatzelement_section (voelker_view.py:707): MDIconButton(icon="pencil", ...) neben dem Chip, expandable_box für Aufklapp-Verhalten.

     Umsetzung

     1. functions/volk_funktionen.py — AH-Aktivierung + ignore_voraussetzungen-Parameter

     - waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False):
       - Signatur um ignore_voraussetzungen=False erweitern.
       - Vor dem manuellen talent.ausgewaehlt = True (Zeile 536) ersetzen/ergänzen durch einen Aufruf an talent_funktionen.talent_auswaehlen(charakter, talent_name, skip_prereq_check=ignore_voraussetzungen). Bei Erfolg übernimmt
      dieser die komplette Logik (Mächte, Machtpunkte, Auto-Handicaps, Auto-Talente, berechne_abgeleitete_werte).
       - Vorher weiterhin das Menschen-Tracking über _get_menschen_freies_talent / _set_menschen_freies_talent (Zeilen 513–533) durchführen und beim Wechsel das alte Talent regulär abwählen via talent_funktionen.talent_abwaehlen
      (statt nur ausgewaehlt = False), damit dort auch AH-Effekte / Mächte / Machtpunkte zurückgerollt werden.
       - Wenn ignore_voraussetzungen=False und die Voraussetzungen nicht erfüllt sind (Prüfung über pruefe_voraussetzungen + is_talent_rang_hoeher_als_charakter), einen klaren Rückgabewert liefern
     ("needs_voraussetzungen_confirmation"), damit der View den Bestätigungsdialog anstoßen kann. Die Fehlermeldungen temporär an charakter.temp_voraussetzungs_fehler hängen (gleiche Konvention wie in talente_view.py:518).
     - waehle_mensch_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False) (Zeile 1478): neuen Parameter akzeptieren und an waehle_freies_talent durchreichen.
     - waehle_halbelf_talent analog (falls vorhanden).

     2. views/voelker_auswahl_overlay.py::_show_talent_selection

     - Zusätzlicher Zustand self._filter_nur_verfuegbar = True.
     - Neben dem Headline einen MDIconButton(icon="filter") platzieren (analog voelker_view.py:937). Initial Icon filter / Stil tonal; nach Toggle Icon filter-off / Stil outlined.
     - populate_talents: Liste über get_freie_talente(self._charakter, nur_verfuegbare=self._filter_nur_verfuegbar) neu ziehen. Talente, deren Voraussetzungen nicht erfüllt sind, zusätzlich optisch markieren (MDLabel-Farbe
     theme_text_color="Error" oder ein kleines Warndreieck-Icon alert-circle-outline in der Row), damit der User bei "alle zeigen" sieht, welche nicht erfüllbar sind — wie in talente_view.py implizit über die
     Voraussetzungs-Spalte.
     - on_confirm → _on_talent_chosen(talent_typ, selected_talent[0]) leitet wie bisher weiter; kein Precheck im Overlay, das macht volk_funktionen.

     3. views/voelker_view.py::_on_overlay_volk_chosen

     - Für mensch_talent / freies_talent / halbelf_talent: Rückgabewert von waehle_mensch_talent / waehle_freies_talent auswerten. Wenn "needs_voraussetzungen_confirmation":
       - Bestätigungsdialog analog talente_view.py::_show_voraussetzungen_confirmation_dialog (Zeilen 511–591) öffnen. Fehler aus charakter.temp_voraussetzungs_fehler laden.
       - Button "Trotzdem auswählen" ruft waehle_mensch_talent(..., ignore_voraussetzungen=True) erneut auf, anschließend wie gewohnt _update_zusatzelemente / _update_selected_volk_details.
       - "Abbrechen" → Dialog schließen, voelker_auswahlen nicht aktualisieren.

     4. views/voelker_view.py::_update_zusatzelemente — Edit-Möglichkeit

     - Für jede Selection-Zeile in der Chip-Darstellung (Zeilen 623–642) zusätzlich ein MDIconButton(icon="pencil", size=(dp(36), dp(36))) rechts neben den Chip hängen. on_release:
       - Für 'Freies Talent' / 'Vielseitig Wahl': Overlay erneut über self._voelker_overlay.open(...) öffnen, dabei current_volk=self.selected_volk_name durchreichen. Das Overlay erkennt bei gleichem Volk (Zeile 341) und
     überspringt die Phase-1-Neuwahl, springt aber via _selected_volk = volk_name + _build_extras_phase direkt in Phase 2 — dafür eine kleine Erweiterung: neuer Einstiegspunkt open_extras_only(volk_name, charakter, auswahl_typ)
     der direkt _phase = "extras" und _build_menschen_section() / _build_halbelf_section() / _build_generic_extras_section() ruft.
       - Alternativ (einfacher, bevorzugt): direkt self._voelker_overlay._show_talent_selection(<talent_typ>) aufrufen, wenn das Overlay initialisierbar ist. _selected_volk und _charakter vorher setzen.

     5. views/volk_popup.py::_show_talent_optionen_dialog (Zeilen 690–776)

     - Analog zu Punkt 2: Filter-Button neben der Listenüberschrift, Listeninhalt aus get_freie_talente(charakter, nur_verfuegbare=self._popup_nur_verfuegbar).
     - Analog zu Punkt 3: Beim _on_confirm die neue Rückgabe "needs_voraussetzungen_confirmation" verarbeiten und Bestätigungsdialog zeigen.

     Verifikation

     1. Unit-Tests: python "test units/run_all_tests.py" — sollte weiterhin grün bleiben. Neue Tests (optional, aber empfohlen) in test units/test_setting_funktionen.py oder neuer Datei test_volk_freies_talent.py:
       - Szenario: Charakter mit Mensch-Volk, waehle_mensch_talent(charakter, 'Mensch', 'Arkaner Hintergrund: Magie'). Nach Ausführung: charakter.verfuegbare_maechte == 3, charakter.machtpunkte == 10 (oder was das Talent in
     talent_config.json definiert), charakter.selected_handicaps enthält Auto-Handicaps des AH.
       - Szenario: Talent mit unerfüllter Voraussetzung → waehle_freies_talent(..., ignore_voraussetzungen=False) gibt "needs_voraussetzungen_confirmation" zurück, talent.ausgewaehlt bleibt False.
       - Szenario: ignore_voraussetzungen=True → Talent wird trotz fehlender Voraussetzung korrekt ausgewählt inkl. AH-Aktivierung.
       - Szenario: Wechsel des freien Menschen-Talents: erstes Talent (AH: Magie) setzen, dann zweites (AH: Wunder) setzen. Danach verfuegbare_maechte / machtpunkte entsprechen AH: Wunder, nicht akkumuliert.
     2. Manueller Test in der App (python main.py):
       - Neuen Charakter anlegen, Volk "Mensch" wählen. Bei Vielseitig-Auswahl "Freies Talent" wählen.
       - Im Overlay: Filter-Button klicken → Talente mit nicht erfüllten Voraussetzungen erscheinen (z. B. "Duellant" ohne ausreichenden Kampf-Skill). Bestätigen.
       - Bestätigungsdialog "Voraussetzungen nicht erfüllt" erscheint mit passender Fehlermeldung. "Trotzdem auswählen" wählen → Talent ist gesetzt.
       - Stattdessen "Arkaner Hintergrund: Magie" wählen → im Charakterbogen / Mächte-Tab erscheinen Machtpunkte > 0 und verfügbare Mächte > 0, Auto-Handicap (z. B. "Verpflichtet (klein)") ist gesetzt.
       - Im Völker-Tab neben der Chip-Anzeige des freien Talents auf das Stift-Icon klicken → Overlay öffnet sich erneut, anderes Talent wählen → alte AH-Effekte werden zurückgerollt, neue aktiviert.
     3. Android-Smoke-Test: Checkbox-/Debounce-Muster aus CLAUDE.md beachten — der Filter-Button im Overlay ist ein MDIconButton mit on_release, daher Debounce-Pattern wie in den anderen Dialogen anwenden (500 ms Guard).