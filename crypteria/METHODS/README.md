# methods

## Purpose
The `methods` module is the central orchestrator of Crypteria. It provides the high-level application programming interface (API) that dictates the lifecycle of a file moving between the local filesystem and the cloud.

## Key Modules
- **`upload.py`**: Coordinates the upload workflow. It accepts a local file, runs it through size/type validations, encrypts the payload, logs the metadata to the local DB, and pushes the ciphertext to a cloud provider.
- **`download.py`**: Coordinates the download workflow. It fetches ciphertext from a cloud provider based on a database ID record, pulls the correct decryption key from the OS keyring, and reconstructs the plaintext file locally.

## Interaction with Other Modules
`methods` acts as the bridge connecting the entire package:
- **`utils`**: For payload validation and temporary path resolution.
- **`security`**: For invoking encryption before network dispatch, and decryption after network retrieval.
- **`dbs`**: For storing and querying file metadata state.
- **`cloud`**: For the final push or pull of ciphertext over the network.

## Example Usage
```python
from pathlib import Path
from crypteria.methods.upload import upload_document

# Upload a local file to Dropbox securely
upload_document(Path("C:/my_documents/secret.pdf"), provider="Dropbox")
```
