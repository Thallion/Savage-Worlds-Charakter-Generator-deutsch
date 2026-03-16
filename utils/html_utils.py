"""
HTML-Hilfsfunktionen für den Charakterbogen-Generator
Plattformunabhängiger HTML-Export als Alternative zur PDF-Generierung
"""

import html
from kivy.logger import Logger


def generiere_html(charakter, output_html, printer_friendly=False):
    """
    Generiert den Charakterbogen als HTML-Datei.

    Args:
        charakter: Das Charakterobjekt mit allen Daten
        output_html: Pfad für die zu erstellende HTML-Datei
        printer_friendly: Bool, ob eine druckerfreundliche Version ohne Hintergrundfarben erstellt werden soll

    Returns:
        bool: True wenn erfolgreich, False bei Fehler
    """
    try:
        sections = []

        # Profil
        sections.append(_erzeuge_profil_sektion(charakter))

        # Attribute und Fertigkeiten (nebeneinander mit Volk und abgeleiteten Werten)
        sections.append(_erzeuge_attribute_fertigkeiten_sektion(charakter))

        # Handicaps
        sections.append(_erzeuge_handicaps_sektion(charakter))

        # Talente
        sections.append(_erzeuge_talente_sektion(charakter))

        # Mächte
        maechte_html = _erzeuge_maechte_sektion(charakter)
        if maechte_html:
            sections.append(maechte_html)

        # Superkräfte
        superkraefte_html = _erzeuge_superkraefte_sektion(charakter)
        if superkraefte_html:
            sections.append(superkraefte_html)

        # Allgemeine Ausrüstung
        sections.append(_erzeuge_allgemeine_ausruestung_sektion(charakter))

        # Waffen
        waffen_html = _erzeuge_waffen_sektion(charakter)
        if waffen_html:
            sections.append(waffen_html)

        # Rüstungen
        ruestungen_html = _erzeuge_ruestungen_sektion(charakter)
        if ruestungen_html:
            sections.append(ruestungen_html)

        # Schilde
        schilde_html = _erzeuge_schilde_sektion(charakter)
        if schilde_html:
            sections.append(schilde_html)

        # Steigerungs-Journal
        journal_html = _erzeuge_steigerungen_sektion(charakter)
        if journal_html:
            sections.append(journal_html)

        body_content = "\n".join(sections)

        char_name = html.escape(charakter.char_name) if charakter.char_name else "Charakterbogen"
        html_doc = _erzeuge_html_dokument(char_name, body_content, printer_friendly)

        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_doc)

        Logger.info(f"HTML-Charakterbogen wurde erfolgreich erstellt unter: {output_html}")
        return True

    except Exception as e:
        Logger.error(f"Fehler beim Erstellen des HTML-Charakterbogens: {e}")
        return False


def _esc(text):
    """Kurzform für html.escape mit String-Konvertierung"""
    return html.escape(str(text)) if text is not None else ""


def _create_mod_text(modifier):
    """Erstellt den Text für den Modifier."""
    if modifier != 0:
        return f"{modifier:+}"
    return ""


def _erzeuge_html_dokument(title, body_content, printer_friendly=False):
    """Erzeugt das vollständige HTML5-Dokument mit Inline-CSS"""
    if printer_friendly:
        header_bg = "#ffffff"
        row_bg = "#ffffff"
        body_bg = "#ffffff"
    else:
        header_bg = "#ffb961"  # Moccasin
        row_bg = "#FFE4B5"    # OldLace
        body_bg = "#FFF8DC"   # Cornsilk

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10pt;
    color: #000;
    background-color: {body_bg};
    margin: 10px;
    padding: 0;
}}
h1 {{
    font-size: 16pt;
    margin: 0 0 8px 0;
}}
h2 {{
    font-size: 12pt;
    margin: 12px 0 4px 0;
}}
table {{
    border-collapse: collapse;
    margin-bottom: 8px;
}}
th, td {{
    border: 1px solid #000;
    padding: 3px 6px;
    text-align: left;
    vertical-align: top;
}}
th {{
    background-color: {header_bg};
    font-weight: bold;
}}
td {{
    background-color: {row_bg};
}}
td.gesamt {{
    background-color: {header_bg};
    font-weight: bold;
}}
.two-column {{
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    align-items: flex-start;
}}
.two-column > div {{
    flex: 0 1 auto;
}}
.beschreibung {{
    font-style: normal;
    font-size: 9pt;
}}
@media print {{
    body {{
        background-color: #fff;
    }}
    th {{
        background-color: {header_bg if not printer_friendly else '#fff'};
    }}
    td {{
        background-color: {row_bg if not printer_friendly else '#fff'};
    }}
    td.gesamt {{
        background-color: {header_bg if not printer_friendly else '#fff'};
    }}
}}
@media (max-width: 600px) {{
    .two-column {{
        flex-direction: column;
    }}
    table {{
        width: 100%;
    }}
}}
</style>
</head>
<body>
<h1>Charakterbogen:</h1>
{body_content}
</body>
</html>"""


def _erzeuge_profil_sektion(charakter):
    """Erzeugt die Profil-Sektion"""
    profil_data = charakter.profil_daten
    rows = ""
    for key, value in profil_data.items():
        rows += f"<tr><td><b>{_esc(key)}</b></td><td>{_esc(value)}</td></tr>\n"

    return f"""<h2>Profil</h2>
