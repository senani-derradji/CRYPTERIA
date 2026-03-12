import keyring, sys
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


    def services_key(self, op: str, data, key_name="db_dek"):

        get_key = keyring.get_password(f"Crypteria{sys.platform}", key_name)

        if get_key is None:
            k = Fernet.generate_key()
            keyring.set_password(f"Crypteria{sys.platform}", key_name, k.decode())

            get_key = k.decode()

        f = Fernet(get_key.encode())

        if not data: ValueError("DATA NOT FOUND !")

        if type(data) != bytes: data = data.encode()

        if op == 'enc': return f.encrypt(data)
        elif op == 'dec': return f.decrypt(data)

        else: return None

