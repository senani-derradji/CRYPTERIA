import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import keyring
from pathlib import Path
from typing import Union

from SDK.UTILS.validation import DataTypeValidate
from SDK.SECURITY.security_utils import save_decrypted_data



def load_data(data: Union[Path, DataTypeValidate]) -> bytes:
    path = data.file_path if isinstance(data, DataTypeValidate) else data

    if path.is_file():
        return path.read_bytes()

    raise FileNotFoundError(f"{path} is not a valid file.")



def get_os_type() -> str: return sys.platform

def get_length_of_file(file: Path) -> int: return str(len(load_data(file)))

def get_type_of_file(file: Path) -> str: return str(file).split(".")[1]

def get_name_of_file(file: Path) -> str: return str(file).split(".")[0]

def get_path_of_file(file: Path) -> str: return str(file)



class PathManager:

    @staticmethod
    def get_appdata_path(app_name="Crypteria") -> Path:

        if sys.platform.startswith("win"):
            base_dir = os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")

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


def save_large_data(service, username, data, block_size=500):
    blocks = [data[i:i+block_size] for i in range(0, len(data), block_size)]

    for idx, block in enumerate(blocks):
        keyring.set_password(service, f"{username}_block_{idx}", block)

    keyring.set_password(service, f"{username}_blocks_count", str(len(blocks)))

    return len(blocks)


def load_large_data(service, username):
    count = int(keyring.get_password(service, f"{username}_blocks_count"))
    blocks = []

    for idx in range(count):
        block = keyring.get_password(service, f"{username}_block_{idx}")

        if block is None:
            raise ValueError(f"Missing block {idx}")
        blocks.append(block)

    return "".join(blocks)


def check_data_in_tmp_before_download_upload(file : Path):
    
    for f in os.listdir(PathManager.get_temp_folder()):
        if f[:-4] == file.stem:
            print(f[:-4], " :f: FILE EXISTS :file: ", file)
            return True, Path(f)

        else:
            continue
    return False

