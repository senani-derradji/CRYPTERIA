import os, sys ; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hashlib

from security.encryption import load_key
from security.security_utils import save_decrypted_data
from security.crypto import (
    UniversalCrypto, CryptoMode, decrypt_file,
    KeyManager
)
from cloud.google_drive_service import download_file as download_file_drive
from dbs.crud import (
    get_file_by_id,
    get_data_type_by_id,
    create_file_record,
    get_file_name_by_enc_file_id,
    get_providor_by_id,
    get_file_sha256,
    get_file_nonce,
    _decrypt_field
)
from dbs.database import SessionLocal
from services.logs_service import logger
from security.sensetive import KeysEncryption
from utils.general_utils import PathManager
from pathlib import Path

db = SessionLocal()
enc_dec = KeysEncryption()

path_of_decrypted_downloaded_files = PathManager.get_temp_folder()

# Key manager for handling encryption keys
_key_manager = KeyManager()

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte)
    return sha256_hash.hexdigest()


def verify_sha256(file_path: Path, expected_hash: str) -> bool:
    """Verify file SHA256 hash matches expected value"""
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

        # Get or generate key
        if key is None:
            if use_advanced_encryption:
                # Try to get key from keyring (check both upload_key and master_key)
                key = _key_manager.get_key("upload_key")
                if key is None:
                    key = _key_manager.get_key("master_key")
                if key is None:
                    # Fall back to legacy key
                    key = load_key()
                    self.use_advanced_encryption = False
            else:
                key = load_key()

        self.key = key
        self._crypto = None

    def _get_crypto(self):
        """Get or create crypto instance"""
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

        # Get stored SHA256 for verification
        stored_sha256 = get_file_sha256(db, self.id_)
        print(f"DEBUG: stored_sha256 = {stored_sha256}", file=sys.stderr, flush=True)

        # Get stored nonce for decryption (from database)
        stored_nonce = get_file_nonce(db, self.id_)
        print(f"DEBUG: stored_nonce = {stored_nonce}", file=sys.stderr, flush=True)

        # Debug: Log what's retrieved
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

        # Verify SHA256 of downloaded encrypted file before decryption
        if stored_sha256:
            if not verify_sha256(Path(data_downloaded), stored_sha256):
                logger.error("File integrity check FAILED! The downloaded file may be corrupted.")
                return False

        if self.use_advanced_encryption:
            # Use new AES-256-GCM decryption
            crypto = self._get_crypto()

            # Use stored nonce from database (preferred) or fall back to local file
            nonce = stored_nonce
            if nonce is None:
                # Fall back to local nonce file (for legacy uploads)
                nonce_file = Path(str(data_downloaded).replace('.enc', '') + '.nonce')
                if nonce_file.exists():
                    nonce = nonce_file.read_bytes()

            if nonce:
                enc_path = Path(data_downloaded)

                # Read the encrypted file
                # The encrypted file format is: nonce (12 bytes) + ciphertext
                enc_data = enc_path.read_bytes()
                # Extract nonce from file (first 12 bytes) and ciphertext (rest)
                file_nonce = enc_data[:12]
                ciphertext = enc_data[12:]

                # Use the nonce from the file (not from database) - they're the same but file one is more reliable
                nonce_to_use = file_nonce

                # Decrypt using AES-256-GCM directly
                decrypted = crypto.decrypt_gcm(ciphertext, self.key, nonce_to_use)

                # Write decrypted data to output file
                output_path = Path(str(enc_path).replace('.enc', ''))
                output_path.write_bytes(decrypted)

                logger.info(f"File decrypted with AES-256-GCM: {output_path}")
                res = output_path
            else:
                # Fall back to legacy decryption
                logger.warning("Nonce file not found, falling back to legacy decryption")
                try:
                    res = save_decrypted_data(data_downloaded, self.key, data_file_type, path_of_decrypted_downloaded_files)
                except Exception as e:
                    # If decryption fails, return the encrypted file path for verification
                    logger.error(f"Decryption failed: {e}. Returning encrypted file path.")
                    return data_downloaded
        else:
            # Use legacy decryption
            try:
                res = save_decrypted_data(data_downloaded, self.key, data_file_type, path_of_decrypted_downloaded_files)
            except Exception as e:
                # If decryption fails, return the encrypted file path
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
        """Download and decrypt data, returning bytes directly"""
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

            # Check for nonce file
            nonce_file = Path(str(data_downloaded).replace('.enc', '') + '.nonce')
            if nonce_file.exists():
                nonce = nonce_file.read_bytes()
                enc_data = Path(data_downloaded).read_bytes()

                # Decrypt directly to bytes
                decrypted = crypto.decrypt_gcm(enc_data, self.key, nonce)
                return decrypted

        # Fall back to legacy
        return Path(data_downloaded).read_bytes()
