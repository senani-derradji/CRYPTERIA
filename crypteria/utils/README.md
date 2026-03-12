# utils

## Purpose
The `utils` module provides foundational helper functions, data validation schemas, and environment-aware path management. It acts as the backbone that keeps Crypteria consistent, robust, and functional across different operating systems.

## Key Modules
- **`general_utils.py`**:
  - **`PathManager`**: Dynamically resolves cross-platform storage. It finds `%APPDATA%` / `~/.local/share` for persistent storage and `%TEMP%` / `/tmp` for volatile ciphertext processing.
  - Contains functions like `load_data()`, `get_os_type()`, and chunking utilities for large `keyring` operations.
- **`validation.py`**: Implements `pydantic` schemas. It enforces maximum file sizes, verifies file existence, and ensures extensions match a comprehensive whitelist before allowing expensive encryption processes.

## Interaction with Other Modules
- **`methods`**: Uses validators to sanitize inputs before orchestrating uploads.
- **`dbs` / `services`**: Depend on `PathManager` to know where to safely save SQLite files and log outputs without throwing OS permission errors.

## Example Usage
```python
from crypteria.utils.general_utils import PathManager
from crypteria.utils.validation import DataPayload, is_valid_file_type
from pathlib import Path

# Get a safe path for writing temporary SDK files
temp_dir = PathManager.get_temp_folder("MyTempOperations")

# Validate a payload structure using Pydantic
payload = DataPayload(file_path=Path("document.pdf"))
```
