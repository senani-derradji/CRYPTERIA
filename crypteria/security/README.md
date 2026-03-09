# security

## Purpose
The `security` module provides the foundational cryptographic boundaries for Crypteria. It guarantees that data at rest (before hitting the cloud) and keys at rest (stored locally) are mathematically impenetrable.

## Key Modules
- **`encryption.py`**: Handles symmetric Fernet cryptography. It generates unique, URL-safe base64-encoded 32-byte keys, separating payloads into chunks to avoid memory limits, and encrypts/decrypts the data streams.
- **`sensetive.py` & `security_utils.py`**: Manages the integration with the host operating system's native secure enclave using the `keyring` library (Windows Credential Manager or Linux Secret Service API).

## Interaction with Other Modules
- **`methods`**: Acts as a strict middle-layer. `methods` passes plaintext into `security`, and `security` outputs ciphertext and an alias to the key.
- **`cloud` / `dbs`**: The `keyring` utilities process OAuth tokens for `cloud` and use `dbs` database IDs to retrieve specific encryption keys without ever returning the literal key to the caller.

## Example Usage
```python
from crypteria.security.encryption import encrypt_data, generate_key

# Generate a strong Fernet key
key = generate_key()

# Encrypt data locally
ciphertext = encrypt_data(b"My sensitive payload", key)
```
