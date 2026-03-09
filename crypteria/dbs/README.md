# dbs (Database)

## Purpose
The `dbs` module manages the local state tracking for Crypteria. The library uses a local-first metadata strategy: the cloud holds the encrypted bytes, the OS keyring holds the decryption keys, and the `dbs` module holds the relational map connecting them.

## Key Modules
- **`models.py`**: Defines the SQLAlchemy database schema (typically SQLite). The core `File` table stores non-sensitive metadata: the `file_id_enc` (linking to the OS keyring), the original `file_name`, the `file_type`, the size, and the `providor_name`.
- **`database.py`**: Configures the SQLAlchemy `engine`, session makers, and declarative base. It uses `utils.PathManager` to dynamically locate the AppData/LocalShare safe folder for the database file.
- **`crud.py`**: Provides Create, Read, Update, and Delete functions used to interact with the database efficiently.

## Interaction with Other Modules
- **`methods`**: `dbs.crud` functions are called by `methods` during the initial stages of an upload to record metadata, and during the initial stages of a download to retrieve the target cloud provider and file attributes.
- **`security`**: Metadata relies on keys managed by `security` for correlating database records with physical encrypted files in the cloud.

## Example Usage
```python
from crypteria.dbs.database import SessionLocal
from crypteria.dbs.crud import get_file_by_id

db = SessionLocal()

file_record = get_file_by_id(db, "internal_file_id_123")
print(file_record.providor_name)
```
