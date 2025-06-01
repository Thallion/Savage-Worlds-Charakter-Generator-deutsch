# utils/app_integration.py
"""
Kompatibilitäts-Hilfsfunktionen für die App-Integration
Behandelt Legacy-Zugriffe auf Widgets über die App-Instanz
"""

from kivy.app import App
from kivy.logger import Logger


def get_einstellungen_widget():
    """
    Sichere Methode zum Abrufen des Einstellungen-Widgets
    
    Returns:
        EinstellungenWidget oder None
    """
    try:
        app = App.get_running_app()
        if app and hasattr(app, 'einstellungen_widget'):
            return app.einstellungen_widget
        
        # Fallback: Suche in den Screens
        if app and hasattr(app, 'screens'):
            for screen_name, screen in app.screens.items():
                if 'Einstellungen' in screen_name:
                    return screen
        
        # Letzter Fallback: Suche in Tab-Definitionen
        if app and hasattr(app, 'tab_definitions'):
            for i, (icon, name, screen_class) in enumerate(app.tab_definitions):
                if name == 'Einstellungen' and hasattr(app.root, 'ids'):
                    carousel = app.root.ids.get('tabs_carousel')
                    if carousel and i < len(carousel.slides):
                        return carousel.slides[i]
        
        Logger.warning("EinstellungenWidget nicht gefunden")
        return None
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen des EinstellungenWidgets: {str(e)}")
        return None


def update_einstellungen_ui():
    """
    Sichere Methode zum Aktualisieren der Einstellungen-UI
    """
    try:
        einstellungen_widget = get_einstellungen_widget()
        if einstellungen_widget and hasattr(einstellungen_widget, 'aktualisiere_ui'):
            einstellungen_widget.aktualisiere_ui()
            Logger.debug("Einstellungen-UI aktualisiert")
            return True
        else:
            Logger.warning("Einstellungen-UI konnte nicht aktualisiert werden")
            return False
    except Exception as e:
        Logger.error(f"Fehler beim Aktualisieren der Einstellungen-UI: {str(e)}")
        return False


def register_widget_with_app(widget, widget_name):
    """
    Registriert ein Widget bei der App-Instanz
    
    Args:
        widget: Das zu registrierende Widget
        widget_name (str): Name des Widget-Attributs
    """
    try:
        app = App.get_running_app()
        if app:
            setattr(app, widget_name, widget)
            Logger.debug(f"Widget '{widget_name}' bei App registriert")
        else:
            Logger.warning("App-Instanz nicht verfügbar")
    except Exception as e:
        Logger.error(f"Fehler beim Registrieren des Widgets: {str(e)}")


# Kompatibilitätsmethoden für alte Code-Teile
def safe_app_access(attr_name, default=None):
    """
    Sicherer Zugriff auf App-Attribute
    
    Args:
        attr_name (str): Name des Attributs
        default: Standardwert falls Attribut nicht existiert
        
    Returns:
        Attributwert oder Standardwert
    """
    try:
        app = App.get_running_app()
        if app and hasattr(app, attr_name):
            return getattr(app, attr_name)
        return default
    except Exception as e:
        Logger.error(f"Fehler beim App-Zugriff auf '{attr_name}': {str(e)}")
        return default


# Monkey-Patch für bessere Fehlerbehandlung
def patch_app_widget_access():
    """
    Patch für die App-Klasse, um bessere Fehlerbehandlung zu bieten
    """
    app = App.get_running_app()
    if not app:
        return
    
    # Original __getattr__ sichern falls vorhanden
    original_getattr = getattr(app.__class__, '__getattr__', None)
    
    def safe_getattr(self, name):
        """Sichere Version von __getattr__ mit Logging"""
        try:
            if original_getattr:
                return original_getattr(self, name)
            else:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        except AttributeError as e:
            Logger.warning(f"App-Attribut '{name}' nicht gefunden: {str(e)}")
            
            # Spezielle Behandlung für bekannte Widget-Attribute
            if name.endswith('_widget'):
                Logger.info(f"Suche nach Widget '{name}' in alternativen Quellen...")
                return None
            
            raise e
    
    # Patch anwenden
    app.__class__.__getattr__ = safe_getattr
    Logger.debug("App-Widget-Access Patch angewendet")


# Automatischer Patch beim Import
try:
    patch_app_widget_access()
except Exception as e:
    Logger.warning(f"Konnte App-Patch nicht anwenden: {str(e)}")