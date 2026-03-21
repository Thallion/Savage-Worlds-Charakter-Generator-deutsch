# views/einstellungen_widget.py
"""
REFACTORED: Einstellungen Widget - Hauptklasse
Stark vereinfacht durch Auslagerung in Handler-Klassen
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

# Handler imports (excluding redundant theme_handler and character_handler)
from controllers.game_elements_handler import GameElementsHandler

# Service imports
from services.service_container import service_container, get_event_service
from services.event_service import EventTypes

# Manager imports - these are the primary implementations
from manager.theme_manager import ThemeManager
from manager.statistics_manager import StatisticsManager
from manager.pdf_manager import PDFManager

# KV-Datei laden mit PyInstaller-kompatiblem Pfad und Mobile-Unterstützung
from utils.path_utils import get_application_root
from utils.platform_utils import is_mobile_layout
import os

_base_path = str(get_application_root())
_mobile = is_mobile_layout()
_kv_name = 'einstellungen_widget_mobile.kv' if _mobile else 'einstellungen_widget.kv'
_kv_path = os.path.join(_base_path, 'views', _kv_name)

# Fallback auf Desktop-KV wenn Mobile-KV nicht existiert
if not os.path.exists(_kv_path):
    _kv_path = os.path.join(_base_path, 'views', 'einstellungen_widget.kv')

Builder.load_file(_kv_path)
Logger.info(f"einstellungen_widget: KV-Datei geladen: {os.path.basename(_kv_path)}")


class EinstellungenWidget(MDBoxLayout):
    """
    REFACTORED: Hauptklasse für Einstellungen
    Deutlich vereinfacht - Funktionalität in Handler-Klassen ausgelagert
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        
        # Handler initialisieren
        self._initialize_handlers()
        
        # Manager initialisieren (falls verfügbar)
        self._initialize_managers()
        
        # Event-Handler registrieren
        self._register_event_handlers()
        
        # Post-Initialisierung planen
        Clock.schedule_once(self._post_init, 0)
    
    def _initialize_handlers(self):
        """Initialisiert Handler (excluding theme - handled by manager)"""
        try:
            self.game_elements_handler = GameElementsHandler(self)
            
            Logger.info("Handler erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Handler-Initialisierung: {e}")
    
    def _initialize_managers(self):
        """Initialisiert Manager - diese sind die primären Implementierungen"""
        try:
            self.theme_manager = ThemeManager(self)
            self.statistics_manager = StatisticsManager(self)
            self.pdf_manager = PDFManager(self)
            # DialogService wird direkt über service_container verwendet (keine redundante Zwischenschicht)
            Logger.info("Manager erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Manager-Initialisierung: {e}")
            # Set defaults to prevent attribute errors
            self.theme_manager = None
            self.statistics_manager = None
            self.pdf_manager = None

    def _register_event_handlers(self):
        """Registriert Event-Handler"""
        try:
            event_service = service_container.get_event_service()
            
            if event_service:
                event_service.subscribe(EventTypes.THEME_CHANGED, self._on_theme_changed)
                event_service.subscribe(EventTypes.CHARACTER_UPDATED, self._on_character_updated)

                Logger.debug("Event-Handler für Einstellungen registriert")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Handler-Registrierung: {e}")

    def _post_init(self, dt):
        """Post-Initialisierung nach dem UI-Aufbau"""
        try:
            # Theme initialisieren (directly via manager)
            if self.theme_manager:
                self.theme_manager.initialize_theme()

            # UI-Felder aktualisierung ausgelagert

            # Statistiken aktualisieren
            if self.statistics_manager:
                self.statistics_manager.update_element_statistics_ui()

            # Mobiler Modus Switch initialisieren
            self._init_mobile_modus_switch()

            Logger.info("Post-Initialisierung erfolgreich abgeschlossen")
        except Exception as e:
            Logger.error(f"Fehler bei Post-Initialisierung: {e}")

    def _init_mobile_modus_switch(self):
        """Initialisiert die UI-Switches aus der Config"""
        try:
            config_service = service_container.get_config_service()
            if not config_service:
                return

            # Mobiler Modus Switch
            mobile_modus = config_service.get('mobile_modus', False)
            switch = self.ids.get('mobile_modus_switch')
            if switch:
                switch.unbind(on_active=None)
                switch.active = mobile_modus
                Logger.debug(f"Mobiler Modus Switch initialisiert: {mobile_modus}")

            # Logger-Leiste Switch
            show_logger = config_service.get('show_logger', True)
            logger_switch = self.ids.get('show_logger_switch')
            if logger_switch:
                logger_switch.unbind(on_active=None)
                logger_switch.active = show_logger
                Logger.debug(f"Logger Switch initialisiert: {show_logger}")
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren der UI-Switches: {e}")

    def toggle_logger(self, active):
        """Wechselt die Logger-Leiste Sichtbarkeit und speichert die Einstellung"""
        try:
            config_service = service_container.get_config_service()
            if config_service:
                config_service.set('show_logger', active)

            app = MDApp.get_running_app()
            if app and hasattr(app, 'set_logger_visible'):
                app.set_logger_visible(active)

            Logger.info(f"Logger-Leiste {'angezeigt' if active else 'ausgeblendet'}")
        except Exception as e:
            Logger.error(f"Fehler beim Umschalten der Logger-Leiste: {e}")

    def toggle_mobile_modus(self, active):
        """Wechselt zwischen horizontalem und vertikalem Menü (ohne Touch-Swipe zu ändern)"""
        try:
            # Config speichern
            config_service = service_container.get_config_service()
            if config_service:
                config_service.set('mobile_modus', active)

            # Menü-Orientierung in der App umschalten
            app = MDApp.get_running_app()
            if app and hasattr(app, 'set_navigation_mode'):
                # Override setzen (manueller Modus)
                app._mobile_modus_override = active if active else None
                app.set_navigation_mode(active)

            Logger.info(f"Vertikales Menü {'aktiviert' if active else 'deaktiviert'}")
        except Exception as e:
            Logger.error(f"Fehler beim Umschalten des Menü-Modus: {e}")

    # ==================== DELEGIERTE METHODEN ====================
    # Alle Methoden delegieren an die entsprechenden Manager/Handler
    
    # Theme-Management (direct delegation to ThemeManager)
    def switch_theme_style(self, style):
        """Delegiert Theme-Stil-Wechsel an ThemeManager"""
        if self.theme_manager:
            return self.theme_manager.switch_theme_style(style)
        else:
            Logger.warning("ThemeManager nicht verfügbar")
    
    def on_color_selected(self, color_name):
        """Delegiert Farbauswahl an ThemeManager"""
        if self.theme_manager:
            return self.theme_manager.on_color_selected(color_name)
        else:
            Logger.warning("ThemeManager nicht verfügbar")
            
    def _on_theme_changed(self, data):
        """Callback für Theme-Änderungen"""
        if self.theme_manager:
            self.theme_manager.update_color_chips()
        else:
            Logger.warning("ThemeManager nicht verfügbar für Theme-Update")
    
    def _on_character_updated(self, data):
        """Callback für Charakter-Änderungen (z.B. Setting-Wechsel)"""
        if self.statistics_manager:
            self.statistics_manager.update_element_statistics_ui()
        else:
            Logger.warning("StatisticsManager nicht verfügbar für Statistik-Update")

    def aktualisiere_ui(self):
        """Aktualisiert die Einstellungen-UI nach Änderungen"""
        if self.statistics_manager:
            self.statistics_manager.update_element_statistics_ui()
        # Layout-Neuberechnung erzwingen (verhindert leere Ansicht nach Tab-Wechsel)
        for child in self.children:
            if hasattr(child, 'do_layout'):
                child.do_layout()

    # Character-Management - Basis-Operationen bleiben hier
    def get_charakter_value(self, attribute, default_value=''):
        """Hilfsmethode zum sicheren Abrufen von Charakter-Attributen"""
        try:
            if self.app.controller and self.app.controller.charakter:
                return str(getattr(self.app.controller.charakter, attribute, default_value))
            return default_value
        except Exception as e:
            Logger.warning(f"Fehler beim Abrufen von {attribute}: {e}")
            return default_value
    
    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Attributsteigerungen-Update")
                return
                
            field_value = self.ids.attributsteigerungen_field.text
            try:
                new_value = int(field_value)
                self.app.controller.charakter.maximale_attributsteigerungen = new_value
                Logger.info(f"Maximale Attributsteigerungen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Attributsteigerungen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Attributsteigerungen: {e}")
    
    def open_log_file(self):
        """Kopiert den Log-Inhalt in die Zwischenablage"""
        try:
            Logger.info("Log-File kopieren wurde aufgerufen")
            
            if not hasattr(self.app, 'log_filepath') or not self.app.log_filepath:
                Logger.warning("Keine Log-Datei verfügbar")
                Logger.warning("ERROR: Log-Datei nicht verfügbar oder Logging deaktiviert.")
                return
            
            log_filepath = self.app.log_filepath
            Logger.info(f"Kopiere Log-Datei in Zwischenablage: {log_filepath}")
            
            # Log-Datei lesen
            try:
                with open(log_filepath, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    
                # Log-Info Header hinzufügen
                header = f"=== Session Log ===\n"
                header += f"Datei: {os.path.basename(log_filepath)}\n"
                header += f"Pfad: {log_filepath}\n"
                header += f"Größe: {len(log_content)} Zeichen\n\n"
                
                full_content = header + log_content
                
                # In Zwischenablage kopieren
                self._copy_to_clipboard(full_content)
                
                # Erfolgs-Nachricht
                lines_count = log_content.count('\n')
                success_msg = f"Log erfolgreich kopiert!\n\n"
                success_msg += f"• {lines_count} Zeilen\n"
                success_msg += f"• {len(log_content)} Zeichen\n"
                success_msg += f"• Datei: {os.path.basename(log_filepath)}\n\n"
                success_msg += f"Der Log-Inhalt ist jetzt in der Zwischenablage und kann in einen Texteditor eingefügt werden."
                
                Logger.info(f"SUCCESS: {success_msg}")
                Logger.info(f"Log-Inhalt erfolgreich in Zwischenablage kopiert ({lines_count} Zeilen)")
                
            except Exception as e:
                Logger.error(f"Fehler beim Lesen der Log-Datei: {e}")
                Logger.error(f"ERROR: Konnte Log-Datei nicht lesen: {str(e)}")
                    
        except Exception as e:
            Logger.error(f"Fehler beim Kopieren der Log-Datei: {e}")
            Logger.error(f"ERROR: Unerwarteter Fehler beim Log-Kopieren: {str(e)}")
    
    def _copy_to_clipboard(self, text):
        """Kopiert Text in die Zwischenablage - plattformspezifisch"""
        try:
            from kivy.utils import platform
            
            if platform == 'android':
                # Android: Kivy Clipboard verwenden + ADB Export
                from kivy.core.clipboard import Clipboard
                Clipboard.copy(text)
                Logger.info("Text über Kivy Clipboard kopiert (Android)")
                
                # Zusätzlich: Log in ADB-zugängliche Datei schreiben
                try:
                    export_file = "/sdcard/savage_worlds_log_export.txt"
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    Logger.info(f"Log auch nach {export_file} exportiert (für ADB-Zugriff)")
                except Exception as e:
                    Logger.warning(f"ADB-Export fehlgeschlagen: {e}")
                
            else:
                # Desktop: System-spezifische Clipboard-Tools verwenden
                try:
                    # Versuche verschiedene Clipboard-Optionen
                    if os.name == 'nt':  # Windows
                        import subprocess
                        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True)
                        process.communicate(text)
                        Logger.info("Text über Windows clip.exe kopiert")
                    elif os.name == 'posix':  # Linux/Mac
                        # Versuche xclip oder pbcopy
                        import subprocess
                        try:
                            subprocess.run(['xclip', '-selection', 'clipboard'], input=text, text=True, check=True)
                            Logger.info("Text über xclip kopiert")
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            try:
                                subprocess.run(['pbcopy'], input=text, text=True, check=True)
                                Logger.info("Text über pbcopy kopiert")
                            except (subprocess.CalledProcessError, FileNotFoundError):
                                # Fallback auf Kivy
                                from kivy.core.clipboard import Clipboard
                                Clipboard.copy(text)
                                Logger.info("Text über Kivy Clipboard kopiert (Linux fallback)")
                    else:
                        # Unbekanntes System - Kivy verwenden
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(text)
                        Logger.info("Text über Kivy Clipboard kopiert (unknown OS)")
                        
                except Exception as e:
                    Logger.warning(f"System-Clipboard fehlgeschlagen, verwende Kivy: {e}")
                    # Fallback auf Kivy Clipboard
                    from kivy.core.clipboard import Clipboard
                    Clipboard.copy(text)
                    Logger.info("Text über Kivy Clipboard kopiert (fallback)")
                    
        except Exception as e:
            Logger.error(f"Fehler beim Kopieren in Zwischenablage: {e}")
            raise
    
    def _show_android_log_info(self, log_filepath):
        """Zeigt Android-spezifische Log-Info ohne Datei-Zugriff"""
        try:
            Logger.info("Zeige Android Log-Info")
            
            # Einfacher Dialog nur mit Pfad-Information
            log_dir = os.path.dirname(log_filepath)
            log_filename = os.path.basename(log_filepath)
            
            message = f"Log-Datei:\n{log_filename}\n\nPfad:\n{log_dir}\n\n"
            message += "So findest du die Log-Datei:\n"
            message += "1. Dateimanager öffnen\n"
            message += "2. 'Interner Speicher' wählen\n" 
            message += "3. Ordner 'SavageWorldsCharGen' suchen\n"
            message += "4. Unterordner 'logs' öffnen\n\n"
            message += "Die Log-Datei zeigt alle Kauf/Verkauf-Transaktionen mit Details."
            
            Logger.info(f"Android Log-Info: {message}")
            
        except Exception as e:
            Logger.error(f"Fehler bei Android Log-Info: {e}")
    
    def _show_log_content_dialog(self, log_filepath):
        """Zeigt den Log-Inhalt in einem scrollbaren Dialog"""
        try:
            # Log-Datei lesen (letzten 200 Zeilen für bessere Performance)
            with open(log_filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Nur die letzten 200 Zeilen anzeigen
                recent_lines = lines[-200:] if len(lines) > 200 else lines
                log_content = ''.join(recent_lines)
            
            # Dialog mit scrollbarem Inhalt
            content = MDBoxLayout(orientation="vertical", spacing="12dp")
            
            # Info-Header
            info_label = MDLabel(
                text=f"Log-Datei: {os.path.basename(log_filepath)}\nPfad: {log_filepath}\nZeilen: {len(recent_lines)}/{len(lines)}",
                size_hint_y=None,
                height="80dp",
                theme_text_color="Secondary",
                halign="left"
            )
            content.add_widget(info_label)
            
            # Scrollbarer Log-Inhalt
            scroll = MDScrollView()
            log_label = MDLabel(
                text=log_content,
                theme_text_color="Primary",
                halign="left",
                valign="top",
                text_size=(None, None),
                font_name='RobotoMono'  # Monospace für bessere Lesbarkeit
            )
            log_label.bind(texture_size=log_label.setter('size'))
            scroll.add_widget(log_label)
            content.add_widget(scroll)
            
            # Dialog erstellen
            dialog = MDDialog(
                title="Log-Datei Inhalt",
                content_cls=content,
                size_hint=(0.9, 0.8),
                buttons=[
                    MDButton(
                        MDButtonText(text="Log-Pfad Info"),
                        on_release=lambda x: self._show_log_path_info(log_filepath)
                    ),
                    MDButton(
                        MDButtonText(text="Schließen"),
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"Fehler beim Lesen der Log-Datei: {e}")
            self._show_error_dialog("Fehler beim Lesen", f"Konnte Log-Datei nicht lesen: {str(e)}")
    
    def _show_log_path_info(self, log_filepath):
        """Zeigt detaillierte Pfad-Informationen für die Log-Datei"""
        from kivy.utils import platform
        
        log_dir = os.path.dirname(log_filepath)
        content_text = f"Log-Datei:\n{log_filepath}\n\nLog-Ordner:\n{log_dir}"
        
        if platform == 'android':
            content_text += "\n\nSo findest du die Logs auf Android:\n"
            content_text += "1. Dateimanager öffnen\n"
            content_text += "2. 'Interner Speicher' wählen\n"
            content_text += "3. Ordner 'SavageWorldsCharGen' suchen\n"
            content_text += "4. Unterordner 'logs' öffnen\n"
            content_text += "\nAlternativer Pfad:\n/sdcard/SavageWorldsCharGen/logs/"
        
        content = MDLabel(
            text=content_text,
            theme_text_color="Primary",
            halign="left",
            valign="top"
        )
        content.bind(texture_size=content.setter('size'))
        
        dialog = MDDialog(
            title="Log-Datei Pfad",
            content_cls=content,
            buttons=[
                MDButton(
                    MDButtonText(text="OK"),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def _show_simple_dialog(self, title, message):
        """Zeigt einen einfachen Dialog"""
        try:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton, MDButtonText
            from kivymd.uix.boxlayout import MDBoxLayout
            
            # Content mit MDBoxLayout umhüllen
            content = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding="12dp"
            )
            
            label = MDLabel(
                text=message,
                theme_text_color="Primary",
                halign="left",
                valign="top",
                text_size=(None, None)
            )
            label.bind(texture_size=label.setter('size'))
            content.add_widget(label)
            
            # Einfacher Dialog ohne veraltete Parameter
            dialog = MDDialog()
            dialog.title = title
            dialog.content_cls = content
            dialog.size_hint = (0.8, None)
            dialog.height = "200dp"
            
            # Button hinzufügen
            from kivymd.uix.button import MDButton, MDButtonText
            ok_button = MDButton(
                MDButtonText(text="OK"),
                on_release=lambda x: dialog.dismiss()
            )
            dialog.add_widget(ok_button)
            
            dialog.open()
            
        except Exception as e:
            # Fallback: Nur Logger verwenden
            Logger.info(f"Dialog-Fallback - {title}: {message}")
            Logger.error(f"Dialog-Error: {e}")
    
    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Fertigkeitssteigerungen-Update")
                return
                
            field_value = self.ids.fertigkeitssteigerungen_field.text
            try:
                new_value = int(field_value)
                self.app.controller.charakter.maximale_fertigkeitssteigerungen = new_value
                Logger.info(f"Maximale Fertigkeitssteigerungen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Fertigkeitssteigerungen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Fertigkeitssteigerungen: {e}")
    
    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Vermögen-Update")
                return
                
            field_value = self.ids.vermoegen_field.text
            try:
                new_value = int(field_value)
                self.app.controller.charakter.vermoegen = new_value
                Logger.info(f"Vermögen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Vermögen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Vermögens: {e}")
    
    def update_waehrung(self):
        """Aktualisiert die Währungseinheit"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Währung-Update")
                return
                
            new_value = self.ids.waehrung_field.text
            self.app.controller.charakter.waehrungseinheit = new_value
            Logger.info(f"Währungseinheit aktualisiert auf: {new_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Währung: {e}")
    
    def _show_warning(self, title, message):
        """Zeigt ein Warn-Popup an"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_info_dialog(message, title)
        else:
            Logger.warning(f"{title}: {message}")

    def erhoehe_startkapital(self):
        """Erhöht das Startkapital mit Handicap-Punkten"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Startkapital-Erhöhung")
                return

            char = self.app.controller.charakter
            if not char:
                return

            if char.verbleibende_handicap_punkte <= 0:
                self._show_warning(
                    "Keine Handicap-Punkte",
                    "Es sind keine Handicap-Punkte verfügbar.\n\n"
                    "Wähle zuerst Handicaps aus, um Punkte zu erhalten, "
                    "die du für zusätzliches Startkapital einsetzen kannst."
                )
                return

            self.app.controller.erhoehe_startkapital_mit_handicap()
            Logger.info("Startkapital mit Handicap-Punkten erhöht")
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Startkapitals: {e}")

    def erhoehe_aufstieg(self):
        """Erhöht die Aufstiege"""
        try:
            if not (self.app.controller and self.app.controller.charakter):
                Logger.warning("Controller oder Charakter nicht verfügbar für Aufstieg-Erhöhung")
                return

            char = self.app.controller.charakter
            if not char.char_gen_completed:
                self._show_warning(
                    "Charaktergenerierung nicht abgeschlossen",
                    "Aufstiege können erst nach Abschluss der Charaktergenerierung "
                    "hinzugefügt werden.\n\n"
                    "Schließe zuerst die Charaktererstellung ab."
                )
                return

            from functions.character_advancement import increase_aufstiege
            increase_aufstiege(char)
            Logger.info("Aufstieg erhöht")
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Aufstiegs: {e}")

    def senke_aufstieg(self):
        """Senkt die Aufstiege"""
        try:
            if not (self.app.controller and self.app.controller.charakter):
                Logger.warning("Controller oder Charakter nicht verfügbar für Aufstieg-Senkung")
                return

            char = self.app.controller.charakter
            if not char.char_gen_completed:
                self._show_warning(
                    "Charaktergenerierung nicht abgeschlossen",
                    "Aufstiege können erst nach Abschluss der Charaktergenerierung "
                    "verändert werden.\n\n"
                    "Schließe zuerst die Charaktererstellung ab."
                )
                return

            if char.verbleibende_aufstiege <= 0 and char.aufstiege_gesamt <= 0:
                self._show_warning(
                    "Kein Abstieg möglich",
                    "Es sind keine Aufstiege vorhanden, die entfernt werden könnten."
                )
                return

            from functions.character_advancement import decrease_aufstiege
            decrease_aufstiege(char)
            Logger.info("Aufstieg gesenkt")
        except Exception as e:
            Logger.error(f"Fehler beim Senken des Aufstiegs: {e}")

    # ==================== MOBILE POPUPS ====================

    def open_punkte_popup(self):
        """Öffnet Popup für Attribut-/Fertigkeitspunkte (Mobile)"""
        try:
            from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
            from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
            from kivymd.uix.button import MDButton, MDButtonText
            from kivymd.uix.label import MDLabel
            from kivy.metrics import dp

            char = self.app.controller.charakter if self.app.controller else None
            attr_val = str(getattr(char, 'maximale_attributsteigerungen', 5)) if char else '5'
            fert_val = str(getattr(char, 'maximale_fertigkeitssteigerungen', 12)) if char else '12'

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(20), padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter('height'))

            # Attribut-Punkte
            attr_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            attr_row.add_widget(MDLabel(
                text="Attributs-Punkte:", size_hint_x=0.6,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_attr_field = MDTextField(
                text=attr_val, mode="outlined",
                size_hint_x=0.4, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            attr_row.add_widget(self._popup_attr_field)
            content.add_widget(attr_row)

            # Fertigkeits-Punkte
            fert_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            fert_row.add_widget(MDLabel(
                text="Fertigkeits-Punkte:", size_hint_x=0.6,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_fert_field = MDTextField(
                text=fert_val, mode="outlined",
                size_hint_x=0.4, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            fert_row.add_widget(self._popup_fert_field)
            content.add_widget(fert_row)

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._punkte_dialog.dismiss(),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Übernehmen"), style="text",
                on_release=lambda x: self._apply_punkte_popup(),
            ))
            content.add_widget(button_row)

            self._punkte_dialog = MDDialog(
                MDDialogHeadlineText(text="Start-Punkte"),
                MDDialogContentContainer(content, orientation="vertical", padding=dp(0)),
                auto_dismiss=False,
            )
            self._punkte_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Punkte-Popups: {e}")

    def _apply_punkte_popup(self):
        """Wendet die Werte aus dem Punkte-Popup an"""
        try:
            self._punkte_dialog.dismiss()
            char = self.app.controller.charakter if self.app.controller else None
            if not char:
                return

            try:
                attr_val = int(self._popup_attr_field.text)
                char.maximale_attributsteigerungen = attr_val
                if 'attributsteigerungen_field' in self.ids:
                    self.ids.attributsteigerungen_field.text = str(attr_val)
            except ValueError:
                pass

            try:
                fert_val = int(self._popup_fert_field.text)
                char.maximale_fertigkeitssteigerungen = fert_val
                if 'fertigkeitssteigerungen_field' in self.ids:
                    self.ids.fertigkeitssteigerungen_field.text = str(fert_val)
            except ValueError:
                pass

            # Button-Text aktualisieren
            if 'punkte_button_text' in self.ids:
                self.ids.punkte_button_text.text = (
                    f"Attr: {char.maximale_attributsteigerungen} / "
                    f"Fert: {char.maximale_fertigkeitssteigerungen}"
                )

            Logger.info(f"Punkte aktualisiert: Attr={char.maximale_attributsteigerungen}, "
                        f"Fert={char.maximale_fertigkeitssteigerungen}")
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden der Punkte: {e}")

    def open_vermoegen_popup(self):
        """Öffnet Popup für Vermögen/Währung (Mobile)"""
        try:
            from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
            from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
            from kivymd.uix.button import MDButton, MDButtonText
            from kivymd.uix.label import MDLabel
            from kivy.metrics import dp

            char = self.app.controller.charakter if self.app.controller else None
            money_val = str(getattr(char, 'vermoegen', 500)) if char else '500'
            currency_val = str(getattr(char, 'waehrungseinheit', 'Gold')) if char else 'Gold'

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(20), padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter('height'))

            # Vermögen
            money_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            money_row.add_widget(MDLabel(
                text="Vermögen:", size_hint_x=0.4,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_money_field = MDTextField(
                text=money_val, mode="outlined",
                size_hint_x=0.6, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            money_row.add_widget(self._popup_money_field)
            content.add_widget(money_row)

            # Währung
            currency_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            currency_row.add_widget(MDLabel(
                text="Währung:", size_hint_x=0.4,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_currency_field = MDTextField(
                text=currency_val, mode="outlined",
                size_hint_x=0.6, size_hint_y=None, height=dp(56),
            )
            currency_row.add_widget(self._popup_currency_field)
            content.add_widget(currency_row)

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._vermoegen_dialog.dismiss(),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Übernehmen"), style="text",
                on_release=lambda x: self._apply_vermoegen_popup(),
            ))
            content.add_widget(button_row)

            self._vermoegen_dialog = MDDialog(
                MDDialogHeadlineText(text="Vermögen & Währung"),
                MDDialogContentContainer(content, orientation="vertical", padding=dp(0)),
                auto_dismiss=False,
            )
            self._vermoegen_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Vermögen-Popups: {e}")

    def _apply_vermoegen_popup(self):
        """Wendet die Werte aus dem Vermögen-Popup an"""
        try:
            self._vermoegen_dialog.dismiss()
            char = self.app.controller.charakter if self.app.controller else None
            if not char:
                return

            try:
                money_val = int(self._popup_money_field.text)
                char.vermoegen = money_val
                if 'vermoegen_field' in self.ids:
                    self.ids.vermoegen_field.text = str(money_val)
            except ValueError:
                pass

            currency_val = self._popup_currency_field.text or 'Gold'
            char.waehrungseinheit = currency_val
            if 'waehrung_field' in self.ids:
                self.ids.waehrung_field.text = currency_val

            # Button-Text aktualisieren
            if 'vermoegen_button_text' in self.ids:
                self.ids.vermoegen_button_text.text = f"{char.vermoegen} {char.waehrungseinheit}"

            Logger.info(f"Vermögen aktualisiert: {char.vermoegen} {char.waehrungseinheit}")
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden des Vermögens: {e}")

    # Game Elements Management (delegiert an GameElementsHandler)
    def open_add_volk_dialog(self):
        """Delegiert Volk-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_volk_dialog()
    
    def open_delete_volk_dialog(self):
        """Delegiert Volk-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_volk_dialog()
    
    def open_add_talent_popup(self):
        """Delegiert Talent-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_talent_popup()
    
    def open_delete_talent_popup(self):
        """Delegiert Talent-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_talent_popup()
    
    def open_add_macht_popup(self):
        """Delegiert Macht-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_macht_popup()
    
    def open_delete_macht_popup(self):
        """Delegiert Macht-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_macht_popup()
    
    def open_add_fertigkeit_popup(self):
        """Delegiert Fertigkeit-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_fertigkeit_popup()
    
    def open_delete_fertigkeit_popup(self):
        """Delegiert Fertigkeit-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_fertigkeit_popup()
    
    def open_add_handicap_popup(self):
        """Delegiert Handicap-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_handicap_popup()
    
    def open_delete_handicap_popup(self):
        """Delegiert Handicap-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_handicap_popup()
    
    def open_add_ausruestung_popup(self):
        """Delegiert Ausrüstung-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_ausruestung_popup()
    
    def open_add_waffe_popup(self):
        """Delegiert Waffen-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_waffe_popup()
    
    def open_add_ruestung_popup(self):
        """Delegiert Rüstung-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_ruestung_popup()
    
    def open_add_schild_popup(self):
        """Delegiert Schild-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_schild_popup()
    
    def open_delete_ausruestung_popup(self):
        """Delegiert Ausrüstung-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_ausruestung_popup()
    
    def open_delete_waffe_popup(self):
        """Delegiert Waffen-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_waffe_popup()
    
    def open_delete_ruestung_popup(self):
        """Delegiert Rüstung-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_ruestung_popup()
    
    def open_delete_schild_popup(self):
        """Delegiert Schild-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_schild_popup()
    
    def open_add_setting_popup(self):
        """Öffnet Dialog zum Hinzufügen von Settings"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_setting_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Setting hinzufügen nicht möglich")
    
    def open_setting_switch_options(self):
        """Delegiert Setting-Wechsel-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_setting_switch_options()

    def open_setting_switch_popup(self):
        """Setting-Wechsel mit Auswahl-Popup (Mobile, Stil wie Neuer-Charakter-Wizard)"""
        try:
            from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
            from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
            from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
            from kivymd.uix.button import MDButton, MDButtonText
            from kivymd.uix.list import MDList
            from kivymd.uix.scrollview import MDScrollView
            from kivy.metrics import dp

            if not (self.app.controller and self.app.controller.charakter):
                self._show_warning("Kein Charakter", "Kein Charakter verfügbar.")
                return

            char = self.app.controller.charakter
            available_settings = char.custom_element_manager.get_all_settings()
            current_setting = char.active_setting_name

            if not available_settings or len(available_settings) <= 1:
                self._show_warning(
                    "Kein Setting-Wechsel möglich",
                    f"Nur ein Setting verfügbar: '{current_setting}'"
                )
                return

            self._switch_pending_setting = current_setting

            # Hauptcontainer
            dialog_content = MDBoxLayout(
                orientation="vertical", spacing=dp(15), padding=dp(20),
                size_hint_y=None,
            )
            dialog_content.bind(minimum_height=dialog_content.setter('height'))

            # Info
            from kivymd.uix.label import MDLabel
            dialog_content.add_widget(MDLabel(
                text=f"Aktuelles Setting: {current_setting}",
                theme_text_color="Secondary", font_style="Body",
                size_hint_y=None, height=dp(30),
            ))

            # Suchfeld
            search_field = MDTextField(
                mode="outlined", size_hint_y=None, height=dp(56), size_hint_x=1
            )
            search_field.add_widget(MDTextFieldHintText(text="Setting suchen..."))
            dialog_content.add_widget(search_field)

            # Scrollbare Liste
            scroll_view = MDScrollView(size_hint=(1, None), height=dp(250))
            scroll_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None))
            items_list = MDList(size_hint_y=None, size_hint_x=1)
            items_list.bind(minimum_height=items_list.setter('height'))
            scroll_layout.add_widget(items_list)
            scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
            scroll_view.add_widget(scroll_layout)
            scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
            dialog_content.add_widget(scroll_view)

            def populate_list(*args):
                items_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                pending = self._switch_pending_setting

                for setting_name in sorted(available_settings):
                    if search_text and search_text not in setting_name.lower():
                        continue
                    is_sel = (pending == setting_name)
                    is_current = (setting_name == current_setting)
                    item = MDListItem(
                        size_hint_y=None, height=dp(48),
                        on_release=lambda x, s=setting_name: _select(s),
                        md_bg_color=self.app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                    )
                    if is_sel:
                        item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                    label_text = f"{setting_name} (aktiv)" if is_current else setting_name
                    headline = MDListItemHeadlineText(text=label_text)
                    if is_sel:
                        headline.bold = True
                    item.add_widget(headline)
                    items_list.add_widget(item)

            def _select(setting_name):
                self._switch_pending_setting = setting_name
                populate_list()

            search_field.bind(text=populate_list)
            populate_list()

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._switch_dialog.dismiss(),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Wechseln"), style="text",
                on_release=lambda x: self._apply_setting_switch(),
            ))
            dialog_content.add_widget(button_row)

            self._switch_dialog = MDDialog(
                MDDialogHeadlineText(text="Setting wechseln"),
                MDDialogContentContainer(dialog_content, orientation="vertical", padding=dp(0)),
                auto_dismiss=False,
            )
            self._switch_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Setting-Wechsel-Popups: {e}")

    def _apply_setting_switch(self):
        """Wendet den Setting-Wechsel aus dem Popup an"""
        try:
            self._switch_dialog.dismiss()
            chosen = getattr(self, '_switch_pending_setting', None)
            if not chosen:
                return

            char = self.app.controller.charakter
            if chosen == char.active_setting_name:
                return

            # Delegiere an GameElementsHandler für Merge-Dialog
            self.game_elements_handler._on_setting_choice_made(chosen)
        except Exception as e:
            Logger.error(f"Fehler beim Setting-Wechsel: {e}")

    def open_delete_setting_popup(self):
        """Öffnet Dialog zum Löschen von Settings"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_setting_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Setting löschen nicht möglich")
    
    # Volk-Dialoge
    def open_add_volk_dialog(self):
        """Öffnet Dialog zum Hinzufügen von Völkern"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_volk_dialog()
        else:
            Logger.warning("DialogService nicht verfügbar - Volk hinzufügen nicht möglich")
    
    def open_delete_volk_dialog(self):
        """Öffnet Dialog zum Löschen von Völkern"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_volk_dialog()
        else:
            Logger.warning("DialogService nicht verfügbar - Volk löschen nicht möglich")
    
    # Talent-Dialoge
    def open_add_talent_popup(self):
        """Öffnet Dialog zum Hinzufügen von Talenten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_talent_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Talent hinzufügen nicht möglich")
    
    def open_delete_talent_popup(self):
        """Öffnet Dialog zum Löschen von Talenten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_talent_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Talent löschen nicht möglich")
    
    # Macht-Dialoge
    def open_add_macht_popup(self):
        """Öffnet Dialog zum Hinzufügen von Mächten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_macht_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Macht hinzufügen nicht möglich")
    
    def open_delete_macht_popup(self):
        """Öffnet Dialog zum Löschen von Mächten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_macht_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Macht löschen nicht möglich")
    
    # Fertigkeit-Dialoge
    def open_add_fertigkeit_popup(self):
        """Öffnet Dialog zum Hinzufügen von Fertigkeiten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_fertigkeit_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Fertigkeit hinzufügen nicht möglich")
    
    def open_delete_fertigkeit_popup(self):
        """Öffnet Dialog zum Löschen von Fertigkeiten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_fertigkeit_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Fertigkeit löschen nicht möglich")
    
    # Handicap-Dialoge
    def open_add_handicap_popup(self):
        """Öffnet Dialog zum Hinzufügen von Handicaps"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_handicap_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Handicap hinzufügen nicht möglich")
    
    def open_delete_handicap_popup(self):
        """Öffnet Dialog zum Löschen von Handicaps"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_handicap_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Handicap löschen nicht möglich")
    
    # Ausrüstung-Dialoge
    def open_add_ausruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen von Ausrüstung"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ausruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Ausrüstung hinzufügen nicht möglich")
    
    def open_delete_ausruestung_popup(self):
        """Öffnet Dialog zum Löschen von Ausrüstung"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_ausruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Ausrüstung löschen nicht möglich")
    
    # Waffen-Dialoge
    def open_add_waffe_popup(self):
        """Öffnet Dialog zum Hinzufügen von Waffen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_waffe_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Waffe hinzufügen nicht möglich")
    
    def open_delete_waffe_popup(self):
        """Öffnet Dialog zum Löschen von Waffen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_waffe_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Waffe löschen nicht möglich")
    
    # Rüstung-Dialoge
    def open_add_ruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen von Rüstungen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Rüstung hinzufügen nicht möglich")
    
    def open_delete_ruestung_popup(self):
        """Öffnet Dialog zum Löschen von Rüstungen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_ruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Rüstung löschen nicht möglich")
    
    # Schild-Dialoge
    def open_add_schild_popup(self):
        """Öffnet Dialog zum Hinzufügen von Schilden"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_schild_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Schild hinzufügen nicht möglich")
    
    def open_delete_schild_popup(self):
        """Öffnet Dialog zum Löschen von Schilden"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_schild_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Schild löschen nicht möglich")

    # ==================== CLEANUP ====================
    
    def on_stop(self):
        """Cleanup beim Beenden"""
        try:
            # Event-Handler entfernen
            event_service = service_container.get_event_service()
            
            if event_service:
                event_service.unsubscribe(EventTypes.THEME_CHANGED, self._on_theme_changed)
            
            Logger.info("EinstellungenWidget bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen: {e}")