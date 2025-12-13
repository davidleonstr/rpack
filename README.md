# RPack

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

RPack is a Python library for creating, reading, and managing compressed binary resource packages. It provides an efficient way to bundle multiple files into a single compressed archive with integrity verification and virtual file system support.

## Features

- **Multiple Compression Methods**: Support for zlib, lzma, or no compression
- **Integrity Verification**: SHA-256 hash verification for file contents
- **Virtual File System**: Navigate packed files as if they were in a directory structure
- **PyInstaller Compatible**: Works seamlessly with frozen executables
- **Simple API**: Easy-to-use builder and reader interfaces
- **File Metadata**: Stores original size, compressed size, and hash information

## Installation

```bash
pip install git+https://github.com/davidleonstr/rpack.git
```

## Quick Start

### Creating a Package

```python
from rpack import RPackBuilder

# Create a package from a directory
builder = RPackBuilder(
    input_path='./my_resources',
    output_path='resources.rpack',
    compression='zlib'  # Options: 'zlib', 'lzma', 'none'
)
builder.build()
```

### Reading from a Package

```python
from rpack import ResourcePack

# Open an existing package
pack = ResourcePack('resources.rpack', compression='zlib')

# Read a file as bytes
data = pack.get('path/to/file.txt')

# Check if file exists
if pack.exists('config.json'):
    config_data = pack.get('config.json')

# List directory contents
files = pack.listdir('assets/images')

# Close when done
pack.close()
```

## Command Line Interface

RPack includes a command-line interface for common operations:

### Create a Package

```bash
# Using folder
python -m rpack create --input <input_directory> --output <output_file> [OPTIONS]

# Using files
python -m rpack create -f <input_files_separated_with_space> -o <output_file>

# Short form
python -m rpack create -i ./resources -o resources.rpack

# With compression options
python -m rpack create -i ./data -o data.rpack -c lzma -l 9
```

**Options:**
- `--files, -f`: Input files
- `--input, -i`: Input folder or file (Required if no files are given)
- `--output, -o`: Output .rpack file (required)
- `--compression, -c`: Compression method: zlib, lzma, none (default: zlib)
- `--compression-level, -l`: Compression level (default: 6)

### List Package Contents

```bash
python -m rpack list <package_file> [OPTIONS]

# Example
python -m rpack list resources.rpack
python -m rpack list resources.rpack -c lzma
```

**Options:**
- `--compression, -c`: Compression method used in the package (default: zlib)

Example output:
```
Content of resources.rpack:
Folder: assets/
  Folder: images/
    File: logo.png (45.32 KB)
    File: background.jpg (128.45 KB)
  File: config.json (2.15 KB)
```

### Extract Package Contents

```bash
python -m rpack extract <package_file> [OPTIONS]

# Example
python -m rpack extract resources.rpack
python -m rpack extract resources.rpack -o ./output -c lzma
```

**Options:**
- `--output, -o`: Output folder (default: extracted)
- `--compression, -c`: Compression method used in the package (default: zlib)

## API Reference

### RPackBuilder

Creates compressed resource packages from files or directories.

```python
from rpack import RPackBuilder

builder = RPackBuilder(
    input_path='./resources',      # Source directory or file
    output_path='output.rpack',     # Destination package file
    compression='zlib',             # Compression method
    verbose=True                    # Print progress messages
)
builder.build()
```

**Parameters:**
- `input_path` (str): Path to source directory or file
- `output_path` (str): Path for the output package file
- `compression` (CompressionType): Compression method ('zlib', 'lzma', 'none'),
- `files` (list): specific files,
- `verbose` (bool): Enable/disable progress output (default: True)

### ResourcePack

Reads and accesses files from compressed resource packages.

```python
from rpack import ResourcePack

pack = ResourcePack(
    path='resources.rpack',
    compression='zlib'
)

# Get file contents
data = pack.get('file.txt', verify_hash=True)

# Check existence
exists = pack.exists('path/to/file')

# List directory
files = pack.listdir('assets')

# Check type
is_file = pack.isfile('config.json')
is_dir = pack.isdir('assets')

# Access virtual file system
vfs = pack.vfs

# Close the package
pack.close()
```

**Methods:**
- `get(path, verify_hash=False)`: Retrieve file contents as bytes
- `exists(path)`: Check if a file or directory exists
- `listdir(path='')`: List contents of a directory
- `isfile(path)`: Check if path is a file
- `isdir(path)`: Check if path is a directory
- `close()`: Close the package file handle

### VirtualFS

Provides a virtual file system interface for navigating package contents.

```python
# Access through ResourcePack
pack = ResourcePack('resources.rpack')
vfs = pack.vfs

# Check existence
vfs.exists('path/to/file')

# List directory
items = vfs.listdir('assets')

# Check types
vfs.isfile('config.json')
vfs.isdir('assets')
```

### Compressor

Handles compression and decompression operations.

```python
from rpack.compressor import Compressor

compressor = Compressor(method='zlib', level=6)

# Compress data
compressed = compressor.compress(b'Hello, World!')

# Decompress data
original = compressor.decompress(compressed)
```

## Package Format

RPack files use a binary format with the following structure:

```
[Magic Header: "RPACKv1"] (7 bytes)
[Index Size] (4 bytes, little-endian)
[Compressed Index] (JSON metadata)
[Compressed File Data 1]
[Compressed File Data 2]
...
```

### Index Structure

The index is a JSON object containing metadata for each file:

```json
{
  "path/to/file.txt": {
    "offset": 0,
    "size_original": 1024,
    "size_compressed": 512,
    "hash": "sha256_hash_here",
    "compression": "zlib"
  }
}
```

## Compression Methods

RPack supports multiple compression algorithms:

- **zlib**: Fast compression with good ratio (default)
- **lzma**: Higher compression ratio, slower
- **none**: No compression (store only)

## Use Cases

- **Game Assets**: Bundle game resources into a single file
- **Application Resources**: Package UI assets, images, and configurations
- **Data Distribution**: Compress and distribute large datasets
- **Protected Content**: Bundle files with integrity verification
- **PyInstaller Apps**: Include resources in frozen executables

## Advanced Usage

### Custom Compression Levels

```python
builder = RPackBuilder(
    input_path='./data',
    output_path='data.rpack',
    compression='zlib',
    level=9  # Maximum compression
)
builder.build()
```

### Hash Verification

```python
pack = ResourcePack('resources.rpack')

# Verify file integrity on read
data = pack.get('important.dat', verify_hash=True)
```

### Working with Binary Files

```python
# Read binary data
image_data = pack.get('images/logo.png')

# Save to file
with open('extracted_logo.png', 'wb') as f:
    f.write(image_data)
```

## Error Handling

```python
from rpack import ResourcePack

try:
    pack = ResourcePack('missing.rpack')
except FileNotFoundError:
    print("Package file not found")

try:
    data = pack.get('nonexistent.txt')
except FileNotFoundError:
    print("File not found in package")

try:
    data = pack.get('file.txt', verify_hash=True)
except ValueError:
    print("File integrity check failed")
```

## PyInstaller Integration

RPack automatically handles PyInstaller's `_MEIPASS` directory for bundled resources:

```python
# Works in both development and frozen environments
pack = ResourcePack('resources.rpack')
data = pack.get('config.json')
```

## Performance Tips

1. **Choose appropriate compression**: Use `zlib` for balanced performance, `lzma` for maximum compression, `none` for speed
2. **Disable hash verification** unless integrity is critical
3. **Keep packages under 100MB** for optimal performance
4. **Use batch operations** when extracting multiple files
