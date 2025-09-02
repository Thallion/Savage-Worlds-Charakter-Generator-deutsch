# views/element_dialog_manager.py
"""
Element Dialog Manager für Einstellungen-Widget
Kapselt alle Element-Dialog-bezogenen Funktionalitäten
"""

from kivy.logger import Logger
from services.service_container import service_container


class ElementDialogManager:
    """Manager für Element-Dialog-Funktionalitäten"""
    
    def __init__(self, widget):
        self.widget = widget
        self.dialog_service = service_container.get_dialog_service()
    
    def _ensure_dialog_service(self):
        """Stellt sicher, dass der Dialog-Service verfügbar ist"""
        if not self.dialog_service:
            Logger.error("Dialog-Service nicht verfügbar")
            return False
        return True
    
    # Setting-Dialoge
    def open_add_setting_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_setting_popup()
    
    def open_delete_setting_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_setting_popup()
    
    # Volk-Dialoge
    def open_add_volk_dialog(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_volk_dialog()
    
    def open_delete_volk_dialog(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_volk_dialog()
    
    # Talent-Dialoge
    def open_add_talent_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_talent_popup()
    
    def open_delete_talent_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_talent_popup()
    
    # Macht-Dialoge
    def open_add_macht_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_macht_popup()
    
    def open_delete_macht_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_macht_popup()
    
    # Fertigkeit-Dialoge
    def open_add_fertigkeit_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_fertigkeit_popup()
    
    def open_delete_fertigkeit_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_fertigkeit_popup()
    
    # Handicap-Dialoge
    def open_add_handicap_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_handicap_popup()
    
    def open_delete_handicap_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_handicap_popup()
    
    # Ausrüstung-Dialoge
    def open_add_ausruestung_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_ausruestung_popup()
    
    def open_delete_ausruestung_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_ausruestung_popup()
    
    # Waffen-Dialoge
    def open_add_waffe_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_waffe_popup()
    
    def open_delete_waffe_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_waffe_popup()
    
    # Rüstung-Dialoge
    def open_add_ruestung_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_ruestung_popup()
    
    def open_delete_ruestung_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_ruestung_popup()
    
    # Schild-Dialoge
    def open_add_schild_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_add_schild_popup()
    
    def open_delete_schild_popup(self):
        if self._ensure_dialog_service():
            self.dialog_service.open_delete_schild_popup()