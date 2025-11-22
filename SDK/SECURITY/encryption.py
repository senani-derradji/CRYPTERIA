import hashlib, base64, keyring, sys, os
from cryptography.fernet import Fernet

from SDK.UTILS.validation import DataPayload
from SDK.SECURITY.sensetive import KeysEncryption
from SDK.SERVICES.logs_service import logger


def get_password_for_key() -> bytes:

    try:
        r = sys.platform+sys.version.split()[0]+str(round(sys.maxsize/(1024**3)))

    except Exception as e:
        print(f"GET PASSWORD FOR KEY ERROR : {e}")
        logger.error(f"GET PASSWORD FOR KEY ERROR : {e}") ; r = None

    return r.encode()


def get_salt() -> bytes:
    try:
        salt_str = keyring.get_password("Crypteria_INFO", "salt")

        if salt_str is None:
            salt = os.urandom(16)
            salt_str = base64.b64encode(salt).decode("ascii")
            keyring.set_password("Crypteria_INFO", "salt", salt_str)
            logger.info("Generated new salt and stored in keyring")
            return salt

        else:
            return base64.b64decode(salt_str)

    except Exception as e:
        logger.error(f"GET SALT ERROR : {e}")
        return os.urandom(16)


_k = hashlib.pbkdf2_hmac(
    hash_name="sha256",
    password=get_password_for_key(),
    salt=get_salt(),
    iterations=100000,
    dklen=32
)


def generate_key():

    KeysEncryption.set_data_enc_key(base64.encodebytes(_k))

    return base64.encodebytes(_k)


def load_key():
    key = KeysEncryption.get_data_enc_key()

    if not key:
        key = generate_key()

    return key


def encrypt_data(data: bytes | DataPayload, key: bytes) -> bytes:

    if isinstance(data, bytes): data = DataPayload(data=data).data
    else: ValueError("Data must be of type bytes")

    if not data or not key: raise ValueError("Missing data or key for encryption")

    fer = Fernet(key)
    encrypted = fer.encrypt(data)

    return encrypted


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    if not encrypted_data or not key: raise ValueError("Missing data or key for decryption")

    fer = Fernet(key)
    decrypted = fer.decrypt(encrypted_data)

    return decrypted