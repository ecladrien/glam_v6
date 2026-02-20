import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow
from .utils.logging_config import setup_logging
from .config.manager import Config
from .gui.main_window import MainWindow
from .gui.ui_Splash_screen import Ui_SplashScreen


class SplashScreenWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)


def _create_splash(config: Config) -> SplashScreenWindow:
    project_root = Path(__file__).resolve().parents[1]
    splash_candidates = [
        project_root / "ressources" / "img" / "splashscreen.png",
        Path(config.paths.default_img),
    ]

    pixmap = QPixmap()
    for candidate in splash_candidates:
        if candidate.exists() and pixmap.load(str(candidate)):
            break

    splash = SplashScreenWindow()
    if not pixmap.isNull():
        splash.ui.splashscreen_img.setScaledContents(True)
        splash.ui.splashscreen_img.setPixmap(pixmap)
    splash.ui.please_wait_label.setText("Démarrage de GLAM...")
    return splash


def _apply_dialog_dark_theme(app: QApplication) -> None:
    dialog_style = """
QMessageBox, QDialog, QFileDialog {
    background-color: #1e1e1e;
    color: #ffffff;
}
QMessageBox QLabel, QDialog QLabel, QFileDialog QLabel {
    color: #ffffff;
}
QMessageBox QPushButton, QDialog QPushButton, QFileDialog QPushButton {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444444;
    padding: 4px 10px;
}
QMessageBox QPushButton:hover, QDialog QPushButton:hover, QFileDialog QPushButton:hover {
    background-color: #3a3a3a;
}
QFileDialog QLineEdit, QFileDialog QListView, QFileDialog QTreeView, QFileDialog QComboBox {
    background-color: #252526;
    color: #ffffff;
    selection-background-color: #3f3f46;
    border: 1px solid #3f3f46;
}
"""
    app.setStyleSheet(f"{app.styleSheet()}\n{dialog_style}")


def main() -> None:
    logger = setup_logging("glam.app")
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
        # Initialiser l'application Qt
        app = QApplication(sys.argv)
        _apply_dialog_dark_theme(app)

        config = Config.load_default()
        logger.info("GLAM starting")
        
        # Lire le mode plein écran depuis la configuration
        fullscreen_mode = config.display.fullscreen
        if fullscreen_mode:
            logger.info("Plein écran activé (depuis config)")

        splash = _create_splash(config)
        splash.show()
        app.processEvents()
        splash.ui.please_wait_label.setText("Chargement de la fenêtre principale...")
        app.processEvents()

        # Créer la fenêtre principale en lui passant la config si possible
        try:
            window = MainWindow(config, fullscreen=fullscreen_mode)
        except TypeError:
            window = MainWindow()

        if fullscreen_mode:
            window.showFullScreen()
        else:
            window.show()
        splash.close()

        logger.info("GUI window displayed")
        window.set_log_text("GLAM started successfully")

        # Lancer la boucle d'événements Qt et retourner le code de sortie
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
        sys.exit(exit_code)
    except Exception:
        logger.exception("Unhandled exception during application startup")
        sys.exit(1)


if __name__ == "__main__":
    main()
