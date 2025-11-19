import os, sys
from pathlib import Path


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))


def load_data(data: Path) -> bytes:
    if data.is_file():
        with open(data, 'rb') as f:
            return f.read()


def get_length_of_file(file: Path) -> int: return str(len(load_data(file)))
def get_type_of_file(file: Path) -> str: return str(file).split(".")[1]
def get_name_of_file(file: Path) -> str: return str(file).split(".")[0]
def get_path_of_file(file: Path) -> str: return str(file)

import os
import sys
from pathlib import Path

class PathManager:

    @staticmethod
    def get_appdata_path(app_name="Crypteria") -> Path:
        if sys.platform.startswith("win"):
            base_dir = os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")
        elif sys.platform == "darwin":
            base_dir = Path.home() / "Library" / "Application Support"
        elif sys.platform.startswith("linux"):
            base_dir = Path.home() / ".local" / "share"
        else:
            base_dir = Path.home()

        app_dir = Path(base_dir) / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    @staticmethod
    def get_temp_folder(folder: str = "CryperaTMP") -> Path:
        system = sys.platform

        if system.startswith("win"):
            base = os.environ.get("TEMP") or os.environ.get("TMP") or "C:\\Windows\\Temp"
        elif system.startswith("linux"):
            if "ANDROID_STORAGE" in os.environ or "android" in sys.platform:
                base = "/data/local/tmp"
            else:
                base = "/tmp"
        elif system == "darwin":
            base = "/tmp"
        else:
            base = "/tmp"

        final_path = Path(base) / folder
        final_path.mkdir(parents=True, exist_ok=True)
        return final_path
