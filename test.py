import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from SDK.SECURITY.encryption import load_key
from pathlib import Path
from SDK.METHODS.upload import UploadDataCloud
from SDK.DBS.database import Base, engine, SessionLocal
from SDK.METHODS.download import DownloadDataCloud
# from SDK.DBS.crud import get_file_by_id
# from sqlalchemy.orm import Session
from SDK.general_utils import PathManager
import time



token = """

vsqkygauq0366ak

mc22qv5jtbfwn1k

ovqxTokCD4AAAAAAAAAAMRJaBm_udVlini7kHZnrcXM

"""


get_appdata_path = PathManager.get_appdata_path()

session = SessionLocal()
def init_db():
    Base.metadata.create_all(engine, checkfirst=True)
    print("Database initialized (created if not exists)")

init_db()

x = '------'

p = r"C:\Users\DERRADJI\Desktop\PROXERA\20210224_095829.jpg"
data = Path(p)
# up   = UploadDataCloud(data).upload_encrypted_file(cloud='google_drive')
# print(up)
# print("DRIVE DOWNLAOD : ", x*100)
# down = DownloadDataCloud(1, load_key())
# down.download_decrypted_data()

# print(x * 10)
# time.sleep(5)
# print()

drop = UploadDataCloud(data).upload_encrypted_file(cloud='dropbox')
print("DROPBOX DOWNLAOD : ", x*100)

down = DownloadDataCloud(2, load_key())


# from SDK.DBS.database import Base, SessionLocal, engine
# from SDK.DBS.models import File
# from SDK.DBS.crud import create_file_record

# # Create tables
# Base.metadata.create_all(bind=engine)

# # Start session
# db = SessionLocal()

# # Insert records
# for i in range(1, 50000):
#     print(
#         create_file_record(
#             db=db,
#             file_id=f"{i}OdwdevdfvrvfwI{i}Jowerverdedededededvddwi{i}",
#             file_name="helloworld",
#             file_type="jpg",
#             file_length=23,
#             file_path="jdpwoidjowe.jpg"
#         ),
#         " : ----- : ",
#         i
#     )
