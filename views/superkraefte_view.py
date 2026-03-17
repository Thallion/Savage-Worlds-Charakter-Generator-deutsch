# views/superkraefte_view.py
"""
Eigenständige View-Komponente für Superkräfte nach dem MVC-Pattern.
Zeigt Machtstufen-Header, SKP-Anzeige, gewählte Kräfte-Liste und Action-Buttons.
Verwendet den SuperkraftDialogHandler für Auswahl/Konfiguration.
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.progressindicator import MDLinearProgressIndicator

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp


class SuperkraefteWidget(MDBoxLayout):
    """
    Eigenständiges Widget zur Anzeige und Verwaltung von Superkräften.
    Wird als eigener Tab im Superkräfte-Setting angezeigt.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.padding = dp(10)

        # Controller-Referenz
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None

        # UI-Referenzen
        self._machtstufe_label = None
        self._skp_label = None
        self._progress_bar = None
        self._krafte_list_box = None
        self._placeholder_label = None

        # Dialog-Handler
        self._dialog_handler = None

        Clock.schedule_once(self._setup_view, 0.1)

    @property
    def dialog_handler(self):
        """Lazy-Init des DialogHandlers."""
        if self._dialog_handler is None:
            from views.superkraft_popup import SuperkraftDialogHandler
            self._dialog_handler = SuperkraftDialogHandler(self.controller)
        return self._dialog_handler

    def _get_charakter(self):
        """Gibt das Charakter-Objekt zurück."""
        if self.controller and hasattr(self.controller, 'charakter'):
            return self.controller.charakter
        return None

    def _setup_view(self, dt):
        """Setzt die Superkräfte-UI auf."""
        try:
            self._create_machtstufe_header()
            self._create_superkraefte_list()
            self._create_action_buttons()
            self.refresh_widget()
        except Exception as e:
            Logger.error(f"Fehler beim Setup der Superkräfte-View: {e}")

    def _create_machtstufe_header(self):
        """Erstellt den Header mit Machtstufen-Info und SKP-Anzeige."""
        header_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            height=dp(120),
            padding=dp(15)
        )

        # Machtstufen-Zeile
        machtstufe_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        machtstufe_label = MDLabel(
            text="Machtstufe:",
            size_hint_x=None,
            width=dp(100),
            theme_text_color="Primary"
        )

        self._machtstufe_label = MDButton(
            MDButtonText(text="III - Four-Color-Helden"),
            style="text",
            on_release=self._on_machtstufe_click
        )

        machtstufe_row.add_widget(machtstufe_label)
        machtstufe_row.add_widget(self._machtstufe_label)
        header_layout.add_widget(machtstufe_row)

        # SKP-Zeile
        skp_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        skp_label = MDLabel(
            text="SKP:",
            size_hint_x=None,
            width=dp(100),
            theme_text_color="Primary"
        )

        self._skp_label = MDLabel(
            text="0/45  Obergrenze: 15",
            theme_text_color="Secondary"
        )

        skp_row.add_widget(skp_label)
        skp_row.add_widget(self._skp_label)
        header_layout.add_widget(skp_row)

        # Fortschrittsbalken
        self._progress_bar = MDLinearProgressIndicator(
            value=0,
            size_hint_y=None,
            height=dp(6),
            indicator_color=[0.2, 0.8, 0.2, 1]
        )
        header_layout.add_widget(self._progress_bar)

        self.add_widget(header_layout)

    def _create_superkraefte_list(self):
        """Erstellt den scrollbaren Bereich für gewählte Superkräfte."""
        from kivymd.uix.scrollview import MDScrollView

        list_header = MDLabel(
            text="Gewählte Superkräfte:",
            theme_text_color="Primary",
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(32)
        )
        self.add_widget(list_header)

        scroll = MDScrollView(size_hint_y=1)
        self._krafte_list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            padding=(0, 0, 0, dp(8)),
        )
        self._krafte_list_box.bind(minimum_height=self._krafte_list_box.setter('height'))

        # Platzhalter
        self._placeholder_label = MDLabel(
            text="Noch keine Superkräfte gewählt.\n\n"
                 "Klicke auf '+ Superkraft hinzufügen' um Kräfte auszuwählen.",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(100),
        )
        self._krafte_list_box.add_widget(self._placeholder_label)

        scroll.add_widget(self._krafte_list_box)
        self.add_widget(scroll)

    def _create_action_buttons(self):
        """Erstellt die Action-Buttons."""
        button_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        add_button = MDButton(
            MDButtonText(text="+ Superkraft hinzufügen"),
            style="elevated",
            on_release=self._on_add_superkraft
        )

        button_row.add_widget(add_button)
        self.add_widget(button_row)

    # ==================== EVENT HANDLER ====================

    def _on_add_superkraft(self, instance):
        """Öffnet den Superkraft-Auswahl-Dialog."""
        Logger.info("SuperkraefteWidget: Superkraft hinzufügen")
        self.dialog_handler.show_auswahl_dialog()

    def _on_machtstufe_click(self, instance):
        """Öffnet den Machtstufe-Auswahl-Dialog."""
        Logger.info("SuperkraefteWidget: Machtstufe ändern")
        self.dialog_handler.show_machtstufe_dialog()

    def _on_kraft_entfernen(self, kraft_name):
        """Öffnet den Entfernen-Dialog für eine Superkraft."""
        Logger.info(f"SuperkraefteWidget: Superkraft '{kraft_name}' entfernen")
        self.dialog_handler.show_entfernen_dialog(kraft_name)

    # ==================== REFRESH ====================

    def refresh_widget(self):
        """Aktualisiert die komplette Superkräfte-Anzeige mit aktuellen Charakter-Daten."""
        Logger.debug("SuperkraefteWidget: refresh_widget")
        charakter = self._get_charakter()
        if not charakter:
            return

        self._update_header(charakter)
        self._update_krafte_list(charakter)

    def _update_header(self, charakter):
        """Aktualisiert Machtstufe, SKP und Fortschrittsbalken."""
        stufe = getattr(charakter, 'machtstufe', 'III')
        skp_gesamt = getattr(charakter, 'superkraft_punkte_gesamt', 0)
        skp_verbraucht = getattr(charakter, 'superkraft_punkte_verbraucht', 0)
        obergrenze = getattr(charakter, 'kraftobergrenze', 15)

        # Machtstufen-Namen
        stufen_namen = {
            "I": "I - Pulp-Helden",
            "II": "II - Straßenkämpfer",
            "III": "III - Four-Color-Helden",
            "IV": "IV - Schwere Kaliber",
            "V": "V - Kosmische Beschützer",
        }
        stufen_text = stufen_namen.get(stufe, stufe)

        if self._machtstufe_label:
            # MDButton enthält MDButtonText als Kind
            for child in self._machtstufe_label.children:
                if hasattr(child, 'text'):
                    child.text = stufen_text
                    break

        if self._skp_label:
            verbleibend = skp_gesamt - skp_verbraucht
            self._skp_label.text = (
                f"{skp_verbraucht}/{skp_gesamt}  "
                f"Verfügbar: {verbleibend}  "
                f"Obergrenze: {obergrenze}"
            )

        if self._progress_bar:
            if skp_gesamt > 0:
                prozent = min(100, (skp_verbraucht / skp_gesamt) * 100)
                self._progress_bar.value = prozent
                # Farbe je nach Auslastung
                if prozent > 90:
                    self._progress_bar.indicator_color = [0.8, 0.2, 0.2, 1]
                elif prozent > 70:
                    self._progress_bar.indicator_color = [0.8, 0.8, 0.2, 1]
                else:
                    self._progress_bar.indicator_color = [0.2, 0.8, 0.2, 1]
            else:
                self._progress_bar.value = 0

    def _update_krafte_list(self, charakter):
        """Aktualisiert die Liste der gewählten Superkräfte."""
        if not self._krafte_list_box:
            return

        self._krafte_list_box.clear_widgets()

        import functions.superkraft_funktionen as skf
        ausgewaehlt = skf.ausgewaehlte_superkraefte(charakter)

        if not ausgewaehlt:
            # Platzhalter anzeigen
            self._placeholder_label = MDLabel(
                text="Noch keine Superkräfte gewählt.\n\n"
                     "Klicke auf '+ Superkraft hinzufügen' um Kräfte auszuwählen.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(100),
            )
            self._krafte_list_box.add_widget(self._placeholder_label)
            return

        for kraft in sorted(ausgewaehlt, key=lambda k: k.name):
            kraft_card = self._create_kraft_card(kraft)
            self._krafte_list_box.add_widget(kraft_card)

    def _create_kraft_card(self, kraft):
        """Erstellt eine Card für eine gewählte Superkraft."""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=dp(12),
            style="outlined",
        )

        # Obere Zeile: Name + Kosten + Entfernen-Button
        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
        )

        name_label = MDLabel(
            text=kraft.name,
            theme_text_color="Primary",
            font_style="Title",
            role="small",
            size_hint_x=0.6,
        )

        kosten_label = MDLabel(
            text=f"{kraft.gesamt_kosten} SKP",
            theme_text_color="Secondary",
            halign="right",
            size_hint_x=0.25,
        )

        entfernen_btn = MDIconButton(
            icon="close-circle-outline",
            style="standard",
            on_release=lambda x, n=kraft.name: self._on_kraft_entfernen(n),
        )

        top_row.add_widget(name_label)
        top_row.add_widget(kosten_label)
        top_row.add_widget(entfernen_btn)
        card.add_widget(top_row)

        # Untere Zeile: Modifikatoren
        if kraft.gewaehlte_modifikatoren:
            mod_namen = [m.name for m in kraft.gewaehlte_modifikatoren]
            mod_text = "Mods: " + ", ".join(mod_namen)
        else:
            mod_text = kraft.beschreibung[:80] + ("..." if len(kraft.beschreibung) > 80 else "")

        detail_label = MDLabel(
            text=mod_text,
            theme_text_color="Secondary",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(detail_label)

        return card
