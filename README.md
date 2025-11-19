# Crypteria SDK – Minimal README

## 🎯 Target
- Provide a lightweight, secure SDK for communication with the Cloud / Core Server.
- Enable end-to-end encryption (E2EE) on client-side.
- Support upload/download operations for external applications.

## 🔐 Security Practices
- Encrypt all sensitive data before sending.
- Keep encryption keys local; never send them to the server.
- Support key rotation when needed.
- Minimal logging; never log sensitive information.

## 🗄️ Database Security
- Encrypt all database values before storing.
- Save database in a secure system path (e.g., `%APPDATA%/Crypteria` on Windows, `$HOME/.local/share/Crypteria` on Linux).
- Store **all metadata locally only**: file IDs, types, sizes, etc. never leave the system.
- file protection: hidden + permissions.
- Data integrity verification (checksum or hash). (soon ..)

## ☁️ Cloud Integration
- **Personal / Small Users:** Google Drive
  - Uses `credentials.json` to generate token
  - Token saved securely in system Keyring
- **Developers / Enterprises:** Multiple cloud providers (planned, to be added soon)
- Data sent to cloud is **encrypted (zero-knowledge)**: cloud cannot read file content
- Cloud only stores encrypted file content, no metadata

## 🧩 Encryption & Cloud Architecture
```
Client-Side (SDK)
│
├─ Layer 1: Data Encryption Key (DEK) – Fernet/AES
│   • Encrypts all files before sending
│
Core Server (Optional Encryption Layer)
│
├─ Layer 2: Server-Side Encryption (optional)
│   • Adds extra protection before cloud upload
│
Cloud Storage (Encrypted, Zero-Knowledge)
│   • Stores encrypted file content only
│
Local Encrypted DB
│   • Stores all metadata: file_id, type, size, checksum, etc.
│
Client retrieves data → Core Server decrypts Layer 2 (Optional) → SDK decrypts Layer 1 → Original data
```

## 🧩 SDK Structure
- Services: Encryption & Security / Validation / Requests / Cloud / DataBase
- Modular: easy to add Compression, Proxy, or other Cloud providers
- Complete separation between SDK and Core Server

## 📦 What to Add
- Unified interface for: upload, download, delete, list
- Optional caching layer
- Key management system for local keys
- Unified error handling
- Secure logging system

## 🚀 Final Goal
Lightweight, secure, extensible SDK ready for integration in any external application.
