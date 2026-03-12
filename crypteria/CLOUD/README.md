# cloud

## Purpose
The `cloud` module serves as the adapter layer that communicates with external cloud APIs. Because Crypteria handles encryption locally, this module strictly deals with uploading and downloading **ciphertext** (encrypted data files). It has no knowledge of the file's contents, only its binary payload and intended destination.

## Key Modules
- **`google_drive_service.py`**: Manages OAuth2 authorization with Google using `google-auth-oauthlib`. Uses `MediaFileUpload` and `MediaIoBaseDownload` to handle chunked, resumable I/O streams for large files, keeping memory overhead low.
- **`drive.py`**: Alternative Google Drive service with enhanced encryption for OAuth credentials.

## Interaction with Other Modules
- **`methods`**: The primary caller of this module. `methods` dictates when and what to upload or download.
- **`security`**: The `cloud` module uses secure `keyring` operations provided by `security` to safely stash OAuth access tokens locally, keeping them out of plaintext files.

## Example Usage
```python
from crypteria.cloud.google_drive_service import authenticate, upload_to_drive

# Establish an authenticated Google Drive session
creds = authenticate()

# Upload an encrypted file to Google Drive
file_id = upload_to_drive("/tmp/local_encrypted_payload.bin")
```
