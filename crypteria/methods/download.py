import os
import sys
import hashlib

from ..security.encryption import load_key
from ..security.security_utils import save_decrypted_data
from ..security.crypto import (
    UniversalCrypto, CryptoMode, decrypt_file,
    KeyManager
)
from ..cloud.google_drive_service import download_file as download_file_drive
from ..dbs.crud import (
    get_file_by_id,
    get_data_type_by_id,
    create_file_record,
    get_file_name_by_enc_file_id,
    get_providor_by_id,
    get_file_sha256,
    get_file_nonce,
    _decrypt_field
)
from ..dbs.database import SessionLocal
from ..services.logs_service import logger
from ..security.sensetive import KeysEncryption
from ..utils.general_utils import PathManager
from pathlib import Path

db = SessionLocal()
enc_dec = KeysEncryption()

path_of_decrypted_downloaded_files = PathManager.get_temp_folder()

_key_manager = KeyManager()

def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte)
    return sha256_hash.hexdigest()


def verify_sha256(file_path: Path, expected_hash: str) -> bool:
    actual_hash = calculate_sha256(file_path)
    if actual_hash == expected_hash:
        logger.info(f"SHA256 verification PASSED: {actual_hash}")
        return True
    else:
        logger.error(f"SHA256 verification FAILED! Expected: {expected_hash}, Actual: {actual_hash}")
        return False


class DownloadDatacloud:
    def __init__(self, id_: int, key: bytes = None, use_advanced_encryption: bool = True):
        self.id_ = id_
        self.use_advanced_encryption = use_advanced_encryption

        if key is None:
            if use_advanced_encryption:
                key = _key_manager.get_key("upload_key")
                if key is None:
                    key = _key_manager.get_key("master_key")
                if key is None:
                    key = load_key()
                    self.use_advanced_encryption = False
            else:
                key = load_key()

        self.key = key
        self._crypto = None

    def _get_crypto(self):
        if self._crypto is None:
            self._crypto = UniversalCrypto(self.key, CryptoMode.GCM)
        return self._crypto

    def download_decrypted_data(self):
        print("DEBUG download_decrypted_data: START", file=sys.stderr, flush=True)
        file_id_enc = get_file_by_id(db, self.id_)
        print(f"DEBUG: file_id_enc = {file_id_enc}", file=sys.stderr, flush=True)
        if not file_id_enc:
            logger.error(f"File with ID {self.id_} not found.")
            return False

        providor_name = get_providor_by_id(db, self.id_)
        print(f"DEBUG: providor_name = {providor_name}", file=sys.stderr, flush=True)
        id_ = _decrypt_field(file_id_enc)
        print(f"DEBUG: id_ = {id_}", file=sys.stderr, flush=True)
        data_file_type = get_data_type_by_id(db, self.id_)

        stored_sha256 = get_file_sha256(db, self.id_)
        print(f"DEBUG: stored_sha256 = {stored_sha256}", file=sys.stderr, flush=True)

        stored_nonce = get_file_nonce(db, self.id_)
        print(f"DEBUG: stored_nonce = {stored_nonce}", file=sys.stderr, flush=True)

        logger.info(f"Debug - stored_sha256: {stored_sha256}")
        logger.info(f"Debug - stored_nonce type: {type(stored_nonce)}, value: {stored_nonce}")
        logger.info(f"Debug - key type: {type(self.key)}, length: {len(self.key) if self.key else 0}")

        print(f"DEBUG: About to download from {providor_name}", file=sys.stderr, flush=True)
        if providor_name == "google_drive":
            data_downloaded = download_file_drive(id_)
        else:
            logger.error(f"Unknown provider: {providor_name}")
            return False

        print(f"DEBUG: Downloaded to {data_downloaded}", file=sys.stderr, flush=True)

        if stored_sha256:
            if not verify_sha256(Path(data_downloaded), stored_sha256):
                logger.error("File integrity check FAILED! The downloaded file may be corrupted.")
                return False

        if self.use_advanced_encryption:
            crypto = self._get_crypto()

            nonce = stored_nonce
            if nonce is None:
                nonce_file = Path(str(data_downloaded).replace('.enc', '') + '.nonce')
                if nonce_file.exists():
                    nonce = nonce_file.read_bytes()

            if nonce:
                enc_path = Path(data_downloaded)

                enc_data = enc_path.read_bytes()
                file_nonce = enc_data[:12]
                ciphertext = enc_data[12:]

                nonce_to_use = file_nonce

                decrypted = crypto.decrypt_gcm(ciphertext, self.key, nonce_to_use)

                output_path = Path(str(enc_path).replace('.enc', ''))
                output_path.write_bytes(decrypted)

                logger.info(f"File decrypted with AES-256-GCM: {output_path}")
                res = output_path
            else:
                logger.warning("Nonce file not found, falling back to legacy decryption")
                try:
                    res = save_decrypted_data(data_downloaded, self.key, data_file_type, path_of_decrypted_downloaded_files)
                except Exception as e:
                    logger.error(f"Decryption failed: {e}. Returning encrypted file path.")
                    return data_downloaded
        else:
            try:
                res = save_decrypted_data(data_downloaded, self.key, data_file_type, path_of_decrypted_downloaded_files)
            except Exception as e:
                logger.error(f"Decryption failed: {e}. Returning encrypted file path.")
                return data_downloaded

        if res:
            if create_file_record(
                db = db,

                file_id = id_,
                file_name = res,
                file_type = data_file_type,
                file_length = len(str(data_downloaded)),
                file_path = res,

                action = "download",
                providor = providor_name,
            ):
                logger.info(f"File downloaded successfully ({res})")

                return res

        else:
            return False

    def download_decrypted_data_bytes(self) -> bytes:
        file_id_enc = get_file_by_id(db, self.id_)
        if not file_id_enc:
            logger.error(f"File with ID {self.id_} not found.")
            return None

        providor_name = get_providor_by_id(db, file_id_enc)
        id_ = _decrypt_field(file_id_enc)

        if providor_name == "google_drive":
            data_downloaded = download_file_drive(id_)
        else:
            return None

        if self.use_advanced_encryption:
            crypto = self._get_crypto()

            nonce_file = Path(str(data_downloaded).replace('.enc', '') + '.nonce')
            if nonce_file.exists():
                nonce = nonce_file.read_bytes()
                enc_data = Path(data_downloaded).read_bytes()

                decrypted = crypto.decrypt_gcm(enc_data, self.key, nonce)
                return decrypted

        return Path(data_downloaded).read_bytes()
