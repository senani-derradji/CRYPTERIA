import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from pathlib import Path
import keyring
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SDK.general_utils import PathManager

SERVICE = "CrypteriaDropbox"
APP_KEY_DROP = "APP_KEY_DROPBOX"
APP_SECRET_DROP = "APP_SECRET_DROPBOX"
ACCESS_TOKEN_DROP = "ACCESS_TOKEN_DROPBOX"


def get_credential(key_name: str, prompt_text: str) -> str:
    value = keyring.get_password(SERVICE, key_name)
    if value:
        return value
    value = os.getenv(key_name)
    if value:
        return value
    return input(f"{prompt_text}: ").strip()


def save_credential(key_name: str, value: str):
    print(type(value) , " ---- VALUE TYPE")
    if not isinstance(value, str):
        str(value)

    keyring.set_password(SERVICE, key_name, value)


class DropboxClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dbx = cls._instance._authenticate()
        return cls._instance

    def _authenticate(self):
        APP_KEY = get_credential(APP_KEY_DROP, "Enter Dropbox App Key")
        APP_SECRET = get_credential(APP_SECRET_DROP, "Enter Dropbox App Secret")

        ACCESS_TOKEN = keyring.get_password(SERVICE, ACCESS_TOKEN_DROP)

        if not ACCESS_TOKEN:
            flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
            print("OPEN THE LINK AND GRANT PERMISSIONS:")
            print(flow.start())
            code = input("Enter the code here: ").strip()
            ACCESS_TOKEN = flow.finish(code).access_token
            save_credential(ACCESS_TOKEN_DROP, ACCESS_TOKEN)

        dbx = dropbox.Dropbox(ACCESS_TOKEN)

        try:
            dbx.users_get_current_account()
        except dropbox.exceptions.AuthError:
            print("Invalid token, retrying...")
            keyring.delete_password(SERVICE, ACCESS_TOKEN_DROP)
            return self._authenticate()

        save_credential(APP_KEY_DROP, APP_KEY)
        save_credential(APP_SECRET_DROP, APP_SECRET)

        return dbx

    def get_client(self):
        return self.dbx


def upload_file(file_path: Path, dest_path: str = None):
    dbx = DropboxClient().get_client()
    dest_path = f"/{file_path.name}" if dest_path is None else "/" + dest_path.strip("/")
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode("overwrite"))
    print(f"Uploaded Successfully! File path: {dest_path}")
    return dest_path


def list_files(folder_path: str = ""):
    dbx = DropboxClient().get_client()
    folder_path = "/" + folder_path.strip("/")
    result = dbx.files_list_folder(folder_path)
    items = result.entries
    if not items:
        print("No files found.")
        return []
    print("Files:")
    for item in items:
        print(f"{item.name} (ID: {item.id})")
    return items


def download_file(file_path: str, dest_folder: Path = None):
    dbx = DropboxClient().get_client()
    file_path = "/" + file_path.strip("/")
    if dest_folder is None:
        dest_folder = PathManager.get_temp_folder("CryperaBin")
    dest_folder.mkdir(parents=True, exist_ok=True)
    local_path = dest_folder / Path(file_path).name
    metadata, res = dbx.files_download(file_path)
    with open(local_path, "wb") as f:
        f.write(res.content)
    print(f"Downloaded Successfully! File path: {local_path}")
    return local_path


print(keyring.get_password(SERVICE, APP_KEY_DROP))
print(keyring.get_password(SERVICE, APP_SECRET_DROP))
print(keyring.get_password(SERVICE, ACCESS_TOKEN_DROP))