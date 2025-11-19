from SECURITY.encryption import load_key
from pathlib import Path
from SDK.CLOUD.drive import upload_to_drive
from SDK.CLOUD.drpbox import upload_file as upload_to_dropbox
from DBS.crud import create_file_record
from DBS.database import SessionLocal
from SDK.SECURITY.security_utils import save_encrypted_data as SED
from SDK.general_utils import (
               get_name_of_file,
               get_type_of_file,
               get_length_of_file,
               get_path_of_file
)
import os
from SDK.SERVICES.logs_service import logger
from SDK.validation import ProvidorValidation


db = SessionLocal()

class UploadDataCloud:
    def __init__(self, image: Path):
        self.image = image


    def upload_encrypted_file(self, cloud : ProvidorValidation):
        key = load_key()
        enc_image = SED(self.image, key)

        if cloud == "google_drive":
            res = upload_to_drive(enc_image)
        elif cloud == "dropbox":
            res = upload_to_dropbox(enc_image)
        else: return False

        print(res)

        if create_file_record(
            db = db,
            file_id = str(res),
            file_name = get_name_of_file(self.image),
            file_type = get_type_of_file(self.image),
            file_length = get_length_of_file(self.image),
            file_path = get_path_of_file(self.image),
            action = "upload",
            providor = cloud,
        ):

            logger.info(f"File uploaded successfully ({self.image})")
            print(enc_image)
            return True
        else: return False