<table>
<tr><th>Attribut</th><th>Beschreibung</th></tr>
{rows}</table>"""


def _erzeuge_attribute_fertigkeiten_sektion(charakter):
    """Erzeugt Attribute, Fertigkeiten, Volk und abgeleitete Werte in Zwei-Spalten-Layout"""

    # Linke Spalte: Attribute + Fertigkeiten
    # Attribute
    attr_rows = ""
    for attribut in charakter.attribute.values():
        wert_text = f"W{attribut.wert}"
        mod_text = _create_mod_text(attribut.modifier)
        combined = f"{wert_text} {mod_text}" if mod_text else wert_text
        attr_rows += f"<tr><td>{_esc(attribut.attribut_name)}</td><td>{_esc(combined)}</td></tr>\n"

    left_html = f"""<h2>Attribute</h2>
<table>
<tr><th>Attribut</th><th>Wert</th></tr>
{attr_rows}</table>"""

    # Fertigkeiten
    fert_rows = ""
    for fertigkeit in charakter.fertigkeiten.values():
        if fertigkeit.modifier == -2:
            continue
        if fertigkeit.modifier == 0 and fertigkeit.wert not in [4, 6, 8, 10, 12]:
            continue
        wert_text = f"W{fertigkeit.wert}"
        mod_text = _create_mod_text(fertigkeit.modifier)
        combined = f"{wert_text} {mod_text}" if mod_text else wert_text
        fert_rows += f"<tr><td>{_esc(fertigkeit.fertigkeit_name)}</td><td>{_esc(combined)}</td></tr>\n"

    left_html += f"""
<h2>Fertigkeiten</h2>
<table>
<tr><th>Fertigkeit</th><th>Wert</th></tr>
{fert_rows}</table>"""

    # Rechte Spalte: Volk + Abgeleitete Werte
    right_html = _erzeuge_volk_sektion(charakter)
    right_html += _erzeuge_abgeleitete_werte_sektion(charakter)

    return f"""<div class="two-column">
<div>{left_html}</div>
<div>{right_html}</div>
</div>"""


def _erzeuge_volk_sektion(charakter):
    """Erzeugt die Volk-Sektion"""
    selected_volk = None
    for volk, aktiv in charakter.voelker_selected.items():
        if aktiv:
            selected_volk = volk
            break

    if not selected_volk:
        return "<p>Kein Volk ausgewählt.</p>"

    volk_obj = charakter.voelker.get(selected_volk, None)
    result = f"<h2>Volk: {_esc(selected_volk)}</h2>"

    if not volk_obj:
        return result + "<p>Keine Daten für das ausgewählte Volk vorhanden.</p>"

    if volk_obj.talente:
        rows = "".join(f"<tr><td>{_esc(t)}</td></tr>\n" for t in volk_obj.talente)
        result += f"""<table>
<tr><th>Talent</th></tr>
{rows}</table>"""

    if volk_obj.handicaps:
        rows = "".join(f"<tr><td>{_esc(h)}</td></tr>\n" for h in volk_obj.handicaps)
        result += f"""<table>
