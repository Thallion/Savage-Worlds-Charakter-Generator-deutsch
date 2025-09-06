"""
PDF-Hilfsfunktionen für den Charakterbogen-Generator
Unterstützt plattformspezifische PDF-Generierung (Desktop only)
"""

import os
import sys
from pathlib import Path
from kivy.logger import Logger

# Import path utilities
from utils.path_utils import get_assets_path, get_application_root as get_app_root

# Platform detection
def is_android():
    """Prüft ob die App auf Android läuft"""
    try:
        from jnius import autoclass
        return True
    except ImportError:
        return False

def is_desktop():
    """Prüft ob die App auf Desktop (Windows/Linux/macOS) läuft"""
    return not is_android()

# Conditional reportlab imports - nur auf Desktop
REPORTLAB_AVAILABLE = False
if is_desktop():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            KeepTogether,
            Paragraph,
            Table,
            TableStyle,
            Spacer,
            SimpleDocTemplate,
            PageBreak,
            ListFlowable,
            ListItem,
        )
        from reportlab.lib import colors
        from PIL import Image
        
        REPORTLAB_AVAILABLE = True
        Logger.info("PDF-Utils: Reportlab erfolgreich geladen (Desktop-Modus)")
        
    except ImportError as e:
        Logger.warning(f"PDF-Utils: Reportlab nicht verfügbar auf Desktop: {e}")
        REPORTLAB_AVAILABLE = False
else:
    Logger.info("PDF-Utils: Android-Modus erkannt - PDF-Funktionalität deaktiviert")

# Removed - using centralized path utilities instead

