import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import Column, Integer, String, LargeBinary
from SDK.DBS.database import Base
from sqlalchemy import DateTime
from datetime import datetime



class File(Base):
    __tablename__ = "files_table"
    __table_args__ = {'extend_existing': True}


    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(LargeBinary, index=True, nullable=False)
    file_name = Column(LargeBinary, nullable=False)
    file_type = Column(String(5), nullable=False)
    file_length = Column(Integer, nullable=False)
    file_path = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    providor = Column(String)