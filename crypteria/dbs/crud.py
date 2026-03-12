import os
import sys
from sqlalchemy.orm import Session
from .models import File
from ..security.sensetive import KeysEncryption
from ..security.crypto import UniversalCrypto, CryptoMode, KeyManager
from ..services.logs_service import logger


enc_dec = KeysEncryption()

_db_key_manager = KeyManager()

_db_enc_key = _db_key_manager.get_key("db_field_key")
if _db_enc_key is None:
    _db_enc_key = _db_key_manager.generate_key(CryptoMode.GCM)
    _db_key_manager.store_key(_db_enc_key, "db_field_key")

_db_crypto = UniversalCrypto(_db_enc_key, CryptoMode.GCM)


def _encrypt_field(value: str) -> bytes:
    if isinstance(value, str):
        value = value.encode()
    ciphertext, nonce = _db_crypto.encrypt_gcm(value)
    return f"{nonce.hex()}:{ciphertext.hex()}".encode()


def _decrypt_field(encrypted_value: bytes) -> str:
    try:
        parts = encrypted_value.decode().split(':')
        if len(parts) == 2:
            nonce = bytes.fromhex(parts[0])
            ciphertext = bytes.fromhex(parts[1])
            return _db_crypto.decrypt_gcm(ciphertext, _db_enc_key, nonce).decode()
    except Exception as e:
        pass

    return enc_dec.services_key('dec', encrypted_value).decode()


def create_file_record(db : Session,
                       file_id,
                       file_name,
                       file_type,
                       file_length,
                       file_path,
                       action = None,
                       providor = None,
                       file_sha256 = None,
                       nonce = None,
                       use_advanced_encryption: bool = True,
                       ):

    try:
        if use_advanced_encryption:
            file = File(
                file_id=_encrypt_field(str(file_id)),
                file_name=_encrypt_field(str(file_name)),
                file_type=file_type,
                file_length=file_length,
                file_path=_encrypt_field(str(file_path)),
                file_sha256=file_sha256,
                nonce=nonce,
                action=action,
                providor=providor,
            )
        else:
            file = File(
                file_id=enc_dec.services_key('enc',(str(file_id).encode())),
                file_name=enc_dec.services_key('enc',str(file_name).encode()),
                file_type=file_type,
                file_length=file_length,
                file_path=enc_dec.services_key('enc',str(file_path).encode()),
                file_sha256=file_sha256,
                nonce=nonce,
                action=action,
                providor=providor,
            )

        db.add(file)
        db.commit()
        db.refresh(file)

        logger.info(f"File record created with ID: {file.id}")
        return file

    except Exception as e:
        logger.error(f"Failed to create file record: {e}")
        db.rollback()
        return None

def get_file_by_id(db: Session, id_) -> str:

    id_ = db.query(File).filter(File.id == id_).first()

    if id_ and id_.file_id:
        return id_.file_id

    else:
        return None


def get_file_name_by_enc_file_id(db: Session, file_id_in: str) -> str:
    row = db.query(File).filter(File.file_id == file_id_in).first()

    if row and row.file_name:
        try:
            return _decrypt_field(row.file_name)
        except:
            return enc_dec.services_key('dec', row.file_name).decode()

    return None


def get_all_files(db: Session):
    return db.query(File).all()


def delete_file_by_id(db: Session, file_id):
    try:
        decrypted_id = _decrypt_field(file_id)
    except:
        try:
            decrypted_id = enc_dec.services_key('dec', file_id).decode()
        except:
            decrypted_id = file_id

    db.query(File).filter(File.file_id == file_id).delete()
    db.commit()

    return True


def get_data_type_by_id(db: Session, id: int):
    row = db.query(File).filter(File.id == id).first()
    return row.file_type if row else None


def get_providor_by_id(db: Session, id: int):
    row = db.query(File).filter(File.id == id).first()
    return row.providor if row else None


def get_file_sha256(db: Session, id: int):
    row = db.query(File).filter(File.id == id).first()
    return row.file_sha256 if row else None


def get_file_nonce(db: Session, id: int):
    row = db.query(File).filter(File.id == id).first()
    return row.nonce if row else None
