from pathlib import Path

from SDK.UTILS.validation import DataTypeValidate


bin_files_path = Path()


def save_encrypted_data(dt: Path | DataTypeValidate, key: bytes):

    from SDK.UTILS.general_utils import load_data
    from SDK.SECURITY.encryption import encrypt_data
    from SDK.UTILS.general_utils import PathManager

    if isinstance(dt, Path):
        dt = DataTypeValidate(file_path=dt).file_path

    en_data_info = encrypt_data(load_data(dt), key)
    enc_data = PathManager.get_temp_folder() / (dt.stem + ".bin")

    with open(enc_data, 'wb') as f: f.write(en_data_info)

    return enc_data



def save_decrypted_data(dt: Path, key: bytes, _type: str, dest_path: Path = Path.cwd()) -> bytes:
    from SDK.SECURITY.encryption import decrypt_data
    from SDK.UTILS.general_utils import load_data


    dec_data = dest_path / Path(str(dt).split(".")[0] + "." + str(_type))

    dec_data_info = decrypt_data(load_data(dt), key)

    with open(dec_data, 'wb') as f:
        f.write(dec_data_info)

    return dec_data
