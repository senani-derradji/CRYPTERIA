# 📝 Services Module

<p align="center">
  <i>Logging, observability, and background operations</i>
</p>

---

## Purpose

The `services` module contains background operations and daemons critical to Crypteria's observability, health tracking, and debugging. It is designed to track operations natively without ever leaking sensitive plaintext data or keys.

## Key Modules

| Module | Description |
|--------|-------------|
| [`logs_service.py`](logs_service.py) | A central configuration wrapper around the Python standard `logging` library. It sets up file handlers with formatted timestamps, caller modules, and severity tiers (INFO, WARNING, ERROR). |

## Interaction with Other Modules

- **Across the package**: Every other module (`cloud`, `utils`, `dbs`, `methods`, `security`) imports the configured `logger` from this service. This ensures a unified logging format.
- **`utils`**: The logger uses `utils.PathManager` to determine safe, writable OS-specific directories for log files (e.g., `%APPDATA%` on Windows or `~/.local/share` on Linux).

## Example Usage

```python
from crypteria.services.logs_service import logger

def my_crypt_function():
    logger.info("Starting a new background task.")
    try:
        # Do work
        pass
    except Exception as e:
        logger.error(f"Failed to execute task: {e}")
```

---

<p align="center">
  <a href="../../README.md">← Back to Main README</a>
</p>
