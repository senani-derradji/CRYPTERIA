# cloud

## Purpose
The `cloud` module serves as the adapter layer that communicates with external cloud APIs. Because Crypteria handles encryption locally, this module strictly deals with uploading and downloading **ciphertext** (encrypted data files). It has no knowledge of the file's contents, only its binary payload and intended destination.

## Key Modules
- **`google_drive_service.py`**: Manages OAuth2 authorization with Google using `google-auth-oauthlib`. Uses `MediaFileUpload` and `MediaIoBaseDownload` to handle chunked, resumable I/O streams for large files, keeping memory overhead low.
- **`dropbox_service.py`**: Utilizes the `dropbox` Python SDK to handle OAuth flows and file transfers. It supports overwrite logic and dynamic naming if file collisions occur.

## Interaction with Other Modules
- **`methods`**: The primary caller of this module. `methods` dictates when and what to upload or download.
- **`security`**: The `cloud` module uses secure `keyring` operations provided by `security` to safely stash OAuth access tokens locally, keeping them out of plaintext files.

## Example Usage
```python
from crypteria.cloud.dropbox_service import authenticate, upload_file

# Establish an authenticated Dropbox session
dbx = authenticate()

# Upload an encrypted file to the root directory
cloud_file_id = upload_file("/tmp/local_encrypted_payload.bin", "/remote_file.bin")
```