<tr><th>Handicap</th></tr>
{rows}</table>"""

    if volk_obj.besonderheiten:
        rows = "".join(f"<tr><td>{_esc(b)}</td></tr>\n" for b in volk_obj.besonderheiten)
        result += f"""<table>
<tr><th>Besonderheit</th></tr>
{rows}</table>"""

    return result


def _erzeuge_abgeleitete_werte_sektion(charakter):
    """Erzeugt die abgeleiteten Werte Sektion"""
    abgeleitete_werte = {
        'Bewegungsweite': charakter.bewegungsweite,
        'Parade': charakter.parade,
        'Robustheit': charakter.robustheit_mit_ruestung,
        'Machtpunkte': charakter.machtpunkte,
        'Wunden': charakter.wunden,
        'Erschöpfung': charakter.erschoepfung,
        'Bennys': charakter.bennys,
        'Entschlossenheit': charakter.entschlossenheit,
        'Maximale Traglast': f"{charakter.gesamtgewicht} / {charakter.maximale_traglast} kg",
    }

    rows = ""
    for key, value in abgeleitete_werte.items():
        rows += f"<tr><td>{_esc(key)}</td><td>{_esc(value)}</td></tr>\n"

    # Cyberware-Stress für SciFi-Settings
    from functions.cyberware_funktionen import ist_cyberware_setting
    if ist_cyberware_setting(charakter.active_setting_name):
        stress_aktuell = charakter.cyberware_stress_aktuell
        stresslimit = charakter.cyberware_stresslimit
        stress_max = charakter.cyberware_stress_maximum
        rows += f"<tr><td>Cyberware Stress</td><td>{_esc(stress_aktuell)} / {_esc(stresslimit)} (Max: {_esc(stress_max)})</td></tr>\n"
        installationen = len(getattr(charakter, 'cyberware_installationen', {}))
        if installationen > 0:
            rows += f"<tr><td>Installationen</td><td>{_esc(installationen)}</td></tr>\n"

    return f"""<h2>Abgeleitete Werte</h2>
<table>
<tr><th>Beschreibung</th><th>Wert</th></tr>
{rows}</table>"""


def _erzeuge_handicaps_sektion(charakter):
    """Erzeugt die Handicaps-Sektion"""
    handicaps = charakter.selected_handicaps
    rows = ""
    for handicap_name_key in handicaps:
        handicap = charakter.handicaps.get(handicap_name_key)
        if handicap:
            rows += f"<tr><td>{_esc(handicap.name)}</td><td>{_esc(handicap.stufe)}</td></tr>\n"
            rows += f'<tr><td colspan="2" class="beschreibung">{_esc(handicap.beschreibung)}</td></tr>\n'

    return f"""<h2>Handicaps</h2>
<table>
<tr><th>Handicap</th><th>Stufe</th></tr>
{rows}</table>"""


def _erzeuge_talente_sektion(charakter):
    """Erzeugt die Talente-Sektion"""
    talente = charakter.selected_talente
    rows = ""
    for talent_name_key in talente:
        talent = charakter.talente.get(talent_name_key)
        if talent:
            rows += f"<tr><td>{_esc(talent.name)}</td><td>{_esc(talent.rang)}</td></tr>\n"
            rows += f'<tr><td colspan="2" class="beschreibung">{_esc(talent.beschreibung)}</td></tr>\n'

    return f"""<h2>Talente</h2>
<table>
<tr><th>Talent</th><th>Rang</th></tr>
{rows}</table>"""


def _erzeuge_maechte_sektion(charakter):
    """Erzeugt die Mächte-Sektion (nur wenn Mächte vorhanden)"""
    maechte = charakter.selected_maechte
    if not maechte:
        return None

    rows = ""
    for macht_name_key in maechte:
        macht = charakter.maechte.get(macht_name_key)
        if macht:
            rows += (f"<tr><td>{_esc(macht.name)}</td><td>{_esc(macht.rang)}</td>"
                     f"<td>{_esc(macht.machtpunkte)}</td><td>{_esc(macht.reichweite)}</td>"
                     f"<td>{_esc(macht.dauer)}</td></tr>\n")
            rows += f'<tr><td colspan="5" class="beschreibung">{_esc(macht.beschreibung)}</td></tr>\n'

    return f"""<h2>Mächte</h2>
