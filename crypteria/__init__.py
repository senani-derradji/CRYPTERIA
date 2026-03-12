__version__ = "1.0.0"
__author__ = "DERRADJI SENANI"
__license__ = "MIT"


from crypteria.main import (
    upload,
    download,
    encrypt,
    decrypt,
    init_db,
    list_files,
    UploadDatacloud,
    DownloadDatacloud,
    methods,
    security,
    dbs,
    cloud,
    services,
    utils,
)


from crypteria.security.crypto import (
    UniversalCrypto,
    CryptoMode,
    KeyManager,
)

from crypteria.dbs.database import SessionLocal

from crypteria.services.logs_service import logger

_db_initialized = False


def __getattr__(name):
    if name == "main":
        import crypteria.main as main_module
        return main_module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return [
        "__version__",
        "__author__",
        "__license__",
        "upload",
        "download",
        "encrypt",
        "decrypt",
        "init_db",
        "list_files",
        "authenticate_cloud",
        "UploadDatacloud",
        "DownloadDatacloud",
        "methods",
        "security",
        "dbs",
        "cloud",
        "services",
        "utils",
        "main",
        "UniversalCrypto",
        "CryptoMode",
        "KeyManager",
        "SessionLocal",
        "logger",
    ]
