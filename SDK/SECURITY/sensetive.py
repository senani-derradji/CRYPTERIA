import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import keyring
from cryptography.fernet import Fernet

class KeysEncryption:


    def set_data_enc_key(self, key: bytes):
        key_str = key.decode()
        keyring.set_password(f"Crypteria{sys.platform}", "dek_master_1", key_str)


    def get_data_enc_key(self) -> bytes:
        key_str = keyring.get_password(f"Crypteria{sys.platform}", "dek_master_1")
        if key_str is None:
            return None
        if key_str.startswith("b'") and key_str.endswith("'"):
            key_str = key_str[2:-1]
        return key_str.encode()


    def key_for_db(self, op: str, data):
        get_key = keyring.get_password(f"Crypteria{sys.platform}", "db_dek")

        if get_key is None:
            k = Fernet.generate_key()
            keyring.set_password(f"Crypteria{sys.platform}", "db_dek", k.decode())
            get_key = k.decode()

        f = Fernet(get_key.encode())

        if op == 'enc': return f.encrypt(data)
        elif op == 'dec': return f.decrypt(data)
        else: return None
