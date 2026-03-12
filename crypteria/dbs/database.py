import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..utils.general_utils import PathManager

from .models import Base, File

p_m = PathManager.get_appdata_path()
data_dir = p_m / "data"

if not data_dir.exists(): data_dir.mkdir(parents=True) ; db_path = data_dir / "crypteria.db"
else: db_path = data_dir / "crypteria.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized (created if not exists)")

init_db()
