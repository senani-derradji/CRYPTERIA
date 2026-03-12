import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hashlib
import base64
import json
import keyring
from typing import Union, Tuple, Optional
from pathlib import Path
from enum import Enum

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from security.sensetive import KeysEncryption
from services.logs_service import logger


class CryptoMode(Enum):
    """Supported encryption modes"""
    GCM = "gcm"      # AES-256-GCM (authenticated encryption)
    CBC = "cbc"      # AES-256-CBC
    FERNET = "fernet" # Fernet (symmetric)


class DataType(Enum):
    """Supported data types for encryption"""
    BYTES = "bytes"
    STRING = "string"
    FILE = "file"
    JSON = "json"


class KeyManager:
    """Manages encryption keys using system keyring"""

    _instance = None
    _keyring = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._keyring = KeysEncryption()
        return cls._instance

    @staticmethod
    def get_platform_key() -> str:
        return f"Crypteria{sys.platform}"

    def generate_key(self, mode: CryptoMode = CryptoMode.GCM) -> bytes:
        """Generate a new encryption key"""
        if mode == CryptoMode.GCM or mode == CryptoMode.CBC:
            return os.urandom(32)  # 256-bit key
        elif mode == CryptoMode.FERNET:
            return Fernet.generate_key()
        else:
            raise ValueError(f"Unsupported mode: {mode}")




    def store_key(self, key: bytes, key_name: str = "master_key") -> None:

        key_str = base64.b64encode(key).decode()
        self._keyring.services_key('enc', key_str)

        keyring.set_password(self.get_platform_key(), key_name, key_str)

        logger.info(f"Key '{key_name}' stored in keyring")

    def get_key(self, key_name: str = "master_key") -> Optional[bytes]:
        """Retrieve encryption key from system keyring"""
        key_str = keyring.get_password(self.get_platform_key(), key_name)
        if key_str:
            return base64.b64decode(key_str)
        return None

    def delete_key(self, key_name: str = "master_key") -> bool:
        """Delete key from system keyring"""
        try:
            keyring.delete_password(self.get_platform_key(), key_name)
            return True
        except Exception as e:
            logger.warning(f"Could not delete key: {e}")
            return False


