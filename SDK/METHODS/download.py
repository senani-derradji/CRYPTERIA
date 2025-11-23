import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SDK.SECURITY.encryption import load_key
from SDK.SECURITY.security_utils import save_decrypted_data
from SDK.DBS.crud import (
    get_file_by_id,
    get_data_type_by_id,
    create_file_record,
    get_providor_by_id,
    get_path_by_file_id,
    get_file_name_by_enc_file_id,
)
from SDK.DBS.database import SessionLocal
from SDK.SERVICES.logs_service import logger
from SDK.SECURITY.sensetive import KeysEncryption
from SDK.UTILS.general_utils import PathManager
from SDK.UTILS.general_utils import check_data_in_tmp_before_download_upload as CHECK_BEFORE_DO
from pathlib import Path
from SDK.CLOUD.dropbox_service import download_file as download_file_dropbox
from SDK.CLOUD.google_drive_service import download_file as download_file_drive



db = SessionLocal()
enc_dec = KeysEncryption()

path_of_decrypted_downloaded_files = PathManager.get_temp_folder()


class DownloadDataCloud:
    def __init__(self, id_: int, key: bytes = load_key()):
        self.id_ = id_
        self.key = key


    def download_decrypted_data(self):

        file_id_enc = get_file_by_id(db, self.id_)
        providor_name = get_providor_by_id(db, file_id_enc)
        id_ = enc_dec.services_key('dec', file_id_enc).decode()
        data_file_type = get_data_type_by_id(db, file_id_enc)
        file_path = get_path_by_file_id(db, file_id_enc)
        print("FILE PATH : ", file_path)
        print(providor_name)

        check, d_file = CHECK_BEFORE_DO(file_path)

        if not check:
            if providor_name == "dropbox": data_downloaded = download_file_dropbox(id_)
            elif providor_name == "google_drive": data_downloaded = download_file_drive(id_)
            else: ValueError("PROVIDOR NOT FOUND")

        else: data_downloaded = d_file

        res = save_decrypted_data(data_downloaded, self.key, data_file_type, path_of_decrypted_downloaded_files)

        if res:
            if create_file_record(
                db = db,
                file_id = id_,
                file_name = res,
                file_type = data_file_type,
                file_length = len(str(data_downloaded)) if data_downloaded else 0,
                file_path = res,

                action = "download",
                providor = providor_name,
            ):
                print(f"File downloaded From CLOUD successfully ({res})")
                logger.info(f"File downloaded successfully ({res})")

                return True

        else: return False