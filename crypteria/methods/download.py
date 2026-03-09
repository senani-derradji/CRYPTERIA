import os, sys ; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.encryption import load_key
from security.security_utils import save_decrypted_data
from cloud.google_drive_service import download_file as download_file_drive
from cloud.dropbox_service import download_file as download_file_dropbox
from dbs.crud import (
    get_file_by_id,
    get_data_type_by_id,
    create_file_record,
    get_file_name_by_enc_file_id,
    get_providor_by_id
)
from dbs.database import SessionLocal
from services.logs_service import logger
from security.sensetive import KeysEncryption
from utils.general_utils import PathManager
from pathlib import Path

db = SessionLocal()
enc_dec = KeysEncryption()

path_of_decrypted_downloaded_files = PathManager.get_temp_folder()


class DownloadDatacloud:
    def __init__(self, id_: int, key: bytes = load_key()):
        self.id_ = id_
        self.key = key


    def download_decrypted_data(self):
        file_id_enc = get_file_by_id(db, self.id_)
        if not file_id_enc:
            logger.error(f"File with ID {self.id_} not found.")
            return False

        providor_name = get_providor_by_id(db, file_id_enc)
        id_ = enc_dec.services_key('dec', file_id_enc).decode()
        data_file_type = get_data_type_by_id(db, file_id_enc)

        if providor_name == "dropbox":
            data_downloaded = download_file_dropbox(id_)

        elif providor_name == "google_drive":
            data_downloaded = download_file_drive(id_)


        res = save_decrypted_data(data_downloaded, self.key, data_file_type, path_of_decrypted_downloaded_files)
        if res:
            if create_file_record(
                db = db,

                file_id = id_,
                file_name = res,
                file_type = data_file_type,
                file_length = len(str(data_downloaded)),
                file_path = res,

                action = "download",
                providor = providor_name,
            ):
                logger.info(f"File downloaded successfully ({res})")

                return True

        else: return False