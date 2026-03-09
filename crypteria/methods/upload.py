
from pathlib import Path
import os, sys ; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.encryption import load_key
from cloud.google_drive_service import upload_to_drive
from cloud.dropbox_service import upload_file as upload_to_dropbox
from dbs.crud import create_file_record
from dbs.database import SessionLocal
from security.security_utils import save_encrypted_data as SED
from utils.general_utils import (
               get_name_of_file,
               get_type_of_file,
               get_length_of_file,
               get_path_of_file
)
from services.logs_service import logger


db = SessionLocal()

class UploadDatacloud:
    def __init__(self, image: Path):
        self.image = image


    def upload_encrypted_file(self, cloud : str):

        __key = load_key()

        enc_image = SED(self.image, __key)

        if cloud == "google_drive":
            res = upload_to_drive(enc_image)
        elif cloud == "dropbox":
            res = upload_to_dropbox(enc_image)
        else:
            return False

        db_file = create_file_record(
            db = db,
            file_id = str(res),

            file_name = get_name_of_file(self.image),
            file_type = get_type_of_file(self.image),
            file_length = get_length_of_file(self.image),
            file_path = get_path_of_file(self.image),

            action = "upload",
            providor = cloud,
        )

        if db_file:
            logger.info(f"File uploaded successfully ({self.image})")
            return db_file.id
        else: return False
