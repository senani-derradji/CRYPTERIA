from pathlib import Path
from sqlalchemy.orm import Session
from SDK.DBS.models import File
from SDK.SECURITY.sensetive import KeysEncryption


enc_dec = KeysEncryption()


def create_file_record(db : Session,
                       file_id,
                       file_name,
                       file_type,
                       file_length,
                       file_path,
                       action = None,
                       providor = None,
                       ):

    file = File(file_id=enc_dec.services_key('enc',(str(file_id).encode())),
                file_name=enc_dec.services_key('enc',str(file_name).encode()),
                file_type=file_type,
                file_length=file_length,
                file_path=enc_dec.services_key('enc',str(file_path).encode()),
                action=action,
                providor=providor,
                )

    db.add(file)
    db.commit()
    db.refresh(file)

    return file


def get_file_by_id(db: Session, id_) -> str:

    id_ = db.query(File).filter(File.id == id_).first()

    if id_ is None:
        NameError("FILE ID NOT FOUND") ; return None

    if id_.file_id:
        return id_.file_id

    else:
        return None


def get_file_name_by_enc_file_id(db: Session, file_id_in: str) -> str:
    if file_id_in is None: NameError("FILE ID NOT FOUND") ; return None

    name = enc_dec.services_key('dec',db.query(File).filter(
        File.file_id == file_id_in
        ).first().file_name).decode()

    if name: return name

    else: return None


def get_all_files(db: Session): return db.query(File).all()


def delete_file_by_id(db: Session, file_id):
    db.query(File).filter(
        File.file_id == enc_dec.services_key('dec',file_id).decode()
        ).delete()

    db.commit()

    return True


def get_data_type_by_id(db: Session, file_id):

    if file_id is None: NameError("FILE ID NOT FOUND") ; return None
    row = db.query(File).filter(File.file_id == file_id).first()

    return row.file_type if row else exit()


def get_providor_by_id(db: Session, file_id) -> str:
    if file_id is None: NameError("FILE ID NOT FOUND") ; return None

    return db.query(File).filter(File.file_id == file_id).first().providor


def get_path_by_file_id(db: Session, file_id) -> Path:
    if file_id is None: NameError("FILE ID NOT FOUND") ; return None

    enc_path = db.query(File).filter(File.file_id == file_id).first().file_path
    return Path(enc_dec.services_key('dec', enc_path).decode())

