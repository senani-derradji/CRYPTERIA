import os
import platform
from pathlib import Path

def get_temp_folder(folder: Path = "CryperaTMP"):
    system = platform.system().lower()

    if "android" in platform.platform().lower():system = "android"
    if system == "windows": temp = os.environ.get("TEMP") or os.environ.get("TMP") or "C:\\Windows\\Temp" ; return Path(temp)
    if system == "linux": return Path("/tmp")
    if system == "darwin": return Path("/tmp")
    if system == "android": return Path("/data/local/tmp")

    return Path("/tmp")


# if not (get_temp_folder() / "CrypteriaTMP").exists():
#     print("CRYPTERIA TMP FOLDER DEOS NOT EXISTS !")
print(get_temp_folder())
if get_temp_folder(folder="CrypteriaTMP").exists():
    print("DEOS NOT EXISTS")