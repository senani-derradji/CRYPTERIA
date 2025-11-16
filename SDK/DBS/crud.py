import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from DBS.models import File
from DBS.database import SessionLocal


def create_file_record(db : Session,
                       file_id,
                       file_name,
                       file_type,
                       file_length,
                       file_path
                       ):

    file = File(file_id=file_id,
                file_name=file_name,
                file_type=file_type,
                file_length=file_length,
                file_path=file_path)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file

def get_file_by_id(db: Session, id_):
    if not id_: return None
    id_ = db.query(File).filter(File.id == id_).first()
    return id_.file_id

def get_all_files(db: Session):
    return db.query(File).all()

def delete_file_by_id(db: Session, file_id):
    db.query(File).filter(File.file_id == file_id).delete()
    db.commit()
    return True

def get_data_type_by_id(db: Session, file_id):
    return db.query(File).filter(File.file_id == file_id).first().file_type