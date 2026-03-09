import dropbox, os, keyring, requests, base64
from pathlib import Path
from cryptography.fernet import Fernet

import os, sys ; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.general_utils import PathManager
from services.logs_service import logger
from utils.general_utils import get_os_type
from utils.general_utils import save_large_data, load_large_data

from dropbox.files import WriteMode


_SERVICE = f"Crypteria{get_os_type()}"

_KEY = "DATA_DROP_KEY"

APP_KEY_NAME = "DROPBOX_APP_KEY"
APP_SECRET_NAME = "DROPBOX_APP_SECRET"

_TOKEN_SYS_NAME = "TOKEN_DROP_REFRESH"


if keyring.get_password(_SERVICE, _KEY) is None:

    keyring.set_password(
        _SERVICE,
        _KEY,
        Fernet.generate_key().decode()
    )

k = keyring.get_password(_SERVICE, _KEY)

fer = Fernet(k.encode() if isinstance(k, str) else k)


def get_app_credentials():

    app_key = keyring.get_password(_SERVICE, APP_KEY_NAME)
    app_secret = keyring.get_password(_SERVICE, APP_SECRET_NAME)

    if app_key is None:
        app_key = input("Enter Dropbox APP KEY: ").strip()
        keyring.set_password(_SERVICE, APP_KEY_NAME, app_key)
        logger.info("Dropbox APP KEY saved in keyring.")

    if app_secret is None:
        app_secret = input("Enter Dropbox APP SECRET: ").strip()
        keyring.set_password(_SERVICE, APP_SECRET_NAME, app_secret)
        logger.info("Dropbox APP SECRET saved in keyring.")

    return app_key, app_secret


def authenticate():

    APP_KEY, APP_SECRET = get_app_credentials()

    refresh_token = load_large_data(_SERVICE, _TOKEN_SYS_NAME)

    if refresh_token is None:

        print(f"""
OPEN THIS URL IN YOUR BROWSER:
-------------------------------------------------------------------------------------------------------------
https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&response_type=code&token_access_type=offline
-------------------------------------------------------------------------------------------------------------
Login and paste the returned CODE here.
""")

        code = input("DROPBOX AUTH CODE: ").strip()

        auth = base64.b64encode(
            f"{APP_KEY}:{APP_SECRET}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth}"
        }

        data = {
            "code": code,
            "grant_type": "authorization_code"
        }

        r = requests.post(
            "https://api.dropboxapi.com/oauth2/token",
            headers=headers,
            data=data
        )

        result = r.json()

        if "refresh_token" not in result:
            raise Exception(f"Dropbox OAuth Error: {result}")

        refresh_token = result["refresh_token"]

        enc = fer.encrypt(refresh_token.encode())

        save_large_data(
            _SERVICE,
            _TOKEN_SYS_NAME,
            enc.decode()
        )

        logger.info("Dropbox refresh token saved.")

    else:

        refresh_token = fer.decrypt(refresh_token).decode()
        logger.info("Dropbox refresh token loaded.")

    dbx = dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=refresh_token
    )

    return dbx


dbx = authenticate()

def dropbox_file_exists(dropbox_path):

    try:
        dbx.files_get_metadata(dropbox_path)
        return True

    except dropbox.exceptions.ApiError as e:
        if (e.error.is_path()
                and e.error.get_path().is_not_found()):
            return False
        else:
            raise

def upload_file(local_path, dropbox_path=None, overwrite=False):
    if dropbox_path is None:
        dropbox_path = f"/{Path(local_path).name}"

    if dropbox_file_exists(dropbox_path):
        if overwrite:
            mode = WriteMode("overwrite")
            logger.info(f"File exists. Will overwrite: {dropbox_path}")

        else:
            logger.warning(f"File already exists: {dropbox_path}")
            dropbox_path = f"/{Path(local_path).stem}_copy{Path(local_path).suffix}"
            logger.info(f"Uploading as new file: {dropbox_path}")
            mode = WriteMode("add")

    else:
        mode = WriteMode("add")

    try:
        with open(local_path, "rb") as f:
            result = dbx.files_upload(f.read(), dropbox_path, mode=mode, mute=True)
    except Exception as e:
        logger.error(f"Dropbox Upload Error: {e}")
        exit()

    logger.info(f"Dropbox Upload Successful — File ID: {result.id}")
    return result.id


def list_files(folder_path=""):

    response = dbx.files_list_folder(folder_path)

    files = []

    for entry in response.entries:

        if isinstance(entry, dropbox.files.FileMetadata):

            item = {
                "name": entry.name,
                "id": entry.id,
                "path": entry.path_lower
            }

            files.append(item)

            logger.info(
                f"{entry.name} (ID: {entry.id}) PATH: {entry.path_lower}"
            )

    return files



def download_file(file_path_or_id):

    if file_path_or_id.startswith("id:"):

        metadata = dbx.files_get_metadata(file_path_or_id)
        dropbox_path = metadata.path_lower

    else:

        dropbox_path = file_path_or_id

    file_name = Path(dropbox_path).name

    local_path = (
        PathManager.get_temp_folder("CrypteriaBin")
        / file_name
    )

    metadata, res = dbx.files_download(path=dropbox_path)

    with open(local_path, "wb") as f:
        f.write(res.content)

    logger.info(
        f"Dropbox Download Successful: {local_path}"
    )

    return local_path