# views/popup_form.py
"""
Deklarative Formular-Dialoge für die Element-Popups (Add/Edit-Flow).

Ersetzt die fast identischen *DialogContent-Klassen und die duplizierten
show_add_dialog/show_edit_dialog/save_*/update_*-Methoden der Element-Handler
durch eine Feld-Spezifikation pro Handler:

    FELDER = [
        {"key": "name", "label": "Name der Waffe", "typ": "text", "pflicht": True},
        {"key": "gewicht", "label": "Gewicht", "typ": "float", "default": 0},
        {"key": "mindeststaerke", "label": "Mindeststärke", "typ": "auswahl",
         "erlaubt": ["W4", "W6", "W8", "W10", "W12", "-"]},
        {"key": "attribut", "label": "Attribut wählen", "typ": "dropdown",
         "optionen": <Liste oder Callable>, "pflicht": True},
        {"key": "grundfertigkeit", "label": "Grundfertigkeit", "typ": "checkbox"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "multiline"},
    ]

Feld-Typen: text, int, float, multiline, auswahl (Freitext mit erlaubter
Wertemenge), dropdown (MDDropDownItem + MDDropdownMenu), checkbox (einzelne
Standalone-Checkbox mit Label).

WICHTIG (Android, docs/ANDROID_WORKAROUNDS.md):
- Der Content enthält KEINEN eigenen ScrollView — das ElementOverlay scrollt
  bereits über TextFieldScrollView (verschachtelte ScrollViews brechen das
  Touch-Handling).
- Checkbox-LISTEN gehören weiterhin in separate Popups (Solution 3). Erlaubt
  ist hier nur die einzelne Standalone-Checkbox (Parität zum bisherigen
  Fertigkeiten-Dialog).
- Das Befüllen im Edit-Modus bleibt Clock-verzögert (0.1 s) wie in den
  bisherigen _fill_fields-Implementierungen.
"""

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

TEXTFELD_TYPEN = ("text", "int", "float", "auswahl", "multiline")


class FormDialogContent(MDBoxLayout):
    """Baut die Formular-Widgets aus einer Feld-Spezifikation auf.

    Layout-Parität zu den bisherigen KV-Definitionen: vertikale Box,
    spacing/padding 12dp, outlined-Textfelder mit Hint-Text, int/float
    über input_filter.
    """

    def __init__(self, felder, daten=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('spacing', dp(12))
        kwargs.setdefault('padding', dp(12))
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.adaptive_height = True

        self.felder = felder
        self.feld_widgets = {}
        self.dropdown_werte = {}
        self._dropdown_texte = {}

        for feld in felder:
            self._baue_feld(feld)

        if daten:
            # Clock-verzögert befüllen (Widgets erst nach dem Frame bereit)
            Clock.schedule_once(lambda dt: self.fill(daten), 0.1)

    # ------------------------------------------------------------------
    # Aufbau
    # ------------------------------------------------------------------
    def _baue_feld(self, feld):
        typ = feld.get('typ', 'text')

        if typ in TEXTFELD_TYPEN:
            textfeld = MDTextField(mode="outlined")
            if typ == 'int':
                textfeld.input_filter = 'int'
            elif typ == 'float':
                textfeld.input_filter = 'float'
            if typ == 'multiline':
                textfeld.multiline = True
                textfeld.size_hint_y = None
                textfeld.height = dp(96)
            textfeld.add_widget(MDTextFieldHintText(text=feld['label']))
            self.feld_widgets[feld['key']] = textfeld
            self.add_widget(textfeld)

        elif typ == 'dropdown':
            item = MDDropDownItem(pos_hint={"center_x": .5})
            item_text = MDDropDownItemText(text=feld['label'])
            item.add_widget(item_text)
            item.bind(on_release=lambda inst, f=feld: self._open_dropdown(inst, f))
            self.feld_widgets[feld['key']] = item
            self._dropdown_texte[feld['key']] = item_text
            self.add_widget(item)

        elif typ == 'checkbox':
            box = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(48),
                spacing=dp(8),
                padding=(dp(4), 0, 0, 0),
            )
            checkbox = MDCheckbox(
                active=bool(feld.get('default', False)),
                size_hint=(None, None),
                size=(dp(48), dp(48)),
            )
            box.add_widget(checkbox)
            box.add_widget(MDLabel(text=feld['label'], adaptive_size=True))
            self.feld_widgets[feld['key']] = checkbox
            self.add_widget(box)

        else:
            Logger.error(f"FormDialogContent: Unbekannter Feld-Typ '{typ}' ({feld.get('key')})")

    def _open_dropdown(self, caller, feld):
        optionen = feld.get('optionen', [])
        if callable(optionen):
            optionen = optionen()
        if not optionen:
            return
        menu_items = [
            {
                "text": option,
                "on_release": lambda x=option, k=feld['key']: self._select_dropdown(k, x),
            }
            for option in optionen
        ]
        MDDropdownMenu(caller=caller, items=menu_items).open()

    def _select_dropdown(self, key, wert):
        self.dropdown_werte[key] = wert
        if key in self._dropdown_texte:
            self._dropdown_texte[key].text = wert

    # ------------------------------------------------------------------
    # Befüllen (Edit-Modus) und Einsammeln
    # ------------------------------------------------------------------
    def fill(self, daten):
        """Befüllt die Felder mit bestehenden Element-Daten."""
        for feld in self.felder:
            key = feld['key']
            if key not in daten:
                continue
            wert = daten[key]
            typ = feld.get('typ', 'text')
            widget = self.feld_widgets.get(key)
            if widget is None:
                continue
            if typ in TEXTFELD_TYPEN:
                widget.text = "" if wert is None else str(wert)
            elif typ == 'dropdown':
                if wert:
                    self._select_dropdown(key, str(wert))
            elif typ == 'checkbox':
                widget.active = bool(wert)

    def collect(self):
        """Sammelt und validiert die Feldwerte ein.

        Returns:
            (dict, list): (Werte je key, Liste der Fehlermeldungen)
        """
        werte = {}
        fehler = []

        for feld in self.felder:
            key = feld['key']
            typ = feld.get('typ', 'text')
            label = feld['label']
            widget = self.feld_widgets.get(key)

            if typ in ('text', 'multiline', 'auswahl'):
                text = widget.text.strip()
                if feld.get('pflicht') and not text:
                    fehler.append(feld.get('pflicht_meldung', f"'{label}' darf nicht leer sein."))
                    continue
                if typ == 'auswahl' and feld.get('erlaubt') and text not in feld['erlaubt']:
                    fehler.append(feld.get(
                        'erlaubt_meldung',
                        f"'{label}' muss einer der Werte {', '.join(feld['erlaubt'])} sein."
                    ))
                    continue
                werte[key] = text

            elif typ in ('int', 'float'):
                text = widget.text.strip()
                if not text and 'default' in feld:
                    werte[key] = feld['default']
                    continue
                try:
                    werte[key] = int(text) if typ == 'int' else float(text)
                except ValueError:
                    fehler.append(feld.get(
                        'zahl_meldung',
                        f"Bitte geben Sie eine gültige Zahl für '{label}' ein."
                    ))

            elif typ == 'dropdown':
                wert = self.dropdown_werte.get(key)
                if feld.get('pflicht') and not wert:
                    fehler.append(feld.get('pflicht_meldung', f"Bitte wähle '{label}' aus."))
                    continue
                werte[key] = wert

            elif typ == 'checkbox':
                werte[key] = bool(widget.active)

        return werte, fehler


