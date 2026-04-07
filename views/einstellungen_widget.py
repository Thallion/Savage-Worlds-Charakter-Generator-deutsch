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

            # Orientierung fixieren Switch
            orientation_locked = config_service.get('screen_orientation_locked', False)
            lock_switch = self.ids.get('orientation_lock_switch')
            if lock_switch:
                lock_switch.unbind(on_active=None)
                lock_switch.active = orientation_locked
                Logger.debug(f"Orientierung-Lock Switch initialisiert: {orientation_locked}")

            # Orientierung Segmented Button
            screen_orientation = config_service.get('screen_orientation', 'auto')
            self._init_orientation_segment(screen_orientation)

            # Orientierung-Auswahl nur bei fixiert sichtbar machen
            self._update_orientation_choice_visibility(orientation_locked)

            # Desktop-Skalierung Slider initialisieren
            self._init_scale_slider(config_service)
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren der UI-Switches: {e}")

    def _init_orientation_segment(self, orientation):
        """Initialisiert den Orientierung-SegmentedButton aus der Config"""
        try:
            segment = self.ids.get('orientation_segment')
            if not segment:
                return
            # Aktuellen Zustand in den Segment-Buttons markieren
            # Die Segmente werden über on_release gesteuert
            Logger.debug(f"Orientierung-Segment initialisiert: {orientation}")
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren des Orientierung-Segments: {e}")

    def _update_orientation_choice_visibility(self, locked):
        """Zeigt/versteckt die Orientierungs-Auswahl je nach Lock-Status"""
        try:
            choice_box = self.ids.get('orientation_choice_box')
            if choice_box:
                if locked:
                    choice_box.height = choice_box.minimum_height if hasattr(choice_box, 'minimum_height') else self._orientation_choice_height
                    choice_box.opacity = 1
                    choice_box.disabled = False
                else:
                    # Höhe merken für späteres Einblenden
                    if hasattr(choice_box, 'minimum_height') and choice_box.height > 0:
                        self._orientation_choice_height = choice_box.height
                    choice_box.height = 0
                    choice_box.opacity = 0
                    choice_box.disabled = True
        except Exception as e:
            Logger.error(f"Fehler bei Orientierung-Sichtbarkeit: {e}")

    def _init_scale_slider(self, config_service):
        """Initialisiert den Skalierungs-Slider aus der Config"""
        try:
            scale_factor = config_service.get('desktop_scale_factor', 'auto')
            slider = self.ids.get('scale_slider')
            label = self.ids.get('scale_label')
            if not slider or not label:
                return

            self._scale_slider_programmatic = True
            if scale_factor == 'auto' or scale_factor is None:
                # Aktuellen Wert aus Environment anzeigen
                import os
                current = float(os.environ.get('KIVY_METRICS_DENSITY', '1.0'))
                slider.value = current
                label.text = f'Auto ({current}x)'
                self._scale_is_auto = True
            else:
                try:
                    val = float(scale_factor)
                    slider.value = val
                    label.text = f'{val}x'
                    self._scale_is_auto = False
                except (ValueError, TypeError):
                    slider.value = 1.0
                    label.text = 'Auto'
                    self._scale_is_auto = True
            self._scale_slider_programmatic = False
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren des Skalierungs-Sliders: {e}")

    def on_scale_slider_changed(self, value):
        """Callback wenn der Skalierungs-Slider verändert wird"""
        if getattr(self, '_scale_slider_programmatic', False):
            return
        try:
            value = round(value, 1)
            label = self.ids.get('scale_label')
            if label:
                label.text = f'{value}x'

            config_service = service_container.get_config_service()
            if config_service:
                config_service.set('desktop_scale_factor', value)
            self._scale_is_auto = False
            Logger.info(f"UI-Skalierung auf {value}x gesetzt (Neustart erforderlich)")
        except Exception as e:
            Logger.error(f"Fehler beim Setzen der Skalierung: {e}")

    def reset_scale_to_auto(self):
        """Setzt die Skalierung auf automatische Erkennung zurück"""
        try:
            config_service = service_container.get_config_service()
            if config_service:
                config_service.set('desktop_scale_factor', 'auto')

            import os
            current = float(os.environ.get('KIVY_METRICS_DENSITY', '1.0'))

            self._scale_slider_programmatic = True
            slider = self.ids.get('scale_slider')
            label = self.ids.get('scale_label')
            if slider:
                slider.value = current
            if label:
                label.text = f'Auto ({current}x)'
            self._scale_is_auto = True
            self._scale_slider_programmatic = False
            Logger.info("UI-Skalierung auf Auto zurückgesetzt (Neustart erforderlich)")
        except Exception as e:
            Logger.error(f"Fehler beim Zurücksetzen der Skalierung: {e}")

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

    def toggle_orientation_lock(self, active):
        """Wechselt zwischen fixierter und flexibler Bildschirm-Orientierung"""
        try:
            config_service = service_container.get_config_service()
            if config_service:
                config_service.set('screen_orientation_locked', active)

            # Orientierungs-Auswahl ein-/ausblenden
            self._update_orientation_choice_visibility(active)

            # Orientierung anwenden
            app = MDApp.get_running_app()
            if app and hasattr(app, 'set_screen_orientation'):
                orientation = 'auto'
                if config_service:
                    orientation = config_service.get('screen_orientation', 'auto')
                app.set_screen_orientation(orientation, active)

            Logger.info(f"Orientierung {'fixiert' if active else 'flexibel (System)'}")
        except Exception as e:
            Logger.error(f"Fehler beim Umschalten der Orientierungs-Sperre: {e}")

    def set_orientation(self, orientation):
        """Setzt die bevorzugte Bildschirm-Orientierung (portrait/landscape)"""
        try:
            config_service = service_container.get_config_service()
            if config_service:
                config_service.set('screen_orientation', orientation)

            # Nur anwenden wenn fixiert
            locked = False
            if config_service:
                locked = config_service.get('screen_orientation_locked', False)

            app = MDApp.get_running_app()
            if app and hasattr(app, 'set_screen_orientation'):
                app.set_screen_orientation(orientation, locked)

            labels = {'portrait': 'Portrait', 'landscape': 'Landscape', 'auto': 'Auto'}
            Logger.info(f"Orientierung auf {labels.get(orientation, orientation)} gesetzt")
        except Exception as e:
            Logger.error(f"Fehler beim Setzen der Orientierung: {e}")

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
                ],
                auto_dismiss=False,
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
            ],
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        dialog.open()
    
    def _show_simple_dialog(self, title, message):
        """Zeigt einen einfachen Dialog"""
        try:
            from kivymd.uix.dialog import (
                MDDialog, MDDialogHeadlineText, MDDialogContentContainer,
                MDDialogButtonContainer
            )
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton, MDButtonText

            dialog = MDDialog(
                MDDialogHeadlineText(text=title),
                MDDialogContentContainer(
                    MDLabel(
                        text=message,
                        theme_text_color="Primary",
                        halign="left",
                    ),
                    orientation="vertical",
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="OK"),
                        style="text",
                        on_release=lambda x: dialog.dismiss(),
                    ),
                    spacing="8dp",
                ),
                size_hint=(0.85, None),
                auto_dismiss=True,
            )
            dialog.open()

        except Exception as e:
            # Fallback: Nur Logger verwenden
            Logger.info(f"Dialog-Fallback - {title}: {message}")
            Logger.error(f"Dialog-Error: {e}")
    

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
    
    # ==================== Tutorial ====================
    
    def open_tutorial(self):
        """Startet das Tutorial (setzt Hilfetexte automatisch zurück)."""
        try:
            from views.tutorial_overlay import show_welcome_tutorial
            show_welcome_tutorial(force=True)
        except Exception as e:
            Logger.error(f"Fehler beim Starten des Tutorials: {e}")

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