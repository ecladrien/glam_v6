from ..config.manager import Config
from PySide6.QtWidgets import QLineEdit, QPushButton

class SetupPageManager:
    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui
        self._connect_buttons()
        self.load_config_to_fields()

    def load_config_to_fields(self):
        self.ui.width_screen_line_edit.setText(str(self.config.screen_width))
        self.ui.height_screen_line_edit.setText(str(self.config.screen_height))
        self.ui.adress_ip_line_edit.setText(str(getattr(self.config, 'device_ip', '')))
        self.ui.adress_ip_cam_line_edit.setText(str(getattr(self.config, 'camera_ip', '')))
        self.ui.adress_ip_artnet_line_edit.setText(str(getattr(self.config, 'artnet_network', '')))

    def save_fields_to_config(self):
        try:
            self.config.screen_width = int(self.ui.width_screen_line_edit.text())
            self.config.screen_height = int(self.ui.height_screen_line_edit.text())
            self.config.device_ip = self.ui.adress_ip_line_edit.text()
            self.config.camera_ip = self.ui.adress_ip_cam_line_edit.text()
            self.config.artnet_network = self.ui.adress_ip_artnet_line_edit.text()
            self.config.save()
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text('Configuration sauvegardée.')
        except Exception as e:
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur lors de la sauvegarde: {e}')

    def reset_to_default(self):
        default_config = Config()
        self.config.screen_width = default_config.screen_width
        self.config.screen_height = default_config.screen_height
        self.config.device_ip = default_config.device_ip
        self.config.camera_ip = default_config.camera_ip
        self.config.artnet_network = default_config.artnet_network
        self.load_config_to_fields()
        if hasattr(self.main_window, 'set_log_text'):
            self.main_window.set_log_text('Valeurs par défaut restaurées (non sauvegardées).')

    def _connect_buttons(self):
        self.ui.save_setup_button.clicked.connect(self.save_fields_to_config)
        self.ui.reset_setup_button.clicked.connect(self.reset_to_default)