<table>
<tr><th>Name</th><th>Rang</th><th>MP</th><th>Reichweite</th><th>Dauer</th></tr>
{rows}</table>"""


def _erzeuge_superkraefte_sektion(charakter):
    """Erzeugt die Superkräfte-Sektion (nur wenn Superkräfte vorhanden)"""
    superkraefte = charakter.selected_superkraefte
    if not superkraefte:
        return None

    machtstufe_info = _esc(f"Superkräfte (Machtstufe {charakter.machtstufe}, "
                           f"{charakter.superkraft_punkte_verbraucht}/{charakter.superkraft_punkte_gesamt} SKP)")

    rows = ""
    for kraft_name_key in superkraefte:
        kraft = charakter.superkraefte.get(kraft_name_key)
        if kraft:
            mod_text = ""
            if kraft.gewaehlte_modifikatoren:
                mod_names = [m.name for m in kraft.gewaehlte_modifikatoren]
                mod_text = ", ".join(mod_names)

            rows += (f"<tr><td>{_esc(kraft.name)}</td><td>{_esc(kraft.basis_kosten)}</td>"
                     f"<td>{_esc(kraft.gewaehlte_kosten)}</td><td>{_esc(mod_text)}</td>"
                     f"<td>{_esc(kraft.gesamt_kosten)}</td></tr>\n")
            rows += f'<tr><td colspan="5" class="beschreibung">{_esc(kraft.beschreibung)}</td></tr>\n'

    return f"""<h2>{machtstufe_info}</h2>
<table>
<tr><th>Name</th><th>Basis</th><th>SKP</th><th>Modifikatoren</th><th>Gesamt</th></tr>
{rows}</table>"""


def _erzeuge_allgemeine_ausruestung_sektion(charakter):
    """Erzeugt die allgemeine Ausrüstung Sektion"""
    items = [item for name, item in charakter.ausruestung.items()
             if item in charakter.selected_allgemeine_ausruestung and item.ausgewaehlt]

    rows = ""
    for item in items:
        menge = getattr(item, 'menge', 1)
        beschreibung = getattr(item, 'beschreibung', '-')
        rows += f"<tr><td>{_esc(item.name)}</td><td>{_esc(menge)}</td><td>{_esc(beschreibung)}</td></tr>\n"

    return f"""<h2>Allgemeine Ausrüstung</h2>
<table>
<tr><th>Name</th><th>Menge</th><th>Beschreibung</th></tr>
{rows}</table>"""


def _erzeuge_waffen_sektion(charakter):
    """Erzeugt die Waffen-Sektion (nur wenn Waffen angelegt)"""
    waffen = [w for w in charakter.selected_waffen if w.angelegt]
    if not waffen:
        return None

    rows = ""
    for waffe in waffen:
        eigenschaften = waffe.eigenschaften
        rows += (f"<tr><td>{_esc(waffe.name)}</td>"
                 f"<td>{_esc(eigenschaften.get('Schaden', '-'))}</td>"
                 f"<td>{_esc(eigenschaften.get('Reichweite', '-'))}</td>"
                 f"<td>{_esc(eigenschaften.get('FR', '-'))}</td>"
                 f"<td>{_esc(eigenschaften.get('Schuss', '-'))}</td>"
                 f"<td>{_esc(eigenschaften.get('PB', '-'))}</td></tr>\n")

    return f"""<h2>Waffen</h2>
<table>
<tr><th>Name</th><th>Schaden</th><th>Reichweite</th><th>FR</th><th>Schuss</th><th>PB</th></tr>
{rows}</table>"""


def _erzeuge_ruestungen_sektion(charakter):
    """Erzeugt die Rüstungen-Sektion (nur wenn Rüstungen angelegt)"""
    ruestungen = [r for r in charakter.selected_ruestungen if r.angelegt]
    if not ruestungen:
        return None

    rows = ""
    for ruestung in ruestungen:
        rows += (f"<tr><td>{_esc(ruestung.name)}</td>"
                 f"<td>{_esc(ruestung.torso)}</td>"
                 f"<td>{_esc(ruestung.arme)}</td>"
                 f"<td>{_esc(ruestung.beine)}</td>"
                 f"<td>{_esc(ruestung.kopf)}</td></tr>\n")

    # Gesamten Rüstungsschutz
    gesamt = charakter.berechne_gesamt_ruestungsschutz()
    rows += (f'<tr><td class="gesamt">Gesamt</td>'
             f'<td class="gesamt">{_esc(gesamt["Torso"])}</td>'
             f'<td class="gesamt">{_esc(gesamt["Arme"])}</td>'
             f'<td class="gesamt">{_esc(gesamt["Beine"])}</td>'
             f'<td class="gesamt">{_esc(gesamt["Kopf"])}</td></tr>\n')

    return f"""<h2>Rüstungen</h2>
