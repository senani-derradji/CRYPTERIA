import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from SDK.validation import DataTypeValidate, DataTypes
from encryption import encrypt_data, decrypt_data
from SDK.general_utils import load_data
from SDK.general_utils import PathManager


bin_files_path = Path()
temp_folder = PathManager.get_temp_folder()

def save_encrypted_data(dt: DataTypeValidate, key: bytes):
    en_data_info = encrypt_data(load_data(dt), key)
    enc_data = temp_folder / (dt.stem + ".bin")
    with open(enc_data, 'wb') as f: f.write(en_data_info)
    return enc_data


def save_decrypted_data(dt: Path, key: bytes, _type: DataTypes, dest_path: Path = Path.cwd()) -> bytes:
    dec_data = dest_path / Path(str(dt).split(".")[0] + "_decrypted." + str(_type))
    dec_data_info = decrypt_data(load_data(dt), key)
    with open(dec_data, 'wb') as f: f.write(dec_data_info)
    return dec_data