# views/handlers/game_elements_handler.py
"""
Game Elements Handler für EinstellungenWidget
Behandelt Setting-Management und Element-Dialoge
"""

from kivy.logger import Logger
from services.service_container import service_container


class GameElementsHandler:
    """Handler für Game Elements und Setting Management"""
    
    def __init__(self, widget):
        self.widget = widget
        self.app = widget.app
        
    @property
    def charakter_controller(self):
        """Getter für CharakterController"""
        return getattr(self.app, 'controller', None)
    
    def _trigger_ui_refresh(self):
        """Triggert UI-Refresh über Event-System"""
        event_service = service_container.get_event_service()
        if event_service:
            from services.event_service import EventTypes
            event_service.publish(EventTypes.CHARACTER_UPDATED, {})
    
    # ==================== SETTING MANAGEMENT ====================
    
    def open_setting_switch_options(self):
        """KORRIGIERT: Setting-Wechsel mit Merge-Dialog"""
        if not self.charakter_controller or not self.charakter_controller.charakter:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog("Kein Charakter verfügbar.")
            return
        
        # Verfügbare Settings direkt über den Charakter abrufen
        char = self.charakter_controller.charakter
        available_settings = char.custom_element_manager.get_all_settings()
        current_setting = char.active_setting_name
        
        if not available_settings or len(available_settings) <= 1:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_info_dialog(
                    f"Nur ein Setting verfügbar: '{current_setting}'",
                    "Kein Setting-Wechsel möglich"
                )
            return
        
        # Setting-Auswahl
        setting_choices = []
        for setting_name in available_settings:
            if setting_name != current_setting:
                setting_choices.append((setting_name, setting_name))
        
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            message = f"Aktuelles Setting: {current_setting}\n\nWähle ein neues Setting:"
            dialog_service.show_choice_dialog(
                message,
                "Setting wechseln", 
                setting_choices,
                self._on_setting_choice_made
            )
    
    def _on_setting_choice_made(self, chosen_setting):
        """KORRIGIERT: Verarbeitet die Setting-Auswahl mit Merge-Dialog"""
        if not chosen_setting or not self.charakter_controller or not self.charakter_controller.charakter:
            return
        
        char = self.charakter_controller.charakter
        if chosen_setting == char.active_setting_name:
            return
        
        # HIER IST DIE KORREKTUR: Jetzt wird der Setting-Merge-Dialog verwendet
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            # Verwende die show_setting_merge_dialog Methode
            dialog_service.show_setting_merge_dialog(
                chosen_setting,
                lambda merge_choice: self._apply_setting_change(chosen_setting, merge_choice)
            )
    
    def _apply_setting_change(self, setting_name, merge_choice):
        """
        Wendet den Setting-Wechsel mit der gewählten Merge-Option an
        
        Args:
            setting_name (str): Name des neuen Settings
            merge_choice (str): 'merge' oder 'replace'
        """
        if not self.charakter_controller or not self.charakter_controller.charakter:
            return
        
        char = self.charakter_controller.charakter
        merge_elements = (merge_choice == "merge")
        
        Logger.info(f"Setting-Wechsel zu '{setting_name}' mit Merge-Option: {merge_elements}")
        
        # Setting wechseln mit der gewählten Option
        success = char.change_active_setting(setting_name, merge_elements=merge_elements)
        
        dialog_service = service_container.get_dialog_service()
        if success and dialog_service:
            merge_text = "zusammengeführt" if merge_elements else "komplett ersetzt"
            dialog_service.show_success_dialog(
                f"Setting erfolgreich zu '{setting_name}' gewechselt.\nElemente wurden {merge_text}.",
                "Setting gewechselt"
            )
            self._trigger_ui_refresh()
        elif dialog_service:
            dialog_service.show_error_dialog(f"Fehler beim Wechseln zu Setting '{setting_name}'.")

    # ==================== ELEMENT DIALOGS STUBS ====================
    # Diese wurden zu ElementDialogManager verschoben, hier nur Stubs für Kompatibilität
    
    def open_add_setting_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Setting hinzufügen - Stub aufgerufen")
    
    def open_delete_setting_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Setting löschen - Stub aufgerufen")
        
    def open_add_volk_dialog(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Volk hinzufügen - Stub aufgerufen")
        
    def open_delete_volk_dialog(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Volk löschen - Stub aufgerufen")
        
    def open_add_talent_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Talent hinzufügen - Stub aufgerufen")
        
    def open_delete_talent_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Talent löschen - Stub aufgerufen")
        
    def open_add_macht_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Macht hinzufügen - Stub aufgerufen")
        
    def open_delete_macht_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Macht löschen - Stub aufgerufen")
        
    def open_add_fertigkeit_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Fertigkeit hinzufügen - Stub aufgerufen")
        
    def open_delete_fertigkeit_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Fertigkeit löschen - Stub aufgerufen")
        
    def open_add_handicap_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Handicap hinzufügen - Stub aufgerufen")
        
    def open_delete_handicap_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Handicap löschen - Stub aufgerufen")
        
    def open_add_ausruestung_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Ausrüstung hinzufügen - Stub aufgerufen")
        
    def open_delete_ausruestung_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Ausrüstung löschen - Stub aufgerufen")
        
    def open_add_waffe_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Waffe hinzufügen - Stub aufgerufen")
        
    def open_delete_waffe_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Waffe löschen - Stub aufgerufen")
        
    def open_add_ruestung_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Rüstung hinzufügen - Stub aufgerufen")
        
    def open_delete_ruestung_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Rüstung löschen - Stub aufgerufen")
        
    def open_add_schild_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Schild hinzufügen - Stub aufgerufen")
        
    def open_delete_schild_popup(self):
        """Stub - echte Implementierung in ElementDialogManager"""
        Logger.info("Schild löschen - Stub aufgerufen")