class UniversalCrypto:
    """
    Universal encryption/decryption class supporting all data types.
    Supports AES-256-GCM, AES-256-CBC, and Fernet modes.
    """

    def __init__(self, key: Optional[bytes] = None, mode: CryptoMode = CryptoMode.GCM):
        self.mode = mode
        self._key = key
        self._fernet = None
        self._aesgcm = None
        self._aes_cbc = None

        if key:
            self._init_cipher(key)

    def _init_cipher(self, key: bytes) -> None:
        """Initialize cipher based on mode"""
        if self.mode == CryptoMode.FERNET:
            if len(key) != 32:  # Fernet keys are 32 bytes URL-safe base64 encoded (actually 32 bytes raw)
                key = base64.urlsafe_b64encode(key[:32].ljust(32, b'0')).decode()
            self._fernet = Fernet(key if isinstance(key, bytes) else key)
        elif self.mode == CryptoMode.GCM:
            self._aesgcm = AESGCM(key)
        elif self.mode == CryptoMode.CBC:
            self._aes_cbc = key

    def set_key(self, key: bytes) -> None:
        """Set encryption key"""
        self._key = key
        self._init_cipher(key)

    @property
    def key(self) -> bytes:
        """Get current key"""
        return self._key

    # ==================== AES-256-GCM (Recommended) ====================

    def encrypt_gcm(self, data: bytes, key: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES-256-GCM (authenticated encryption).
        Returns: (ciphertext, nonce)
        """
        if key is None:
            key = self._key

        if key is None:
            raise ValueError("No key provided for encryption")

        if self._aesgcm is None or key != self._key:
            self._init_cipher(key)

        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self._aesgcm.encrypt(nonce, data, None)
        return ciphertext, nonce

    def decrypt_gcm(self, ciphertext: bytes, key: Optional[bytes] = None, nonce: Optional[bytes] = None) -> bytes:
        """Decrypt data using AES-256-GCM"""
        if key is None:
            key = self._key

        if key is None or nonce is None:
            raise ValueError("No key or nonce provided for decryption")

        if self._aesgcm is None or key != self._key:
            self._init_cipher(key)

        return self._aesgcm.decrypt(nonce, ciphertext, None)

    # ==================== AES-256-CBC ====================

    def encrypt_cbc(self, data: bytes, key: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Encrypt data using AES-256-CBC. Returns: (ciphertext, iv)"""
        if key is None:
            key = self._key

        if key is None:
            raise ValueError("No key provided for encryption")

        # Ensure key is 32 bytes
        if len(key) < 32:
            key = key.ljust(32, b'0')
        elif len(key) > 32:
            key = key[:32]

        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # PKCS7 padding
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, iv

    def decrypt_cbc(self, ciphertext: bytes, key: Optional[bytes] = None, iv: Optional[bytes] = None) -> bytes:
        """Decrypt data using AES-256-CBC"""
        if key is None:
            key = self._key

        if key is None or iv is None:
            raise ValueError("No key or IV provided for decryption")

        # Ensure key is 32 bytes
        if len(key) < 32:
            key = key.ljust(32, b'0')
        elif len(key) > 32:
            key = key[:32]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]

    # ==================== Fernet ====================

    def encrypt_fernet(self, data: bytes, key: Optional[bytes] = None) -> bytes:
        """Encrypt data using Fernet (symmetric)"""
        if key is None:
            key = self._key

        if key is None:
            raise ValueError("No key provided for encryption")

        if self._fernet is None or (key != self._key and not self._check_fernet_key(key)):
            # Need to ensure valid Fernet key
            if len(key) < 32:
                key = base64.urlsafe_b64encode(key.ljust(32, b'0')).decode()
            else:
                key = base64.urlsafe_b64encode(key[:32]).decode()
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

        return self._fernet.encrypt(data)

    def decrypt_fernet(self, encrypted_data: bytes, key: Optional[bytes] = None) -> bytes:
        """Decrypt data using Fernet"""
        if key is None:
            key = self._key

        if key is None:
            raise ValueError("No key provided for decryption")

        if self._fernet is None or not self._check_fernet_key(key):
            if len(key) < 32:
                key = base64.urlsafe_b64encode(key.ljust(32, b'0')).decode()
            else:
                key = base64.urlsafe_b64encode(key[:32]).decode()
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

        return self._fernet.decrypt(encrypted_data)

    def _check_fernet_key(self, key: bytes) -> bool:
        """Check if current key matches Fernet cipher"""
        if self._fernet is None:
            return False
        # Fernet doesn't expose key comparison, so we just check if initialized
        return True

    # ==================== Universal Methods ====================

    def encrypt(self, data: Union[bytes, str], mode: Optional[CryptoMode] = None) -> Union[bytes, Tuple[bytes, bytes]]:
        """
        Universal encrypt method. Automatically handles bytes/string.
        For GCM/CBC returns (ciphertext, nonce/iv), for Fernet returns ciphertext only.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        mode = mode or self.mode

        if mode == CryptoMode.GCM:
            return self.encrypt_gcm(data)
        elif mode == CryptoMode.CBC:
            return self.encrypt_cbc(data)
        elif mode == CryptoMode.FERNET:
            return self.encrypt_fernet(data)
        else:
            raise ValueError(f"Unsupported encryption mode: {mode}")

    def decrypt(self, encrypted_data: bytes, key: Optional[bytes] = None,
                nonce_or_iv: Optional[bytes] = None,
                mode: Optional[CryptoMode] = None) -> bytes:
        """
        Universal decrypt method.
        For GCM/CBC pass nonce/iv, for Fernet it contains the timestamp.
        """
        mode = mode or self.mode

        if mode == CryptoMode.GCM:
            return self.decrypt_gcm(encrypted_data, key, nonce_or_iv)
        elif mode == CryptoMode.CBC:
            return self.decrypt_cbc(encrypted_data, key, nonce_or_iv)
        elif mode == CryptoMode.FERNET:
            return self.decrypt_fernet(encrypted_data, key)
        else:
            raise ValueError(f"Unsupported decryption mode: {mode}")

    # ==================== File Operations ====================

    def encrypt_file(self, file_path: Union[str, Path],
                     output_path: Optional[Path] = None,
                     mode: Optional[CryptoMode] = None) -> Tuple[Path, bytes]:
        """
        Encrypt a file and return (encrypted_file_path, nonce/iv).
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        data = file_path.read_bytes()
        mode = mode or self.mode

        if mode == CryptoMode.GCM:
            ciphertext, nonce = self.encrypt_gcm(data)
        elif mode == CryptoMode.CBC:
            ciphertext, nonce = self.encrypt_cbc(data)
        elif mode == CryptoMode.FERNET:
            ciphertext = self.encrypt_fernet(data)
            nonce = b''
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.enc')

        # Write nonce/iv at the beginning for CBC/GCM
        if mode != CryptoMode.FERNET:
            final_data = nonce + ciphertext
        else:
            final_data = ciphertext

        output_path.write_bytes(final_data)

        return output_path, nonce

    def decrypt_file(self, file_path: Union[str, Path],
                     output_path: Optional[Path] = None,
                     nonce_or_iv: Optional[bytes] = None,
                     mode: Optional[CryptoMode] = None) -> Path:
        """Decrypt a file"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        data = file_path.read_bytes()
        mode = mode or self.mode

        if mode == CryptoMode.FERNET:
            decrypted = self.decrypt_fernet(data)
        else:
            # Extract nonce/iv from beginning of file (file format always has nonce at start)
            if mode == CryptoMode.GCM:
                nonce_or_iv = data[:12]
                data = data[12:]
            elif mode == CryptoMode.CBC:
                nonce_or_iv = data[:16]
                data = data[16:]

            if mode == CryptoMode.GCM:
                decrypted = self.decrypt_gcm(data, self._key, nonce_or_iv)
            elif mode == CryptoMode.CBC:
                decrypted = self.decrypt_cbc(data, self._key, nonce_or_iv)
            else:
                raise ValueError(f"Unsupported mode: {mode}")

        if output_path is None:
            output_path = file_path.with_suffix('.decrypted' + file_path.suffix.replace('.enc', ''))

        output_path.write_bytes(decrypted)
        return output_path


# ==================== Key Derivation Functions ====================

def derive_key_from_password(password: str, salt: Optional[bytes] = None,
                             iterations: int = 100000) -> Tuple[bytes, bytes]:
    """
    Derive a key from password using PBKDF2-HMAC-SHA256.
    Returns: (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    password_bytes = password.encode('utf-8')

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )

    key = kdf.derive(password_bytes)
    return key, salt


