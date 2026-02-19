from __future__ import annotations
from ..config.manager import Config, QlcConfig
from pathlib import Path
from typing import List
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)

class QlcPageManager:
    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui
        # Ensure UI label shows current qlc file (or default) and validate existence
        try:
            current_file = getattr(self.config.qlc, 'qlc_file_path', None)
            default_file = QlcConfig().qlc_file_path

            chosen_path = None
            if current_file:
                p = Path(current_file)
                if not p.exists():
                    alt = Path.cwd().parent / p
                    if alt.exists():
                        p = alt

                if not p.exists():
                    # reset to default if the chosen file no longer exists
                    try:
                        self.config.qlc.qlc_file_path = default_file
                        self.config.save()
                        chosen_path = default_file
                        logger.debug('Reset qlc_file_path to default because stored file was missing')
                    except Exception:
                        logger.exception('Failed to reset qlc_file_path to default')
                        chosen_path = default_file
                else:
                    chosen_path = p
            else:
                chosen_path = default_file

            # update UI label
            try:
                self.ui.path_choose_qlc_file_label.setText(str(chosen_path))
            except Exception:
                logger.debug('Failed to set initial qlc file label text')
        except Exception:
            # best-effort: ignore UI errors
            logger.debug('Error while validating initial qlc file')

        # Connect the choose button to open a file dialog for .qxw files
        try:
            from PySide6.QtWidgets import QFileDialog

            def _choose_qlc_file() -> None:
                start_dir = Path(getattr(self.config.qlc, 'qlc_folder_path', Path('./')))
                # If configured path doesn't exist, try relative lookup
                if not start_dir.exists():
                    alt = Path.cwd().parent / start_dir
                    if alt.exists():
                        start_dir = alt

                file_path, _ = QFileDialog.getOpenFileName(self.main_window,
                                                           "Choisir un fichier QLC+ (.qxw)",
                                                           str(start_dir),
                                                           "QLC+ Project (*.qxw)")
                if file_path:
                    p = Path(file_path)
                    # Save both folder and file path to config
                    try:
                        self.config.qlc.qlc_folder_path = p.parent
                        self.config.qlc.qlc_file_path = p
                        # Persist config (will exclude secrets as implemented)
                        self.config.save()
                    except Exception:
                        logger.exception("Failed to update config with chosen qlc file")

                    try:
                        self.ui.path_choose_qlc_file_label.setText(str(p))
                    except Exception as e:
                        logger.debug('Failed to set qlc file label to chosen file: %s', e)
                else:
                    # No selection: show configured file path fallback
                    try:
                        self.ui.path_choose_qlc_file_label.setText(str(getattr(self.config.qlc, 'qlc_file_path', '')))
                    except Exception as e:
                        logger.debug('Failed to set qlc file label fallback: %s', e)

            # connect signal
            try:
                self.ui.choose_qlc_file_button.clicked.connect(_choose_qlc_file)
            except Exception as e:
                # UI element may not exist in some contexts
                logger.debug("choose_qlc_file_button not available to connect: %s", e)
        except Exception:
            logger.debug("PySide6 not available or QFileDialog import failed")

        # Connect the run button to start qlcplus with the chosen file
        try:
            def _run_qlc() -> None:
                # Determine file to open: prefer configured file path, else qlc_file_path default
                fp = getattr(self.config.qlc, 'qlc_file_path', None)
                if not fp:
                    # nothing configured
                    if hasattr(self.main_window, 'set_log_text'):
                        self.main_window.set_log_text('Aucun fichier QLC configuré à lancer')
                    logger.debug('No qlc_file_path configured')
                    return

                path = Path(fp)
                if not path.exists():
                    # try resolving relative to project root (one level up from src)
                    alt = Path.cwd().parent / path
                    if alt.exists():
                        path = alt

                if not path.exists():
                    if hasattr(self.main_window, 'set_log_text'):
                        self.main_window.set_log_text(f'Fichier QLC introuvable: {path}')
                    logger.debug('QLC file does not exist: %s', path)
                    return

                exe = '/usr/bin/qlcplus'
                # allow system PATH fallback
                if not Path(exe).exists():
                    found = shutil.which('qlcplus')
                    if found:
                        exe = found

                if not Path(exe).exists():
                    if hasattr(self.main_window, 'set_log_text'):
                        self.main_window.set_log_text(f'Executable qlcplus introuvable: {exe}')
                    logger.debug('qlcplus executable not found')
                    return

                cmd = [exe, '--operate', '--overscan', '--open', str(path)]
                try:
                    subprocess.Popen(cmd)
                    logger.debug('Launched qlcplus: %s', cmd)
                except Exception as e:
                    logger.exception('Failed to launch qlcplus')
                    if hasattr(self.main_window, 'set_log_text'):
                        self.main_window.set_log_text(f'Erreur lancement qlcplus: {e}')

            try:
                self.ui.run_qlc_button.clicked.connect(_run_qlc)
            except Exception as e:
                logger.debug('run_qlc_button not available to connect: %s', e)
        except Exception:
            logger.debug('Failed to set up run_qlc_button handler')

