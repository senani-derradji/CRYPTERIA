import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from  crypteria.UTILS.general_utils import PathManager


p_m = PathManager.get_appdata_path()

data_dir = p_m / "data"

if not data_dir.exists(): data_dir.mkdir(parents=True) ; db_path = data_dir / "crypteria.db"
else: db_path = data_dir / "crypteria.db"

if not db_path.exists(): db_path.touch()

Base = declarative_base()

# ------------------------------------ NOTE ---------------------------------------
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