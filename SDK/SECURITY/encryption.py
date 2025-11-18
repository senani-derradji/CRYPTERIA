import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from SDK.validation import DataPayload
from SDK.SECURITY.sensetive import KeysEncryption
import urllib.request
from SDK.SERVICES.logs_service import logger


def get_password_for_key() -> bytes:
    try:
     r = sys.platform+sys.version.split()[0]+str(round(sys.maxsize/(1024**3)))+str(urllib.request.urlopen('https://api.ipify.org').read().decode())
    except Exception as e:
        logger.error(f"GET PASSWORD FOR KEY ERROR : {e}")
        r = None
    return r


ENCKEY = KeysEncryption()
password = get_password_for_key()
if isinstance(password, str): password = password.encode()

k = hashlib.pbkdf2_hmac(
    hash_name='sha256',
    password=password,
    salt=os.urandom(16),
    iterations=100000,
    dklen=32
)

master_key = HKDF(algorithm=hashes.SHA256(),salt=None,length=32,info=None).derive(k)

def generate_key():
    key = Fernet.generate_key()
    ENCKEY.set_data_enc_key(key)
    return key

def load_key():
    key = ENCKEY.get_data_enc_key()
    if not key:
        key = generate_key()
    return key

def encrypt_data(data: DataPayload, key: bytes) -> bytes:
    fer = Fernet(key)
    encrypted = fer.encrypt(data)
    return encrypted


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    fer = Fernet(key)
    decrypted = fer.decrypt(encrypted_data)
    return decrypted