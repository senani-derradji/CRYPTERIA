import os
import sys
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class File(Base):
    __tablename__ = "files_table"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)

    file_id = Column(LargeBinary, index=True, nullable=False)
    file_name = Column(LargeBinary, nullable=False)
    file_type = Column(String(5), nullable=False)
    file_length = Column(Integer, nullable=False)
    file_path = Column(LargeBinary, nullable=False)
    file_sha256 = Column(String(64), nullable=True)
    nonce = Column(LargeBinary, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    providor = Column(String)