def generiere_pdf(charakter, output_pdf, printer_friendly=False):
    """
    Generiert das Charakterbogen-PDF und speichert es unter dem angegebenen Pfad.
    
    Args:
        charakter: Das Charakterobjekt mit allen Daten
        output_pdf: Pfad für die zu erstellende PDF-Datei
        printer_friendly: Bool, ob eine druckerfreundliche Version ohne Hintergrund erstellt werden soll
    
    Returns:
        bool: True wenn erfolgreich, False wenn PDF-Generierung nicht verfügbar
    
    Raises:
        RuntimeError: Wenn PDF-Generierung auf aktueller Plattform nicht unterstützt wird
    """
    # Prüfe ob PDF-Generierung verfügbar ist
    if not REPORTLAB_AVAILABLE:
        error_msg = "PDF-Generierung ist auf dieser Plattform nicht verfügbar"
        if is_android():
            error_msg += " (Android wird nicht unterstützt)"
        Logger.error(error_msg)
        raise RuntimeError(error_msg)
    # Verwende die neue path_utils Funktion für PyInstaller-kompatible Pfade
    background_img = get_assets_path("charbogen_hintergrund.jpg")

    # Dokument erstellen mit konsistenten Seitenrändern
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        topMargin=10,      # Oberer Rand auf 10 Punkte setzen
        bottomMargin=10,   # Unterer Rand auf 10 Punkte setzen
        leftMargin=25,     # Linker Rand auf 10 Punkte setzen
        rightMargin=25     # Rechter Rand auf 10 Punkte setzen
    )

    elements = []

    # Hintergrundbild-Funktion definieren
    def add_background(canvas_obj, doc_obj):
        if not printer_friendly:
            canvas_obj.drawImage(background_img, 0, 0, width=A4[0], height=A4[1])

    # Styles definieren
    styles = getSampleStyleSheet()

    # Individuelle Anpassungen der Stile
    style_normal = styles['Normal']
    style_heading = styles['Heading2']
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        leading=12,
        spaceBefore=0,
        spaceAfter=12
    )

    # Farbdefinitionen, abhängig von printer_friendly
    if not printer_friendly:
        moccasin = colors.HexColor('#ffb961')  # Moccasin für die Kopfzeile
        oldlace = colors.HexColor('#FFE4B5')   # OldLace für die restlichen Zeilen
    else:
        moccasin = colors.white
        oldlace = colors.white

    # Einheitliche Stilbefehle definieren als separate Liste
    tabellen_style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), moccasin),          # Kopfzeile
        ('BACKGROUND', (0, 1), (-1, -1), oldlace),          # Zeilen
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),   # Kopfzeile fett
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    # Erstellen eines Basis TableStyle
    tabellen_style = TableStyle(tabellen_style_commands)

    # Überschrift mit angepasstem Stil
    elements.append(Paragraph("Charakterbogen:", style_title))
    elements.append(Spacer(1, 6))  # 6 Punkte Abstand

    # Maximale Größen für Elemente definieren
    max_width = 450  # Maximalbreite in Punkten
    max_height = 750  # Maximalhöhe in Punkten

    # Funktion zum sicheren Hinzufügen von Elementen
    def add_element_safely(element):
        if isinstance(element, KeepTogether):
            # Vermeide das direkte Aufrufen von wrap auf KeepTogether
            # Stattdessen logge eine Warnung und füge die Inhalte einzeln hinzu
            # Logger.warning("KeepTogether innerhalb von add_element_safely wird nicht unterstützt.")
            for item in element._content:
                add_element_safely(item)
        else:
            elements.append(element)

    # **Profildaten Abschnitt**
    profil_section = []
    profil_section.append(Paragraph("Profil", style_heading))
    profil_data = charakter.profil_daten
    profil_table_data = [["Attribut", "Beschreibung"]]
    for key, value in profil_data.items():
        profil_table_data.append([key, value])

    # Anpassung der colWidths auf 275 Punkte
    profil_table = Table(profil_table_data, colWidths=[60, 225], hAlign='LEFT')  # Summe = 275
    profil_table.setStyle(tabellen_style)
    profil_section.append(profil_table)
    profil_section.append(Spacer(1, 6))
    elements.append(KeepTogether(profil_section))

    # **Kombination von Attribute, Fertigkeiten und Abgeleitete Werte**
    combined_section = []

    # **Linke Spalte: Attribute und Fertigkeiten**
    left_column_content = []

    # **Attribut-Tabelle mit Überschrift**
    attribute_header = Paragraph("Attribute", style_heading)
    attribute_data = [["Attribut", "Wert"]]
    for attribut in charakter.attribute.values():
        wert_text = f"W{attribut.wert}"
        mod_text = create_mod_text(attribut.modifier)
        combined_text = f"{wert_text} {mod_text}" if mod_text else wert_text
        attribute_data.append([attribut.attribut_name, combined_text])

    attribute_table = Table(attribute_data, colWidths=[100, 50], hAlign='LEFT')
    attribute_table.setStyle(tabellen_style)
    left_column_content.append(attribute_header)
    left_column_content.append(attribute_table)
    left_column_content.append(Spacer(1, 6))  # 6 Punkte Abstand

    # **Fertigkeiten-Tabelle mit Überschrift**
    fertigkeiten_header = Paragraph("Fertigkeiten", style_heading)
    fertigkeiten_data = [["Fertigkeit", "Wert"]]
    for fertigkeit in charakter.fertigkeiten.values():
        if fertigkeit.modifier == -2:
            continue
        if fertigkeit.modifier == 0 and fertigkeit.wert not in [4, 6, 8, 10, 12]:
            continue
        wert_text = f"W{fertigkeit.wert}"
        mod_text = create_mod_text(fertigkeit.modifier)
        combined_text = f"{wert_text} {mod_text}" if mod_text else wert_text
        fertigkeiten_data.append([fertigkeit.fertigkeit_name, combined_text])

    fertigkeiten_table = Table(fertigkeiten_data, colWidths=[100, 50], hAlign='LEFT')
    fertigkeiten_table.setStyle(tabellen_style)
    left_column_content.append(fertigkeiten_header)
    left_column_content.append(fertigkeiten_table)
    left_column_content.append(Spacer(1, 6))  # 6 Punkte Abstand

    # **Rechte Spalte: Abgeleitete Werte / Volk**
    right_column_content = []

    # **Volk Abschnitt**
    volk_section = []

    # Ausgewähltes Volk ermitteln
    selected_volk = None
    for volk, aktiv in charakter.voelker_selected.items():
        if aktiv:
            selected_volk = volk
            break

    if not selected_volk:
        volk_section.append(Paragraph("Kein Volk ausgewählt.", style_normal))
    else:
        # Ausgewähltes Volk aus charakter.voelker holen
        volk_obj = charakter.voelker.get(selected_volk, None)

        volk_text = f"Volk: {selected_volk}"
        volk_section.append(Paragraph(volk_text, style_heading))

        if not volk_obj:
            volk_section.append(Paragraph("Keine Daten für das ausgewählte Volk vorhanden.", style_normal))
        else:
            # Talente
            if volk_obj.talente:
                volk_section.append(Paragraph(" ", style_normal))
                talente_table_data = [["Talent"]]
                for talent in volk_obj.talente:
                    talente_table_data.append([Paragraph(talent, style_normal)])
                talente_table = Table(talente_table_data, colWidths=[200], hAlign='LEFT')
                talente_table.setStyle(TableStyle(tabellen_style_commands.copy()))
                volk_section.append(talente_table)
                volk_section.append(Spacer(3, 1))

            # Handicaps
            if volk_obj.handicaps:
                volk_section.append(Paragraph(" ", style_normal))
                handicaps_table_data = [["Handicap"]]
                for handicap in volk_obj.handicaps:
                    handicaps_table_data.append([Paragraph(handicap, style_normal)])
                handicaps_table = Table(handicaps_table_data, colWidths=[200], hAlign='LEFT')
                handicaps_table.setStyle(TableStyle(tabellen_style_commands.copy()))
                volk_section.append(handicaps_table)
                volk_section.append(Spacer(3, 1))

            # Besonderheiten
            if volk_obj.besonderheiten:
                volk_section.append(Paragraph(" ", style_normal))
                besonderheiten_table_data = [["Besonderheit"]]
                for besonderheit in volk_obj.besonderheiten:
                    besonderheiten_table_data.append([Paragraph(besonderheit, style_normal)])
                besonderheiten_table = Table(besonderheiten_table_data, colWidths=[200], hAlign='LEFT')
                besonderheiten_table.setStyle(TableStyle(tabellen_style_commands.copy()))
                volk_section.append(besonderheiten_table)
                volk_section.append(Spacer(3, 1))

    right_column_content.append(volk_section)
    right_column_content.append(Spacer(1, 6))      

    abgeleitete_header = Paragraph("Abgeleitete Werte", style_heading)
    abgeleitete_data = [["Beschreibung", "Wert"]]
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
    for key, value in abgeleitete_werte.items():
        abgeleitete_data.append([key, str(value)])

    abgeleitete_table = Table(abgeleitete_data, colWidths=[100, 70], hAlign='LEFT')
    abgeleitete_table.setStyle(tabellen_style)
    right_column_content.append(abgeleitete_header)
    right_column_content.append(abgeleitete_table)
    right_column_content.append(Spacer(1, 6))  # 6 Punkte Abstand

    # **Kombinieren der linken und rechten Spalte mit Abstand**
    combined_data = [
        [left_column_content, Spacer(1, 10), right_column_content]
    ]
    combined_table = Table(combined_data, colWidths=[200, 20, 180], hAlign='LEFT')
    combined_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Inhalt oben ausrichten
    ]))
    combined_section.append(combined_table)
    combined_section.append(Spacer(1, 6))  # 6 Punkte Abstand
    elements.append(KeepTogether(combined_section))

    # **Handicaps Abschnitt**
    handicaps_section = []
    handicaps_section.append(Paragraph("Handicaps", style_heading))
    handicaps = charakter.selected_handicaps
    data = [["Handicap", "Stufe"]]
    for handicap_name_key in handicaps:
        handicap = charakter.handicaps.get(handicap_name_key)
        if handicap:
            data.append([handicap.name, handicap.stufe])
            # Beschreibung hinzufügen
            beschreibung_paragraph = Paragraph(handicap.beschreibung, style_normal)
            data.append([beschreibung_paragraph, ''])  # Leeres Feld für zweite Spalte

    table = Table(data, colWidths=[450, 75], hAlign='LEFT')  # Summe = 275 + 300 = 575
    # Definieren eines neuen TableStyle für Handicaps, basierend auf tabellen_style_commands
    handicaps_style_commands = tabellen_style_commands.copy()
    for row in range(2, len(data), 2):
        handicaps_style_commands.extend([
            ('SPAN', (0, row), (-1, row)),          # Span über alle Spalten
            ('BACKGROUND', (0, row), (-1, row), oldlace),  # Hintergrundfarbe für Beschreibung
        ])

    handicaps_style = TableStyle(handicaps_style_commands)
    table.setStyle(handicaps_style)
    handicaps_section.append(table)
    handicaps_section.append(Spacer(1, 12))  # 12 Punkte Abstand
    elements.append(KeepTogether(handicaps_section))

    # **Talente Abschnitt**
    talente_section = []
    talente_section.append(Paragraph("Talente", style_heading))
    talente = charakter.selected_talente
    data = [["Talent", "Rang"]]
    for talent_name_key in talente:
        talent = charakter.talente.get(talent_name_key)
        if talent:
            data.append([
                talent.name,
                talent.rang,
            ])
            # Beschreibung hinzufügen
            beschreibung_paragraph = Paragraph(talent.beschreibung, style_normal)
            data.append([beschreibung_paragraph])  # Nur eine Spalte

    table = Table(data, colWidths=[450, 75], hAlign='LEFT')  # Nur eine Spalte, volle Breite
    # Definieren eines neuen TableStyle für Talente, basierend auf tabellen_style_commands
    talente_style_commands = tabellen_style_commands.copy()
    for row in range(2, len(data), 2):
        talente_style_commands.extend([
            ('SPAN', (0, row), (-1, row)),          # Span über alle Spalten (hier nur eine)
            ('BACKGROUND', (0, row), (-1, row), oldlace),  # Hintergrundfarbe für Beschreibung
        ])

    talente_style = TableStyle(talente_style_commands)
    table.setStyle(talente_style)
    talente_section.append(table)
    talente_section.append(Spacer(1, 12))  # 12 Punkte Abstand
    elements.append(KeepTogether(talente_section))

    # **Mächte Abschnitt**
    maechte_section = []
    maechte_section.append(Paragraph("Mächte", style_heading))
    maechte = charakter.selected_maechte
    data = [["Name", "Rang", "MP", "Reichweite", "Dauer"]]
    for macht_name_key in maechte:
        macht = charakter.maechte.get(macht_name_key)
        if macht:
            data.append([
                macht.name,
                macht.rang,
                macht.machtpunkte,
                macht.reichweite,
                macht.dauer
            ])
            # Beschreibung hinzufügen
            beschreibung_paragraph = Paragraph(macht.beschreibung, style_normal)
            data.append([beschreibung_paragraph] + [''] * 4)  # Beschreibung über alle 6 Spalten

    table = Table(data, colWidths=[205, 80, 80, 80, 80], hAlign='LEFT')  # Summe = 575
    # Definieren eines neuen TableStyle für Mächte, basierend auf tabellen_style_commands
    maechte_style_commands = tabellen_style_commands.copy()
    for row in range(2, len(data), 2):
        maechte_style_commands.extend([
            ('SPAN', (0, row), (-1, row)),          # Span über alle Spalten
            ('BACKGROUND', (0, row), (-1, row), oldlace),  # Hintergrundfarbe für Beschreibung
        ])

    maechte_style = TableStyle(maechte_style_commands)
    table.setStyle(maechte_style)
    maechte_section.append(table)
    maechte_section.append(Spacer(1, 12))  # 12 Punkte Abstand
    elements.append(KeepTogether(maechte_section))

    # **Allgemeine Ausrüstung Abschnitt** (analog zu Waffen)
    allgemeine_ausruestung_section = []
    allgemeine_ausruestung_section.append(Paragraph("Allgemeine Ausrüstung", style_heading))

    allgemeine_ausruestung_items = [item for name, item in charakter.ausruestung.items()
                                    if item in charakter.selected_allgemeine_ausruestung and item.ausgewaehlt]

    # Spalten analog zu Waffen (dort Name, Schaden etc.): hier Name, Menge, Beschreibung
    data = [["Name", "Menge", "Beschreibung"]]
    for item in allgemeine_ausruestung_items:
        menge = getattr(item, 'menge', 1)
        beschreibung_text = getattr(item, 'beschreibung', '-')

        # Hier wird ein Paragraph-Objekt für die Beschreibung erstellt
        beschreibung_paragraph = Paragraph(beschreibung_text, style_normal)

        data.append([
            item.name,
            str(menge),
            beschreibung_paragraph
        ])

    allgemeine_table = Table(data, colWidths=[175, 50, 300], hAlign='LEFT')
    allgemeine_table.setStyle(TableStyle(tabellen_style_commands.copy()))
    allgemeine_ausruestung_section.append(allgemeine_table)
    allgemeine_ausruestung_section.append(Spacer(1, 12))
    elements.append(KeepTogether(allgemeine_ausruestung_section))

    # **Waffen Abschnitt**
    waffen_section = []
    waffen_section.append(Paragraph("Waffen", style_heading))
    waffen = [w for w in charakter.selected_waffen if w.angelegt]
    data = [["Name", "Schaden", "Reichweite", "FR", "Schuss", "PB"]]
    for waffe in waffen:
        eigenschaften = waffe.eigenschaften
        data.append([
            waffe.name,
            eigenschaften.get('Schaden', '-'),
            eigenschaften.get('Reichweite', '-'),
            eigenschaften.get('FR', '-'),
            eigenschaften.get('Schuss', '-'),
            eigenschaften.get('PB', '-')
        ])

    # Berechnung der Spaltenbreiten basierend auf Anzahl der Spalten und Gesamtbreite 
    waffen_table = Table(data, colWidths=[205, 70, 70, 60, 60, 60], hAlign='LEFT')  # Summe = 575
    waffen_table.setStyle(tabellen_style)
    waffen_section.append(waffen_table)
    waffen_section.append(Spacer(1, 12))  # 12 Punkte Abstand
    elements.append(KeepTogether(waffen_section))

    # **Rüstungen Abschnitt**
    ruestungen_section = []
    ruestungen_section.append(Paragraph("Rüstungen", style_heading))
    ruestungen = [r for r in charakter.selected_ruestungen if r.angelegt]
    if ruestungen:
        data = [["Name", "Torso", "Arme", "Beine", "Kopf"]]
        for ruestung in ruestungen:
            data.append([
                ruestung.name,
                str(ruestung.torso),
                str(ruestung.arme),
                str(ruestung.beine),
                str(ruestung.kopf)
            ])
        # Gesamten Rüstungsschutz berechnen
        gesamt_ruestungsschutz = charakter.berechne_gesamt_ruestungsschutz()
        # Gesamtrüstungsschutz als letzte Zeile hinzufügen
        data.append([
            "Gesamt",
            str(gesamt_ruestungsschutz['Torso']),
            str(gesamt_ruestungsschutz['Arme']),
            str(gesamt_ruestungsschutz['Beine']),
            str(gesamt_ruestungsschutz['Kopf'])
        ])
        # Berechnung der Spaltenbreiten basierend auf Anzahl der Spalten und Gesamtbreite
        table = Table(data, colWidths=[205, 80, 80, 80, 80], hAlign='LEFT')  # Summe = 525
        ruestungen_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), moccasin),
            ('BACKGROUND', (0, 1), (-1, -2), oldlace),
            ('BACKGROUND', (0, -1), (-1, -1), moccasin),  # Letzte Zeile
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Kopfzeile fett
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Letzte Zeile fett
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(ruestungen_style)
        ruestungen_section.append(table)
    else:
        ruestungen_section.append(Paragraph("Keine Rüstungen angelegt.", style_normal))
    ruestungen_section.append(Spacer(1, 12))  # 12 Punkte Abstand
    elements.append(KeepTogether(ruestungen_section))

    # **Schilde Abschnitt** (analog zu Waffen)
    schilde_section = []
    schilde_section.append(Paragraph("Schilde", style_heading))

    # Analog zu Waffen (waffen = [w for w in ... if w.angelegt]):
    # Bei Schilden: nur angelegte Schilde anzeigen
    schilde_items = [
        s for name, s in charakter.ausruestung.items()
        if s in charakter.selected_schilde and s.angelegt
        ]

    # Spalten analog zu Waffen, nur an Schilde angepasst:
    # Name, Parade, Deckung, Mindeststärke, Beschreibung
    data = [["Name", "Parade", "Deckung", "Mindeststärke"]]
    for schild in schilde_items:
        parade = getattr(schild, 'parade', '-')
        deckung = getattr(schild, 'deckung', '-')
        mindeststaerke = getattr(schild, 'mindeststaerke', '-')
        data.append([
            schild.name,
            str(parade),
            str(deckung),
            mindeststaerke
        ])

    schilde_table = Table(data, colWidths=[265, 80, 80, 100], hAlign='LEFT')
    schilde_table.setStyle(TableStyle(tabellen_style_commands.copy()))
    schilde_section.append(schilde_table)
    schilde_section.append(Spacer(1, 12))
    elements.append(KeepTogether(schilde_section))

    # PDF erstellen mit oder ohne Hintergrundbild
    if printer_friendly:
        doc.build(elements)
    else:
        doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)

    Logger.info(f"PDF wurde erfolgreich erstellt unter: {output_pdf}")
    
    return True

def create_mod_text(modifier):
    """
    Erstellt den Text für den Modifier.
    """
    if modifier != 0:
        return f"{modifier:+}"
    else:
        return ""