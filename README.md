GLAM rewrite - minimal scaffold

This repository is a clean rewrite scaffold for the original GLAM project.

Quickstart

Create a virtualenv and install test deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pytest pydantic
 # GLAM — application de supervision (prototype)

 Ce dépôt contient une réécriture / prototype de l'application GLAM :
 - interface graphique PySide6 pour piloter l'affichage, gérer des plans et afficher des caméras,
 - utilitaires pour la lecture de caméras RTSP/ONVIF et pour la lecture périodique de mesures via Arduino.

 ## Contenu principal
 - Code applicatif : `src/`
 - Configuration par défaut : `data/config.json` (créé/lu par `src/config/manager.py`)
 - Données de mesure : `data/measurements.csv`
 - Ressources (images, plans, fichiers QLC) : `ressources/`

 ## Fonctionnalités
 - Fenêtre principale avec pages : Accueil, Plans, Mesures, Caméra, QLC, Setup.
 - Détection réseau simple de caméras RTSP (scan du sous-réseau, port 554) et sélection persistante.
 - Gestion de caméras RTSP et ONVIF (optionnel) via `src/hardware/camera_manager.py`.
 - Lecture périodique et écriture CSV des mesures via Arduino (utilise `nanpy` si disponible).
 - Configuration typée avec `pydantic` (`src/config/manager.py`).

 ## Prérequis
 - Python 3.9+
 - Voir `requirements.txt` pour les dépendances principales : `PySide6`, `opencv-python`, `nanpy`, `onvif_zeep`, `pydantic`, `pytest`.
 - Certains composants sont optionnels :
	 - `onvif` (ONVIFCamera) pour commandes PTZ/zoom.
	 - `nanpy` pour communication Arduino.

 ## Installation rapide
 1. Créer un environnement virtuel et l'activer :

 ```bash
 python -m venv .venv
 source .venv/bin/activate
 pip install -U pip
 pip install -r requirements.txt
 ```

 2. (Optionnel) Installer `onvif_zeep` et `nanpy` si vous prévoyez d'utiliser ONVIF ou Arduino :

 ```bash
 pip install onvif_zeep nanpy
 ```

 ## Configuration
 - Le fichier de configuration lu/écrit est `data/config.json`.
 - `Config.load_default()` fusionne les valeurs du fichier et les valeurs par défaut codées.
 - Pour protéger le mot de passe RTSP en environnement CI/local, vous pouvez définir la variable d'environnement `RTSP_PASSWORD`.

 Exemples de chemins et valeurs par défaut :
 - `paths.default_img` et `paths.head_img` → images d'interface
 - `network.camera_ip` → IP par défaut de la caméra (utilisé pour la découverte)

 ## Exécution
 - L'application se lance avec :

 ```bash
 python -m src.app
 ```

 - En cas de développement d'interface, ouvrez `src/gui/Ui_MainWindow.py` (généré depuis le `.ui`).

 ## Tests
 - Les tests utilisent `pytest` :

 ```bash
 pytest -q
 ```

 ## Notes d'implémentation importantes
 - Le mot de passe RTSP est stocké en mémoire comme `SecretStr` (Pydantic) et n'est pas écrit dans le `config.json` lors de l'appel `Config.save()`.
 - La détection de caméras effectue un scan simple (port 554) et limite les résultats pour éviter des scans trop longs.
 - L'accès au matériel (Arduino, caméra ONVIF) est optionnel : le code gère l'absence de dépendances et bascule en mode simulé/limité.

 ## Contribution
 - Pour signaler un bug ou proposer une amélioration, ouvrir une issue avec une description et les étapes pour reproduire.

 ---

 Fichier principal : [src/app.py](src/app.py) — fenêtre : [src/gui/main_window.py](src/gui/main_window.py)
