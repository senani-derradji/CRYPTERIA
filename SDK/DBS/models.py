import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import Column, Integer, String
from SDK.DBS.database import Base


class File(Base):
    __tablename__ = "files_table"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    file_name = Column(String(100), nullable=False)
    file_type = Column(String(5), nullable=False)
    file_length = Column(Integer, nullable=False)
    file_path = Column(String)
