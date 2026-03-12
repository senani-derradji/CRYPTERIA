# Crypteria Security Module
# Universal encryption for all data types

# Crypto classes and functions
from .crypto import (
    # Classes
    CryptoMode,
    DataType,
    KeyManager,
    UniversalCrypto,

    # Key derivation functions
    derive_key_from_password,
    derive_key_hkdf,
    hash_data,

    # Convenience functions
    get_default_crypto,
    set_default_key,
    encrypt,
    decrypt,
    encrypt_file,
    decrypt_file,
)

# Legacy encryption functions (from encryption.py)
from .encryption import (
    generate_key,
    load_key,
    encrypt_data,
    decrypt_data,
)

# Security utilities
from .security_utils import (
    save_encrypted_data,
    save_decrypted_data,
)

# Key management
from .sensetive import KeysEncryption

__all__ = [
    # New crypto module
    'CryptoMode',
    'DataType',
    'KeyManager',
    'UniversalCrypto',
    'derive_key_from_password',
    'derive_key_hkdf',
    'hash_data',
    'get_default_crypto',
    'set_default_key',
    'encrypt',
    'decrypt',
    'encrypt_file',
    'decrypt_file',

    # Legacy encryption
    'generate_key',
    'load_key',
    'encrypt_data',
    'decrypt_data',

    # Security utilities
    'save_encrypted_data',
    'save_decrypted_data',

    # Key management
    'KeysEncryption',
]
