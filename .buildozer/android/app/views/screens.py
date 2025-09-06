# views/screens.py
"""
Screen-Klassen extrahiert aus main.py für bessere Code-Organisation
"""

import re
import webbrowser
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText


class EinstellungenScreen(MDScreen):
    def aktualisiere_ui(self):
        """Delegiert an das EinstellungenWidget"""
        try:
            if hasattr(self.ids, 'einstellungen_widget'):
                widget = self.ids.einstellungen_widget
                if widget and hasattr(widget, 'aktualisiere_ui'):
                    widget.aktualisiere_ui()
                    return True
            Logger.warning("EinstellungenWidget oder aktualisiere_ui nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei EinstellungenScreen.aktualisiere_ui: {str(e)}")
            return False


class VoelkerScreen(MDScreen):
    def aktualisiere_ui(self):
        """Delegiert an das VoelkerWidget"""
        try:
            if hasattr(self.ids, 'voelker_widget'):
                widget = self.ids.voelker_widget
                if widget and hasattr(widget, 'aktualisiere_ui'):
                    widget.aktualisiere_ui()
                    return True
            Logger.warning("VoelkerWidget oder aktualisiere_ui nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei VoelkerScreen.aktualisiere_ui: {str(e)}")
            return False


class ProfilScreen(MDScreen):
    def load_profil(self):
        """Delegiert an das ProfilWidget"""
        try:
            if hasattr(self.ids, 'profil_widget'):
                widget = self.ids.profil_widget
                if widget and hasattr(widget, 'load_profil'):
                    widget.load_profil()
                    return True
            Logger.warning("ProfilWidget oder load_profil nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei ProfilScreen.load_profil: {str(e)}")
            return False


class EigenschaftenScreen(MDScreen):
    def update_eigenschaften(self):
        """Delegiert an das EigenschaftenWidget"""
        try:
            if hasattr(self.ids, 'eigenschaften_widget'):
                widget = self.ids.eigenschaften_widget
                if widget and hasattr(widget, 'update_eigenschaften'):
                    widget.update_eigenschaften()
                    return True
            Logger.warning("EigenschaftenWidget oder update_eigenschaften nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei EigenschaftenScreen.update_eigenschaften: {str(e)}")
            return False


class HandicapsScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das HandicapsWidget"""
        try:
            if hasattr(self.ids, 'handicaps_widget'):
                widget = self.ids.handicaps_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("HandicapsWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei HandicapsScreen.refresh_widget: {str(e)}")
            return False


class TalenteScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das TalenteWidget"""
        try:
            if hasattr(self.ids, 'talente_widget'):
                widget = self.ids.talente_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("TalenteWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei TalenteScreen.refresh_widget: {str(e)}")
            return False


class MaechteScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das MaechteWidget"""
        try:
            if hasattr(self.ids, 'maechte_widget'):
                widget = self.ids.maechte_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("MaechteWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei MaechteScreen.refresh_widget: {str(e)}")
            return False


class AusruestungScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das AusruestungWidget"""
        try:
            if hasattr(self.ids, 'ausruestung_widget'):
                widget = self.ids.ausruestung_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("AusruestungWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei AusruestungScreen.refresh_widget: {str(e)}")
            return False


class CharakterbogenScreen(MDScreen):
    def update_overview(self, *args):
        """Delegiert an das CharakterbogenWidget"""
        try:
            if hasattr(self.ids, 'charakterbogen_widget'):
                widget = self.ids.charakterbogen_widget
                if widget and hasattr(widget, 'update_overview'):
                    widget.update_overview(*args)
                    return True
            Logger.warning("CharakterbogenWidget oder update_overview nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei CharakterbogenScreen.update_overview: {str(e)}")
            return False


class HistorieScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das HistorieWidget"""
        try:
            if hasattr(self.ids, 'historie_widget'):
                widget = self.ids.historie_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("HistorieWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei HistorieScreen.refresh_widget: {str(e)}")
            return False


class InfoScreen(MDScreen):
    info_text = StringProperty("""
    Lizenz- und Urheberrechtsinformationen
    Savage Worlds Fan-Produkt

    „Dieses Produkt bezieht sich auf das Regelsystem Savage Worlds, 
    erhältlich bei der Pinnacle Entertainment Group unter www.peginc.com. 
    Savage Worlds und alle zugehörigen Logos und Warenzeichen sind 
    urheberrechtlich geschützt durch die Pinnacle Entertainment Group. 
    Verwendung mit Genehmigung. Die deutsche Übersetzung der 
    Begrifflichkeiten von Ulisses Spiele darf verwendet werden. 
    Pinnacle oder Ulisses Spiele geben keine Zusicherungen oder 
    Garantien in Bezug auf die Qualität, Funktionsfähigkeit oder 
    Eignung dieses Produkts für einen bestimmten Zweck."

    „This game references the Savage Worlds game system, 
    available from Pinnacle Entertainment Group at www.peginc.com. 
    Savage Worlds and all associated logos and trademarks are copyrights 
    of Pinnacle Entertainment Group. Used with permission.
    Pinnacle makes no representation or warranty as to the quality, 
    viability, or suitability for purpose of this product."

    Danksagungen: 
    Vielen Dank an Ulisses Spiele für die Genehmigung der App.
    Danke an die Pinnacle Entertainment Group für dieses großartige Rollenspiel
    und an Ulisses Spiele für die Übersetzung ins Deutsche.
    Besonderer Dank gilt allen Testusern, die fleißig Bugs gesammelt und 
    tolle Anregungen geliefert haben. 
    Danke an alle Savage-Fans, die dem Spiel Leben einhauchen.

    Links:
    """)
    
    # Liste der Links und deren Beschreibungen
    links = [
        ("Ulisses E-Book-Store", "https://www.ulisses-ebooks.de/browse.php?sort=4a&src=fid45795&filters=45795_0_0"),
        ("Pinnacle Entertainment Group", "https://www.peginc.com"),
        ("Savage Worlds Deutschland", "https://ulisses-spiele.de/game-system/savage-worlds/")
    ]

    def on_kv_post(self, base_widget):
        """Fügt die Link-Buttons hinzu, nachdem das KV geladen wurde."""
        # Container für Links finden
        container = self.ids.link_container
        
        # Container für linksbündige Ausrichtung konfigurieren
        container.spacing = dp(4)
        container.padding = [dp(10), dp(4), dp(10), dp(4)]  # links, oben, rechts, unten
        
        # Für jeden Link einen Button erstellen
        for label, url in self.links:
            btn = MDButton(
                style="elevated",
                size_hint_x=None,  # Keine horizontale Größenbindung
                size_hint_y=None,
                height=dp(50),
                pos_hint={"x": 0},  # Linksbündige Positionierung
                on_release=lambda x, u=url: self.open_link(u)
            )
            # Text als Kind-Widget hinzufügen
            btn_text = MDButtonText(
                text=label,
                padding=[dp(20), 0]  # Seitenpolsterung für den Text
            )
            btn.add_widget(btn_text)
            container.add_widget(btn)
            
            # Nach dem Hinzufügen die Breite des Buttons berechnen
            Clock.schedule_once(lambda dt, btn=btn, lbl=label: self._adjust_button_width(btn, lbl), 0)
        
    def _adjust_button_width(self, button, text):
        """Passt die Breite des Buttons basierend auf der Textlänge an."""
        min_width = dp(200)  # Mindestbreite
        # Ungefähre Berechnung der Textbreite (kann verfeinert werden)
        estimated_width = len(text) * dp(10) + dp(40)  # 10dp pro Zeichen + Padding
        button.width = max(min_width, estimated_width)
            
    def open_link(self, url):
        """Öffnet einen Link im Browser."""
        Logger.info(f"Öffne Link: {url}")
        webbrowser.open(url)


# Hyperlink Label-Klasse extrahiert
class HyperlinkLabel(MDLabel):
    """
    Eine benutzerdefinierte MDLabel, die Hyperlinks erkennt und öffnet.
    """
    def __init__(self, **kwargs):
        # Aktiviere Markup
        kwargs['markup'] = True
        super().__init__(**kwargs)
        
        # Speicherung für URL-Informationen
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.urls = []
        self.original_text = ""  # Speichert den Text ohne Markup
        self.hover_cursor = 'hand'
        
        # Einmalige Verarbeitung des Texts
        Clock.schedule_once(self.process_text, 0)
    
    def process_text(self, dt):
        """Verarbeitet den initialen Text, um URLs zu erkennen und zu formatieren."""
        # Originaltext speichern
        self.original_text = self.text
        
        # Wenn kein Text da ist, nichts tun
        if not self.original_text:
            return
        
        # URLs im Text finden
        self.urls = []
        formatted_text = self.original_text
        offset = 0  # Versatz durch hinzugefügte Markup-Tags
        
        for match in self.url_pattern.finditer(self.original_text):
            start, end = match.span()
            url = match.group(0)
            
            # URL in der Liste speichern
            self.urls.append((start, end, url))
            
            # URL im Text formatieren
            markup = f'[color=#3498db][u]{url}[/u][/color]'
            formatted_text = (
                formatted_text[:start+offset] + 
                markup + 
                formatted_text[end+offset:]
            )
            
            # Offset für nächste URL anpassen
            offset += len(markup) - len(url)
        
        # Text mit markierten Links setzen
        if self.urls:
            Logger.info(f"HyperlinkLabel: {len(self.urls)} URLs formatiert")
            self.text = formatted_text
    
    def on_touch_down(self, touch):
        """Erkennt Klicks auf Links und öffnet sie im Browser."""
        if self.collide_point(*touch.pos) and self.urls:
            # Berechne Position im Text
            x_rel = (touch.x - self.x) / self.width
            pos = int(x_rel * len(self.original_text))
            
            # Prüfe, ob auf eine URL geklickt wurde
            for start, end, url in self.urls:
                if start - 5 <= pos <= end + 5:  # Etwas Toleranz für die Klickposition
                    Logger.info(f"Link angeklickt: {url}")
                    webbrowser.open(url)
                    return True
                    
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Ändert den Cursor über Links."""
        if self.collide_point(*touch.pos) and self.urls:
            x_rel = (touch.x - self.x) / self.width
            pos = int(x_rel * len(self.original_text))
            
            for start, end, url in self.urls:
                if start - 5 <= pos <= end + 5:
                    Window.set_system_cursor(self.hover_cursor)
                    return True
            
            Window.set_system_cursor('arrow')
        
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Setzt den Cursor zurück."""
        Window.set_system_cursor('arrow')
        return super().on_touch_up(touch)