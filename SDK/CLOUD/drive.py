from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io, keyring, json
from SDK.general_utils import PathManager
from SDK.SERVICES.logs_service import logger


SERVICE = "CrypteriaGoogleDrive"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def authenticate():
    data = keyring.get_password(SERVICE, "credentials")
    creds = None

    if data:
        info = json.loads(data)
        creds = Credentials(
            token=info.get("token"),
            refresh_token=info.get("refresh_token"),
            token_uri=info.get("token_uri"),
            client_id=info.get("client_id"),
            client_secret=info.get("client_secret"),
            scopes=SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        keyring.set_password(SERVICE, "credentials", creds.to_json())

    return creds



def upload_to_drive(file_path, file_name=None, folder_id=None):
    creds = authenticate()
    print(creds)
    service = build('drive', 'v3', credentials=creds)
    if file_name is None: file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    if folder_id: file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"VIEW : https://drive.google.com/file/d/{file.get('id')}/view")
    logger.info(f"Uploaded Successfully! File ID: {file.get('id')}")
    return file.get('id')


def list_files(page_size=10):

    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.') ; return []
    print('Files:')
    for item in items:
        print(f"{item['name']} (ID: {item['id']})")
    return items



def download_file(file_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_info = service.files().get(fileId=file_id, fields="name").execute()
    file_name = file_info['name']

    destination_path = PathManager.get_temp_folder("CryperaBin") / file_name

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}.")

    logger.info(f"Downloaded Successfully! File path: {destination_path}")


    return  destination_path