<table>
<tr><th>Name</th><th>Torso</th><th>Arme</th><th>Beine</th><th>Kopf</th></tr>
{rows}</table>"""


def _erzeuge_schilde_sektion(charakter):
    """Erzeugt die Schilde-Sektion (nur wenn Schilde angelegt)"""
    schilde_items = [
        s for name, s in charakter.ausruestung.items()
        if s in charakter.selected_schilde and s.angelegt
    ]
    if not schilde_items:
        return None

    rows = ""
    for schild in schilde_items:
        parade = getattr(schild, 'parade', '-')
        deckung = getattr(schild, 'deckung', '-')
        mindeststaerke = getattr(schild, 'mindeststaerke', '-')
        rows += (f"<tr><td>{_esc(schild.name)}</td>"
                 f"<td>{_esc(parade)}</td>"
                 f"<td>{_esc(deckung)}</td>"
                 f"<td>{_esc(mindeststaerke)}</td></tr>\n")

    return f"""<h2>Schilde</h2>
<table>
<tr><th>Name</th><th>Parade</th><th>Deckung</th><th>Mindeststärke</th></tr>
{rows}</table>"""


def _erzeuge_steigerungen_sektion(charakter):
    """Erzeugt die Steigerungs-Journal Sektion"""
    journal = getattr(charakter, 'steigerungs_journal', None)
    if not journal or not isinstance(journal, dict) or not journal.get('entries'):
        return None

    journal_entries = journal['entries']
    steigerungs_typen = {
        'attribut_steigerung': 'Attribut',
        'fertigkeit_steigerung': 'Fertigkeit',
        'talent_hinzugefuegt': 'Talent',
        'talent_entfernt': 'Talent',
        'handicap_hinzugefuegt': 'Handicap',
        'handicap_entfernt': 'Handicap',
        'handicap_reduziert': 'Handicap',
        'macht_hinzugefuegt': 'Macht',
        'macht_entfernt': 'Macht',
    }
    relevante_eintraege = [e for e in journal_entries if e.get('type') in steigerungs_typen]

    if not relevante_eintraege:
        return None

    rows = ""
    for entry in relevante_eintraege:
        rang = entry.get('rang', '')
        details = entry.get('details', {})
        entry_type = entry.get('type', '')
        typ = steigerungs_typen.get(entry_type, '')
        name = details.get('name', '')

        # Name mit Kontext anreichern
        if entry_type in ('attribut_steigerung', 'fertigkeit_steigerung'):
            von = details.get('von', '')
            nach = details.get('nach', '')
            name = f"{name}: W{von} → W{nach}"
        elif entry_type == 'talent_entfernt':
            name = f"{name} (entfernt)"
        elif entry_type == 'handicap_entfernt':
            name = f"{name} (entfernt)"
        elif entry_type == 'handicap_reduziert':
            name = f"{name} (reduziert)"
        elif entry_type == 'macht_entfernt':
            name = f"{name} (entfernt)"

        # Kosten-Text
        kosten = details.get('kosten', details.get('punkte', ''))
        kosten_typ = details.get('kosten_typ', '')
        if kosten != '' and kosten_typ:
            kosten_text = f"{kosten} {kosten_typ}"
        elif kosten != '':
            kosten_text = str(kosten)
        else:
            kosten_text = ''

        rows += (f"<tr><td>{_esc(rang)}</td><td>{_esc(typ)}</td>"
                 f"<td>{_esc(name)}</td><td>{_esc(kosten_text)}</td></tr>\n")

    return f"""<h2>Steigerungen</h2>
<table>
<tr><th>Rang</th><th>Typ</th><th>Name</th><th>Kosten</th></tr>
{rows}</table>"""
