import dropbox, os, keyring
from pathlib import Path
from SDK.UTILS.general_utils import get_os_type
# from SDK.UTILS.general_utils import save_large_data, load_large_data
from cryptography.fernet import Fernet
from dropbox.oauth import DropboxOAuth2FlowNoRedirect
from dropbox.exceptions import ApiError
from dropbox.files import UploadError, WriteError, WriteConflictError


_KEY = "DATA_DROP_KEY"
# _TOKEN_SYS_NAME = "TOKEN_DROP"
_SERVICE = f"Crypteria{get_os_type()}_DropBox"


if keyring.get_password(f"Crypteria{get_os_type()}",_KEY) is None:
    k = keyring.set_password(
                            f"Crypteria{get_os_type()}",
                            _KEY,
                            Fernet.generate_key().decode()
                             )

else: k = keyring.get_password(f"Crypteria{get_os_type()}",_KEY)

fer = Fernet(k)

def authenticate():

    ACCESS_TOKEN = None

    app_key = keyring.get_password(_SERVICE, "app_key_dropbox")
    app_secret = keyring.get_password(_SERVICE, "app_secret_dropbox")

    if app_key is None or app_secret is None:
        app_key = input("DROPBOX APP KEY: ").strip()
        app_secret = input("DROPBOX APP SECRET: ").strip()
        keyring.set_password(_SERVICE, "app_key_dropbox", app_key)
        keyring.set_password(_SERVICE, "app_secret_dropbox", app_secret)

    auth_flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        app_secret,
        token_access_type="offline"
    )
    authorize_url = auth_flow.start()
    print(f"GO TO : {authorize_url}")

    auth_code = input("Enter the authorization code here: ").strip()
    oauth_result = auth_flow.finish(auth_code)

    ACCESS_TOKEN = oauth_result.access_token

    return ACCESS_TOKEN.encode()


def upload_file(local_path: Path , dropbox_path=None):
    ACCESS_TOKEN = authenticate().decode()
    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    from SDK.SERVICES.logs_service import logger

    if dropbox_path is None: dropbox_path = f"/{Path(local_path).name}"

    try:
        with open(local_path, "rb") as f:
            global result
            result = dbx.files_upload(f.read(), dropbox_path, mute=True)
    except ApiError as e:
        if isinstance(e.error, UploadError):
            print(f"Conflict: File '{local_path.stem}' already exists.")
            return None

    file_id = result.id
    logger.info(f"Dropbox Upload Successful — File ID: {file_id}")

    return file_id


def list_files(folder_path=""):
    ACCESS_TOKEN = authenticate().decode()
    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    from SDK.SERVICES.logs_service import logger

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
            logger.info(f"{entry.name}  (ID: {entry.id})  PATH: {entry.path_lower}")

    return files


def download_file(file_path_or_id):
    ACCESS_TOKEN = authenticate().decode()
    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    from SDK.SERVICES.logs_service import logger
    from SDK.UTILS.general_utils import PathManager

    if file_path_or_id.startswith("id:"):
        metadata = dbx.files_get_metadata(file_path_or_id)
        dropbox_path = metadata.path_lower

    else:
        dropbox_path = file_path_or_id

    file_name = Path(dropbox_path).name
    local_path = PathManager.get_temp_folder("CrypteriaBin") / file_name

    metadata, res = dbx.files_download(path=dropbox_path)

    with open(local_path, "wb") as f: f.write(res.content)

    logger.info(f"Dropbox Download Successful: {local_path}")

    return local_path