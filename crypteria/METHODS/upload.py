
from pathlib import Path
import os, sys, hashlib

from security.encryption import load_key
from security.crypto import (
    UniversalCrypto, CryptoMode, encrypt_file,
    get_default_crypto, set_default_key, KeyManager
)
from cloud.google_drive_service import upload_to_drive
from dbs.crud import create_file_record
from dbs.database import SessionLocal
from security.security_utils import save_encrypted_data as SED
from utils.general_utils import (
               get_name_of_file,
               get_type_of_file,
               get_length_of_file,
               get_path_of_file
)
from services.logs_service import logger


db = SessionLocal()

# Key manager for handling encryption keys
_key_manager = KeyManager()


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte)
    return sha256_hash.hexdigest()


class UploadDatacloud:
    def __init__(self, image: Path, use_advanced_encryption: bool = True):
        self.image = image
        self.use_advanced_encryption = use_advanced_encryption
        self._crypto = None

    def _get_crypto(self):
        """Get or create crypto instance with key from keyring"""
        if self._crypto is None:
            # Try to get existing key from keyring
            key = _key_manager.get_key("upload_key")
            if key is None:
                # Generate new key if none exists
                key = _key_manager.generate_key(CryptoMode.GCM)
                _key_manager.store_key(key, "upload_key")

            self._crypto = UniversalCrypto(key, CryptoMode.GCM)
        return self._crypto

    def upload_encrypted_file(self, cloud : str):

        if self.use_advanced_encryption:
            # Use new AES-256-GCM encryption
            crypto = self._get_crypto()
            key = crypto.key

            # Encrypt file and get nonce
            enc_image, nonce = crypto.encrypt_file(self.image)

            # Store nonce with the encrypted file for later decryption (in database)
            # Note: We also save locally for backup purposes
            nonce_file = enc_image.with_suffix(enc_image.suffix + '.nonce')
            nonce_file.write_bytes(nonce)

            if cloud == "google_drive":
                res = upload_to_drive(enc_image)
                # Upload nonce file for backup/legacy support
                upload_to_drive(nonce_file)
            else:
                return False

            # Store the key in keyring for retrieval during download
            key_b64 = __import__('base64').b64encode(key).decode()
            logger.info(f"File encrypted with AES-256-GCM, key stored in keyring")

            # Pass nonce to create_file_record for database storage
            nonce_for_db = nonce
        else:
            # Use legacy Fernet encryption (backward compatibility)
            __key = load_key()
            enc_image = SED(self.image, __key)

            if cloud == "google_drive":
                res = upload_to_drive(enc_image)
            else:
                return False

        # Calculate SHA256 of the encrypted file for integrity verification
        file_sha256 = calculate_sha256(enc_image)
        logger.info(f"File SHA256: {file_sha256}")

        db_file = create_file_record(
            db = db,
            file_id = str(res),

            file_name = get_name_of_file(self.image),
            file_type = get_type_of_file(self.image),
            file_length = get_length_of_file(self.image),
            file_path = get_path_of_file(self.image),
            file_sha256 = file_sha256,
            nonce = nonce_for_db if self.use_advanced_encryption else None,

            action = "upload",
            providor = cloud,
        )

        if db_file:
            logger.info(f"File uploaded successfully ({self.image})")
            return db_file.id
        else: return False

    def upload_encrypted_data(self, data: bytes, cloud: str, file_name: str = "data.bin"):
        """Upload raw data with encryption"""

        if self.use_advanced_encryption:
            crypto = self._get_crypto()
            key = crypto.key

            # Encrypt data
            ciphertext, nonce = crypto.encrypt_gcm(data)

            # Save to temp file
            from utils.general_utils import PathManager
            temp_folder = PathManager.get_temp_folder()
            enc_file = temp_folder / (file_name + '.enc')
            nonce_file = temp_folder / (file_name + '.nonce')

            enc_file.write_bytes(ciphertext)
            nonce_file.write_bytes(nonce)

            # Upload both files
            if cloud == "google_drive":
                res = upload_to_drive(enc_file)
                upload_to_drive(nonce_file)
            else:
                return False

            logger.info(f"Data encrypted with AES-256-GCM and uploaded")
            return res
        else:
            # Legacy encryption
            __key = load_key()
            from security.encryption import encrypt_data
            enc_data = encrypt_data(data, __key)

            from utils.general_utils import PathManager
            temp_folder = PathManager.get_temp_folder()
            enc_file = temp_folder / (file_name + '.enc')
            enc_file.write_bytes(enc_data)

            if cloud == "google_drive":
                res = upload_to_drive(enc_file)
            else:
                return False

            return res
