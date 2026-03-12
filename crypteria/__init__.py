__version__ = "1.0.0"
__author__ = "DERRADJI SENANI"
__license__ = "MIT"


# Core functions - these are the main entry points for developers
from crypteria.main import (
    # High-level API functions
    upload,
    download,
    encrypt,
    decrypt,
    init_db,
    list_files,
    # authenticate_cloud,
    # Classes
    UploadDatacloud,
    DownloadDatacloud,
    # Modules (for advanced usage)
    methods,
    security,
    dbs,
    cloud,
    services,
    utils,
)


# Re-export commonly used items for easier access
from crypteria.security.crypto import (
    UniversalCrypto,
    CryptoMode,
    KeyManager,
)

from crypteria.dbs.database import SessionLocal

from crypteria.services.logs_service import logger

# Lazy database initialization flag
_db_initialized = False


def __getattr__(name):
    """
    Lazy import to avoid circular imports and speed up package loading.
    """
    if name == "main":
        import crypteria.main as main_module
        return main_module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """
    Return list of available attributes for tab-completion.
    """
    return [
        # Version
        "__version__",
        "__author__",
        "__license__",
        # Main functions
        "upload",
        "download",
        "encrypt",
        "decrypt",
        "init_db",
        "list_files",
        "authenticate_cloud",
        # Classes
        "UploadDatacloud",
        "DownloadDatacloud",
        # Modules
        "methods",
        "security",
        "dbs",
        "cloud",
        "services",
        "utils",
        "main",
        # Utilities
        "UniversalCrypto",
        "CryptoMode",
        "KeyManager",
        "SessionLocal",
        "logger",
    ]
