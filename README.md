# Crypteria

<p align="center">
  <a href="https://pypi.org/project/crypteria/">
    <img src="https://img.shields.io/pypi/v/crypteria.svg" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/crypteria/">
    <img src="https://img.shields.io/pypi/py_versions/crypteria.svg" alt="Python Versions">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/crypteria.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/senani-derradji/crypteria/actions">
    <img src="https://github.com/senani-derradji/crypteria/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <a href="https://codecov.io/gh/senani-derradji/crypteria">
    <img src="https://codecov.io/gh/senani-derradji/crypteria/branch/main/graph/badge.svg" alt="Coverage">
  </a>
</p>

<p align="center">
  <strong>A powerful local-first encryption and secure cloud-storage management toolkit in Python.</strong>
</p>

---

Crypteria is a secure file encryption and cloud backup library for Python. It provides a simple yet powerful API to encrypt files using industry-standard AES-256-GCM encryption, store encryption keys securely in the system keyring, and synchronize encrypted files to cloud storage providers like Google Drive.

## ⭐ Key Features

- **🔐 AES-256-GCM Encryption** — Military-grade authenticated encryption
- **🔑 System Keyring Integration** — Keys stored securely in OS keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- **☁️ Google Drive Support** — Built-in cloud storage integration
- **🗄️ SQLite Database** — Local metadata storage for file tracking
- **📝 Comprehensive Logging** — Detailed operation logs for auditing
- **✅ Integrity Verification** — SHA-256 file verification

## 📦 Installation

```bash
pip install crypteria
```

### From Source

```bash
git clone https://github.com/senani-derradji/crypteria.git
cd crypteria
pip install -e .
```

### Requirements

- Python 3.8+
- cryptography >= 45.0.0
- keyring >= 25.0.0
- google-api-python-client >= 2.0.0
- sqlalchemy >= 2.0.0

## 🚀 Quick Start

```python
import crypteria

# Encrypt a file locally
encrypted_file, nonce, key = crypteria.encrypt("secret.pdf")
print(f"Encrypted: {encrypted_file}")

# Decrypt the file
decrypted_file = crypteria.decrypt(encrypted_file, key=key, nonce=nonce)
print(f"Decrypted: {decrypted_file}")

# Upload to Google Drive (automatic encryption)
file_id = crypteria.upload("document.pdf", cloud_provider="google_drive")
print(f"Uploaded! File ID: {file_id}")

# Download and decrypt from Google Drive
downloaded = crypteria.download(file_id=file_id)
print(f"Downloaded: {downloaded}")
```

## 📁 Project Structure

```
crypteria/
├── crypteria/           # Main package
│   ├── cloud/          # Cloud storage integrations (Google Drive, Dropbox)
│   ├── dbs/            # Database and CRUD operations
│   ├── methods/        # Upload and download handlers
│   ├── security/       # Encryption and key management
│   ├── services/       # Logging and utilities
│   └── utils/          # General utilities
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## 📖 Documentation

Detailed documentation is available in [`crypteria/README.md`](crypteria/README.md), including:

- [Architecture Overview](crypteria/README.md#architecture)
- [Usage Examples](crypteria/README.md#usage-examples)
- [Security Design](crypteria/README.md#security-design)
- [Production Use Cases](crypteria/README.md#production-use-cases)
- [Configuration Guide](crypteria/README.md#configuration)
- [API Reference](crypteria/README.md#api-reference)

## 🛠️ Development Setup

```bash
# Clone the repository
git clone https://github.com/senani-derradji/crypteria.git
cd crypteria

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Senani Derradji**

- Email: derradji.senani.1@gmail.com
- GitHub: [@senani-derradji](https://github.com/senani-derradji)

---

<p align="center">
  Built with 🔒 for secure Python applications
</p>
