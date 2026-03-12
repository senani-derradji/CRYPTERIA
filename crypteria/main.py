from pathlib import Path
from typing import Optional, Union

from crypteria import methods
from crypteria import security
from crypteria import dbs
from crypteria import cloud
from crypteria import services
from crypteria import utils

from crypteria.methods.upload import UploadDatacloud
from crypteria.methods.download import DownloadDatacloud

from crypteria.security.crypto import (
    UniversalCrypto,
    CryptoMode,
    KeyManager,
    encrypt_file as crypto_encrypt_file,
    decrypt_file as crypto_decrypt_file,
)
from crypteria.security.encryption import (
    load_key,
    encrypt_data,
    decrypt_data,
)

from crypteria.cloud.google_drive_service import (
    authenticate as authenticate_drive,
    upload_to_drive,
    list_files as list_drive_files,
    download_file as download_from_drive,
)

from crypteria.dbs.database import engine, Base, SessionLocal
from crypteria.dbs.crud import (
    get_all_files,
    get_file_by_id,
    create_file_record,
)

from crypteria.services.logs_service import logger

from crypteria.utils.general_utils import PathManager


_db_initialized = False


def _ensure_db_initialized() -> None:
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


def upload(
    file_path: Union[str, Path],
    cloud_provider: str = "google_drive",
    use_advanced_encryption: bool = True,
) -> Optional[int]:
    _ensure_db_initialized()

    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False

    uploader = UploadDatacloud(file_path, use_advanced_encryption)
    result = uploader.upload_encrypted_file(cloud_provider)

    if result:
        logger.info(f"Successfully uploaded {file_path.name}")
    else:
        logger.error(f"Failed to upload {file_path.name}")

    return result


def download(
    file_id: int,
    use_advanced_encryption: bool = True,
) -> Optional[Path]:

    _ensure_db_initialized()

    downloader = DownloadDatacloud(file_id, use_advanced_encryption=use_advanced_encryption)
    result = downloader.download_decrypted_data()

    if result:
        logger.info(f"Successfully downloaded file ID: {file_id}")
    else:
        logger.error(f"Failed to download file ID: {file_id}")

    return result


def encrypt(
    input_path: Union[str, Path],
    key: Optional[bytes] = None,
    mode: CryptoMode = CryptoMode.GCM,
    store_key: bool = True,
) -> tuple[Path, bytes, bytes]:

    input_path = Path(input_path)

    key_manager = KeyManager()
    if key is None:
        key = key_manager.generate_key(mode)
        if store_key:
            key_manager.store_key(key, "master_key")
            logger.info("Generated and stored new encryption key in keyring")

    crypto = UniversalCrypto(key, mode)
    encrypted_path, nonce = crypto_encrypt_file(input_path, key, mode)

    logger.info(f"File encrypted: {input_path} -> {encrypted_path}")

    return encrypted_path, nonce, key


def decrypt(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    key: Optional[bytes] = None,
    nonce: Optional[bytes] = None,
    mode: CryptoMode = CryptoMode.GCM,
) -> Path:
    input_path = Path(input_path)

    if key is None:
        key_manager = KeyManager()
        key = key_manager.get_key("master_key")
        if key is None:
            raise ValueError("Key is required for decryption. Either provide a key or encrypt a file first to store the key in keyring.")
        logger.info("Retrieved decryption key from keyring")

    if mode == CryptoMode.GCM and nonce is None:
        raise ValueError("Nonce is required for GCM decryption")

    crypto = UniversalCrypto(key, mode)
    decrypted_path = crypto_decrypt_file(input_path, key, nonce, mode)

    logger.info(f"File decrypted: {input_path} -> {decrypted_path}")

    return decrypted_path


def init_db() -> None:

    Base.metadata.create_all(engine)
    logger.info("Database initialized")


def list_files() -> list:
    _ensure_db_initialized()

    db = SessionLocal()
    try:
        files = get_all_files(db)
        return files
    finally:
        db.close()


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Crypteria - Secure File Encryption and Cloud Backup"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    upload_parser = subparsers.add_parser("upload", help="Upload an encrypted file")
    upload_parser.add_argument("file", help="File to upload")
    upload_parser.add_argument(
        "--provider", default="google_drive", help="Cloud provider (default: google_drive)"
    )

    download_parser = subparsers.add_parser("download", help="Download and decrypt a file")
    download_parser.add_argument("id", type=int, help="File ID to download")

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    encrypt_parser.add_argument("file", help="File to encrypt")
    encrypt_parser.add_argument("-o", "--output", help="Output file path")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    decrypt_parser.add_argument("file", help="File to decrypt")
    decrypt_parser.add_argument("-o", "--output", help="Output file path")
    decrypt_parser.add_argument("-k", "--key", required=True, help="Base64 encoded key")
    decrypt_parser.add_argument("-n", "--nonce", required=True, help="Base64 encoded nonce")

    subparsers.add_parser("list", help="List all stored files")

    subparsers.add_parser("init", help="Initialize database")

    args = parser.parse_args()

    if args.command == "upload":
        result = upload(args.file, args.provider)
        if result:
            print(f"Successfully uploaded! File ID: {result}")
            sys.exit(0)
        else:
            print("Upload failed")
            sys.exit(1)

    elif args.command == "download":
        result = download(args.id)
        if result:
            print(f"Successfully downloaded to: {result}")
            sys.exit(0)
        else:
            print("Download failed")
            sys.exit(1)

    elif args.command == "encrypt":
        import base64
        enc_file, nonce = encrypt(args.file, args.output)
        print(f"Encrypted: {enc_file}")
        print(f"Key (base64): {base64.b64encode(enc_file.key if hasattr(enc_file, 'key') else '').decode()}")
        print(f"Nonce (base64): {base64.b64encode(nonce).decode()}")

    elif args.command == "decrypt":
        import base64
        key = base64.b64decode(args.key)
        nonce = base64.b64decode(args.nonce)
        dec_file = decrypt(args.file, args.output, key, nonce)
        print(f"Decrypted: {dec_file}")

    elif args.command == "list":
        files = list_files()
        print(f"Total files: {len(files)}")
        for f in files:
            print(f"  ID: {f.id}, Name: {f.file_name}, Provider: {f.providor}, Action: {f.action}")

    elif args.command == "init":
        init_db()
        print("Database initialized")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
