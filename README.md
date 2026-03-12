# Crypteria SDK

## Distribution Files

The `dist/` directory contains the built distribution packages for the Crypteria SDK.

### Types of Distributions
- **Wheel (`.whl`)**: Built distribution format for Python
- **Source Distribution (`.tar.gz`)**: Source code distribution

## Info Files

The `crypteria.egg-info/` directory contains metadata about the package:

| File | Description |
|------|-------------|
| `PKG-INFO` | Package metadata (name, version, author, etc.) |
| `SOURCES.txt` | List of source files included |
| `dependency_links.txt` | Dependency links |
| `entry_points.txt` | Console scripts and entry points |
| `requires.txt` | Package requirements |
| `top_level.txt` | Top-level module names |

## Installation

Install from wheel:
```bash
pip install dist/crypteria-*.whl
```

Install from source:
```bash
pip install crypteria-*.tar.gz
```