def derive_key_hkdf(master_key: bytes, info: Optional[bytes] = None) -> bytes:
    """Derive a key from master key using HKDF"""
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=info or b'crypteria-encryption',
        backend=default_backend()
    ).derive(master_key)


def hash_data(data: bytes, algorithm: str = 'sha256') -> str:
    """Hash data using specified algorithm"""
    if algorithm == 'sha256':
        return hashlib.sha256(data).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data).hexdigest()
    elif algorithm == 'blake2b':
        return hashlib.blake2b(data).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


# ==================== Convenience Functions ====================

# Default crypto instance (lazy initialization)
_default_crypto: Optional[UniversalCrypto] = None

def get_default_crypto() -> UniversalCrypto:
    """Get or create default crypto instance"""
    global _default_crypto
    if _default_crypto is None:
        _default_crypto = UniversalCrypto(mode=CryptoMode.GCM)
    return _default_crypto


def set_default_key(key: bytes) -> None:
    """Set default encryption key"""
    global _default_crypto
    if _default_crypto is None:
        _default_crypto = UniversalCrypto(key, mode=CryptoMode.GCM)
    else:
        _default_crypto.set_key(key)


def encrypt(data: Union[bytes, str], key: Optional[bytes] = None,
            mode: CryptoMode = CryptoMode.GCM) -> Union[bytes, Tuple[bytes, bytes]]:
    """Convenience function to encrypt data"""
    crypto = UniversalCrypto(key, mode)
    return crypto.encrypt(data, mode)


def decrypt(encrypted_data: bytes, key: bytes,
            nonce_or_iv: Optional[bytes] = None,
            mode: CryptoMode = CryptoMode.GCM) -> bytes:
    """Convenience function to decrypt data"""
    crypto = UniversalCrypto(key, mode)
    return crypto.decrypt(encrypted_data, key, nonce_or_iv, mode)


def encrypt_file(file_path: Union[str, Path], key: Optional[bytes] = None,
                 mode: CryptoMode = CryptoMode.GCM) -> Tuple[Path, bytes]:
    """Convenience function to encrypt a file"""
    crypto = UniversalCrypto(key, mode)
    return crypto.encrypt_file(file_path, mode=mode)


def decrypt_file(file_path: Union[str, Path], key: bytes,
                 nonce_or_iv: Optional[bytes] = None,
                 mode: CryptoMode = CryptoMode.GCM) -> Path:
    """Convenience function to decrypt a file"""
    crypto = UniversalCrypto(key, mode)
    return crypto.decrypt_file(file_path, nonce_or_iv=nonce_or_iv, mode=mode)
