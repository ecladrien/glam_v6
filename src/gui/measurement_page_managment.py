from ..config.manager import Config
from ..hardware.arduino_controller import ArduinoController
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen
from collections import deque
import shutil
import logging
from pathlib import Path
import csv

logger = logging.getLogger(__name__)


class MeasurementPageManager:
    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui

        # Create or accept an Arduino controller instance
        try:
            self.arduino = ArduinoController(config=self.config)
        except Exception:
            self.arduino = ArduinoController()

        # Wire UI buttons if present
        try:
            if hasattr(self.ui, 'measurement_start_button'):
                self.ui.measurement_start_button.clicked.connect(self._on_start)
            if hasattr(self.ui, 'measurement_stop_button'):
                self.ui.measurement_stop_button.clicked.connect(self._on_stop)
            if hasattr(self.ui, 'measurement_savegraph_button'):
                self.ui.measurement_savegraph_button.clicked.connect(self._on_save_graph)
            if hasattr(self.ui, 'measurement_reset_button'):
                self.ui.measurement_reset_button.clicked.connect(self._on_reset)
        except Exception as e:
            logger.exception("Erreur liaison boutons measurement: %s", e)

        # Poll Arduino values periodically and update UI
        try:
            self._timer = QTimer(self.main_window)
            self._timer.timeout.connect(self._poll_values)
            self._timer.start(1000)
        except Exception:
            pass

        # Graph buffers (rolling) and initialization
        try:
            self._max_points = 200
            self._buf_neutre = deque([0.0] * self._max_points, maxlen=self._max_points)
            self._buf_p1 = deque([0.0] * self._max_points, maxlen=self._max_points)
            self._buf_p2 = deque([0.0] * self._max_points, maxlen=self._max_points)
            self._buf_p3 = deque([0.0] * self._max_points, maxlen=self._max_points)
        except Exception:
            self._buf_neutre = deque()
            self._buf_p1 = deque()
            self._buf_p2 = deque()
            self._buf_p3 = deque()

    def _poll_values(self):
        try:
            vals = None
            try:
                # Prefer latest cached values from controller
                vals = self.arduino.get_latest_values()
            except Exception:
                try:
                    vals = self.arduino.read_values()
                except Exception:
                    vals = None

            if not vals:
                return

            # Update UI labels if present
            try:
                neutre = vals.get('neutre')
                p1 = vals.get('phase1')
                p2 = vals.get('phase2')
                p3 = vals.get('phase3')
                self._insert_value_to_label(neutre, p1, p2, p3)

                # Update graph buffers
                try:
                    self._buf_neutre.append(float(neutre) if neutre is not None else 0.0)
                    self._buf_p1.append(float(p1) if p1 is not None else 0.0)
                    self._buf_p2.append(float(p2) if p2 is not None else 0.0)
                    self._buf_p3.append(float(p3) if p3 is not None else 0.0)
                except Exception:
                    pass

                # Redraw graph
                try:
                    self._draw_graph()
                except Exception:
                    logger.exception('Erreur dessin graphe')
            except Exception:
                logger.exception('Erreur mise à jour labels measurement')
        except Exception:
            pass

    def _on_start(self):
        try:
            self.arduino.start_record()
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text('Mesure démarrée')
            logger.info('Arduino recording started')
        except Exception as e:
            logger.exception('Failed to start recording: %s', e)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur démarrage mesure: {e}')

    def _on_stop(self):
        try:
            self.arduino.stop_record()
            # Clear controller's last values so the polling won't restore old readings
            try:
                header = getattr(ArduinoController, 'FIELDNAMES', None)
                if header:
                    # build zeroed dict and set time empty
                    zeros = {k: 0 for k in header}
                    zeros['time'] = ''
                    try:
                        self.arduino._last_values = zeros
                    except Exception:
                        logger.exception('Failed to reset ArduinoController last values on stop')
            except Exception:
                logger.exception('Failed to reset ArduinoController last values on stop')

            # Update UI labels to zero immediately
            self._insert_value_to_label(0, 0, 0, 0)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text('Mesure arrêtée')
            logger.info('Arduino recording stopped')
        except Exception as e:
            logger.exception('Failed to stop recording: %s', e)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur arrêt mesure: {e}')

    def _on_save_graph(self):
        try:
            # Get configured data file path from config.paths.data_file or legacy
            data_file = None
            try:
                data_file = Path(self.config.paths.data_file)
            except Exception:
                data_file = Path(getattr(self.config, 'data_file', 'data/measurements.csv'))

            if not data_file.exists():
                msg = f"Fichier de données introuvable: {data_file}"
                logger.warning(msg)
                if hasattr(self.main_window, 'set_log_text'):
                    self.main_window.set_log_text(msg)
                return

            # Ask user for destination directory
            folder = QFileDialog.getExistingDirectory(self.main_window, "Choisir dossier de sauvegarde")
            if not folder:
                return

            dest_dir = Path(folder)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / f"measurements_copy_{data_file.stem}{data_file.suffix}"
            # If exists, append index
            i = 1
            while dest_file.exists():
                dest_file = dest_dir / f"measurements_copy_{data_file.stem}_{i}{data_file.suffix}"
                i += 1

            shutil.copy2(str(data_file), str(dest_file))
            msg = f"Fichier copié vers: {dest_file}"
            logger.info(msg)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(msg)
        except Exception as e:
            logger.exception('Erreur sauvegarde CSV: %s', e)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur sauvegarde CSV: {e}')

    def _on_reset(self):
        try:
            # Confirm with the user
            reply = QMessageBox.question(self.main_window, 'Confirmer vidage',
                                         "Voulez-vous vraiment vider le fichier de mesures ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

            # Determine data file
            try:
                data_file = Path(self.config.paths.data_file)
            except Exception:
                data_file = Path(getattr(self.config, 'data_file', 'data/measurements.csv'))

            data_file.parent.mkdir(parents=True, exist_ok=True)
            # Truncate and write header
            with open(data_file, 'w', newline='') as fh:
                writer = csv.writer(fh)
                # Use ArduinoController.FIELDNAMES if available
                header = getattr(ArduinoController, 'FIELDNAMES', None)
                if header:
                    writer.writerow(header)
                else:
                    writer.writerow(['time'])

            msg = f"Fichier de mesures vidé: {data_file}"
            logger.info(msg)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(msg)
        except Exception as e:
            logger.exception('Erreur lors du vidage du fichier CSV: %s', e)
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur vidage CSV: {e}')

    def _insert_value_to_label(self, neutre: float, p1: float, p2: float, p3: float):
        if hasattr(self.ui, 'neutral_value_label') and self.ui.neutral_value_label is not None:
            self.ui.neutral_value_label.setText(str(neutre))
        if hasattr(self.ui, 'phase_1_value_label') and self.ui.phase_1_value_label is not None:
            self.ui.phase_1_value_label.setText(str(p1))
        if hasattr(self.ui, 'phase_2_value_label') and self.ui.phase_2_value_label is not None:
            self.ui.phase_2_value_label.setText(str(p2))
        if hasattr(self.ui, 'phase_3_value_label') and self.ui.phase_3_value_label is not None:
            self.ui.phase_3_value_label.setText(str(p3))

    def _draw_graph(self):
        # Draw simple line graph into graph_label from buffers
        if not hasattr(self.ui, 'graph_label') or self.ui.graph_label is None:
            return

        w = max(200, self.ui.graph_label.width())
        h = max(100, self.ui.graph_label.height())
        pix = QPixmap(w, h)
        pix.fill(QColor('black'))

        painter = QPainter(pix)
        try:
            margin = 6
            x0 = margin
            y0 = margin
            gw = w - margin * 2
            gh = h - margin * 2

            # get data arrays
            data_sets = [list(self._buf_neutre), list(self._buf_p1), list(self._buf_p2), list(self._buf_p3)]
            # determine y range
            all_vals = [v for ds in data_sets for v in ds] if data_sets else [0]
            vmin = min(all_vals) if all_vals else 0.0
            vmax = max(all_vals) if all_vals else 1.0
            if vmax == vmin:
                vmax = vmin + 1.0

            colors = [QColor("#0000ff"), QColor('#ffff00'), QColor("#00ff00"), QColor('#ff0000')]

            for ds_idx, ds in enumerate(data_sets):
                if not ds:
                    continue
                pen = QPen(colors[ds_idx])
                pen.setWidth(2)
                painter.setPen(pen)
                n = len(ds)
                for i in range(1, n):
                    x1 = x0 + int(((i - 1) / (self._max_points - 1)) * gw)
                    x2 = x0 + int(((i) / (self._max_points - 1)) * gw)
                    y1 = y0 + int((1.0 - (ds[i - 1] - vmin) / (vmax - vmin)) * gh)
                    y2 = y0 + int((1.0 - (ds[i] - vmin) / (vmax - vmin)) * gh)
                    painter.drawLine(x1, y1, x2, y2)

            # optional grid/axis
            peng = QPen(QColor('#404040'))
            peng.setWidth(1)
            painter.setPen(peng)

        finally:
            painter.end()

        self.ui.graph_label.setPixmap(pix)