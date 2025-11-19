import os, sys, logging, ctypes
from SDK.general_utils import PathManager


app_dir = PathManager.get_appdata_path()

log_path = app_dir / "Lo" / "logs.log"
os.makedirs(log_path.parent, exist_ok=True)
log_path.touch(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if sys.platform.startswith("win"):

    FILE_ATTRIBUTE_HIDDEN = 0x02
    result = ctypes.windll.kernel32.SetFileAttributesW(str(log_path), FILE_ATTRIBUTE_HIDDEN)

    if result == 0:
        logger.warning("Failed to hide log file on Windows.")

    try:
        os.chmod(log_path, 0o600)
    except Exception as e:
        logger.warning(f"chmod failed on Windows: {e}")

elif sys.platform.startswith("linux") or sys.platform == "darwin":
    os.chmod(log_path, 0o600)
