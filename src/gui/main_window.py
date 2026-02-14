from ..config.manager import Config
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMainWindow
from .setup_page_manager import SetupPageManager
from .home_page_manager import HomePageManager
from .plan_page_manager import PlanPageManager
from .measurement_page_managment import MeasurementPageManager
from .Ui_MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):

    """Fenêtre principale avec gestion des signaux et slots."""

    def __init__(self, config: Config | None = None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.config = config

        # Appliquer la taille de fenêtre depuis la config si disponible
        if config is not None:
            try:
                if getattr(config, "screen_width", None) and getattr(config, "screen_height", None):
                    self.resize(int(config.screen_width), int(config.screen_height))
            except Exception:
                pass

        # Connecter les boutons de la barre latérale aux pages correspondantes
        try:
            self.ui.home_button.clicked.connect(lambda: self.ui.main_frame.setCurrentWidget(self.ui.home_page))
            self.ui.plan_button.clicked.connect(lambda: self.ui.main_frame.setCurrentWidget(self.ui.plan_page))
            self.ui.measurement_button.clicked.connect(lambda: self.ui.main_frame.setCurrentWidget(self.ui.measurement_page))
            self.ui.cam_button.clicked.connect(lambda: self.ui.main_frame.setCurrentWidget(self.ui.cam_page))
            self.ui.qlc_button.clicked.connect(lambda: self.ui.main_frame.setCurrentWidget(self.ui.qlc_page))
            self.ui.setup_button.clicked.connect(lambda: self.ui.main_frame.setCurrentWidget(self.ui.setup_page))
        except Exception:
            pass

        # Charger l'image de la page d'accueil: `head_img` sinon `default_img`.
        try:
            self.cfg = self.config if self.config is not None else Config.load_default()
            self.head_path = Path(self.cfg.head_img)
            self.default_path = Path(self.cfg.default_img)
        except Exception:
            pass

        # Affichage de la date et l'heure dans le time label
        try:
            self._update_time_label()
            self._timer_time = QTimer(self)
            self._timer_time.timeout.connect(self._update_time_label)
            self._timer_time.start(1000)
        except Exception as e:
            self.set_log_text(f"Erreur timer horloge: {e}")

        # Initialiser la gestion de la home_page
        try:
            self.home_page_manager = HomePageManager(self, self.cfg)
        except Exception as e:
            self.set_log_text(f"Erreur home_page: {e}")

        # Initialiser la gestion des plans (thumbnails et affichage plein écran)
        try:
            self.plan_page_manager = PlanPageManager(self, self.cfg)
        except Exception as e:
            self.set_log_text(f"Erreur plan_page: {e}")

        # Initialiser la gestion de la measurement_page
        try:
            self.measurement_page_manager = MeasurementPageManager(self, self.cfg)
        except Exception as e:
            self.set_log_text(f"Erreur measurement_page: {e}")

        # Initialiser la gestion de la setup_page
        try:
            self.setup_page_manager = SetupPageManager(self, self.cfg)
        except Exception as e:
            self.set_log_text(f"Erreur setup_page: {e}")
        
    def _update_time_label(self):
        try:
            now = QDateTime.currentDateTime()
            label = getattr(self.ui, "time_label", None)
            if label is not None:
                label.setText(now.toString("dd/MM/yyyy HH:mm:ss"))
        except Exception:
            pass


    def set_log_text(self, text: str) -> None:
        """Place le texte dans la zone de log de la barre de statut."""
        try:
            if hasattr(self.ui, "log") and self.ui.log is not None:
                self.ui.log.setText(str(text))
        except Exception:
            # Ne pas faire planter l'application si le widget est absent
            pass

