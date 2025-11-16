import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import keyring

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

    def key_for_db(self, key) -> bytes:
        key_str = keyring.set_password(f"Crypteria{sys.platform}", "db_dek", key)
        # i will complete it in the next commit xD
