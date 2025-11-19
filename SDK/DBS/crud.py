import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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

    file = File(file_id=enc_dec.key_for_db('enc',(str(file_id).encode())),
                file_name=enc_dec.key_for_db('enc',str(file_name).encode()),
                file_type=file_type,
                file_length=file_length,
                file_path=enc_dec.key_for_db('enc',str(file_path).encode()),
                action=action,
                providor=providor,
                )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file

def get_file_by_id(db: Session, id_) -> str:

    id_ = db.query(File).filter(File.id == id_).first()
    if id_.file_id:
        return id_.file_id
    else:
        return None


def get_file_name_by_enc_file_id(db: Session, file_id_in: str) -> str:

    # if not isinstance(file_id_in, bytes):
    #     file_id_in = file_id_in.encode()

    # file_id_in = enc_dec.key_for_db('enc',file_id_in).decode()
    name = enc_dec.key_for_db('dec',db.query(File).filter(File.file_id == file_id_in).first().file_name).decode()
    print(name)



    if name:
        return name
    else: return None


def get_all_files(db: Session):
    return db.query(File).all()


def delete_file_by_id(db: Session, file_id):
    db.query(File).filter(File.file_id == enc_dec.key_for_db('dec',file_id).decode()).delete()
    db.commit()
    return True


def get_data_type_by_id(db: Session, file_id):
    row = db.query(File).filter(File.file_id == file_id).first()
    return row.file_type if row else exit()


def get_providor_by_id(db: Session, file_id):
    return db.query(File).filter(File.file_id == file_id).first().providor