class FormDialogHandlerMixin:
    """Template-Methoden für den Add/Edit-Flow der Element-Handler.

    Subklassen (zusammen mit BasisDialogHandler) konfigurieren:
        FELDER             Feld-Spezifikation (oder _get_felder() überschreiben)
        titel_neu          Dialogtitel beim Hinzufügen
        titel_bearbeiten   Dialogtitel beim Bearbeiten

    Subklassen implementieren:
        _erstelle_element(werte) -> bool
            Legt das Element an (inkl. element-spezifischer Validierung wie
            Duplikat-Check). Bei False/Fehlermeldung KEIN dismiss.
        _aktualisiere_element(element_key, werte) -> bool   (nur bei Edit-Flow)
        _get_element_daten(element_key) -> dict oder None   (nur bei Edit-Flow)
        _nach_speichern()   optionaler UI-Refresh (Default: Einstellungen-Widget)
    """

    FELDER = []
    titel_neu = "Neues Element hinzufügen"
    titel_bearbeiten = "Element bearbeiten"

    def _get_felder(self):
        return self.FELDER

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    def _erstelle_element(self, werte):
        raise NotImplementedError

    def _aktualisiere_element(self, element_key, werte):
        raise NotImplementedError

    def _get_element_daten(self, element_key):
        raise NotImplementedError

    def _nach_speichern(self):
        app = App.get_running_app()
        if hasattr(app, 'einstellungen_widget'):
            app.einstellungen_widget.aktualisiere_ui()

    # ------------------------------------------------------------------
    # Add/Edit-Flow
    # ------------------------------------------------------------------
    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen eines neuen Elements."""
        self.dialog_content = FormDialogContent(self._get_felder())
        self._get_overlay().open(
            title=self.titel_neu,
            content_widget=self.dialog_content,
            action_text="Speichern",
            on_action=self._on_save_neu,
        )

    def show_edit_dialog(self, element_key):
        """Zeigt das Overlay zum Bearbeiten eines bestehenden Elements."""
        try:
            daten = self._get_element_daten(element_key)
            if daten is None:
                self.show_error(f"{self.element_name} '{element_key}' nicht gefunden.")
                return
            self._edit_key = element_key
            self.dialog_content = FormDialogContent(self._get_felder(), daten=daten)
            self._get_overlay().open(
                title=self.titel_bearbeiten,
                content_widget=self.dialog_content,
                action_text="Speichern",
                on_action=self._on_save_bearbeiten,
            )
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def _on_save_neu(self, *args):
        if not self.dialog_content:
            Logger.error(f"{self.element_name}: Dialog-Content nicht gefunden")
            return
        werte, fehler = self.dialog_content.collect()
        if fehler:
            self.show_error(fehler[0])
            return
        try:
            if self._erstelle_element(werte):
                self._nach_speichern()
                self.dismiss_dialog()
                Logger.info(f"{self.element_name} '{werte.get('name', '')}' wurde hinzugefügt.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern ({self.element_name}): {e}")
            self.show_error(f"Fehler beim Speichern: {self.element_name}")

    def _on_save_bearbeiten(self, *args):
        element_key = getattr(self, '_edit_key', None)
        if not self.dialog_content or not element_key:
            Logger.error(f"{self.element_name}: Dialog-Content oder Auswahl nicht gefunden")
            return
        werte, fehler = self.dialog_content.collect()
        if fehler:
            self.show_error(fehler[0])
            return
        try:
            if self._aktualisiere_element(element_key, werte):
                self._nach_speichern()
                self._edit_key = None
                self.dismiss_dialog()
                Logger.info(f"{self.element_name} '{werte.get('name', '')}' wurde aktualisiert.")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren ({self.element_name}): {e}")
            self.show_error(f"Fehler beim Aktualisieren: {self.element_name}")
