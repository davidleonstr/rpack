import json
import struct
import sys
from pathlib import Path
from typing import BinaryIO, Optional
from .compressor import Compressor, CompressionType
from .vfs import VirtualFS
from .utils import CalculatedHash
from .core import MAGIC_HEADER

class ResourcePack:
    """
    Represents a read-only resource package (RPack) that stores and retrieves files
    from a compressed binary archive.

    The `ResourcePack` class provides methods for reading binary, text, and JSON
    files directly from a packed archive, using an internal virtual file system
    (VFS) and optional hash verification.

    Attributes:
        path (Path): The path to the RPack file.
        _fp (Optional[BinaryIO]): The open file handle for reading the RPack.
        _index (dict): Metadata index of all files within the pack.
        _vfs (Optional[VirtualFS]): Virtual file system instance based on the index.
        _data_offset (int): Byte offset where file data begins in the archive.
        compression (CompressionType): Compression method used in the pack.
        _compressor (Compressor): Internal compressor for decompressing file data.
    """

    def __init__(
            self, 
            path: str, 
            compression: CompressionType = 'zlib',  # type: ignore
            **kwargs
        ):
        """
        Initialize and load an existing RPack archive.

        Args:
            path (str): Path to the RPack file.
            compression (CompressionType, optional): Compression method. Defaults to 'zlib'.
            **kwargs: Additional arguments passed to the compressor.
        """
        self.path = self._resolve_path(path)
        self._fp: Optional[BinaryIO] = None
        self._index = {}
        self._vfs: Optional[VirtualFS] = None
        self._data_offset = 0
        self.compression = compression
        self._compressor = Compressor(method=compression, **kwargs)
        
        self._load_index()

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve the correct path for the RPack file.

        If running in a frozen executable (e.g., PyInstaller), the method attempts
        to locate the resource inside the bundled environment.

        Args:
            path (str): Path to resolve.

        Returns:
            Path: The resolved file path.
        """
        path_obj = Path(path)
        
        if path_obj.exists():
            return path_obj
        
        if getattr(sys, 'frozen', False):
            meipass = Path(sys._MEIPASS)
            frozen_path = meipass / path
            if frozen_path.exists():
                return frozen_path
        
        return path_obj

    def _load_index(self) -> None:
        """
        Load and decompress the metadata index from the RPack file.

        Raises:
            ValueError: If the file does not contain a valid RPack header.
        """
        self._fp = open(self.path, 'rb')

        magic = self._fp.read(len(MAGIC_HEADER))
        if magic != MAGIC_HEADER:
            raise ValueError('Invalid file format')

        index_size_bytes = self._fp.read(4)
        index_size = struct.unpack('<I', index_size_bytes)[0]

        index_compressed = self._fp.read(index_size)
        index_json = self._compressor.decompress(index_compressed)
        self._index = json.loads(index_json.decode('utf-8'))

        self._data_offset = self._fp.tell()
        self._vfs = VirtualFS(self._index)

    def get(self, path: str, verify_hash: bool = False) -> bytes:
        """
        Retrieve and decompress a file from the RPack.

        Args:
            path (str): The virtual path to the file within the pack.
            verify_hash (bool, optional): Whether to verify file integrity using SHA-256. Defaults to False.

        Returns:
            bytes: The raw (decompressed) file data.

        Raises:
            FileNotFoundError: If the requested file does not exist in the pack.
            ValueError: If hash verification fails.
        """
        path = VirtualFS.normalize_path(path)
        
        if path not in self._index:
            raise FileNotFoundError(f'File not found: {path}')
        
        info = self._index[path]
        offset = self._data_offset + info['offset']
        self._fp.seek(offset)
        compressed_data = self._fp.read(info['size_compressed'])
        
        data = self._compressor.decompress(compressed_data)
        
        if verify_hash:
            calculated = CalculatedHash(data).value
            if calculated != info['hash']:
                raise ValueError(f'Hash does not match for {path}')
        
        return data

    def exists(self, path: str) -> bool:
        """
        Check if a file or directory exists in the virtual file system.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return self._vfs.exists(path)

    def listdir(self, path: str = '') -> list:
        """
        List all entries (files and directories) in a given virtual directory.

        Args:
            path (str, optional): Directory path to list. Defaults to root ('').

        Returns:
            list: A list of entries (names) in the directory.
        """
        return self._vfs.listdir(path)

    def isfile(self, path: str) -> bool:
        """
        Check if the given virtual path is a file.

        Args:
            path (str): Path to check.

        Returns:
            bool: True if it is a file, False otherwise.
        """
        return self._vfs.isfile(path)

    def isdir(self, path: str) -> bool:
        """
        Check if the given virtual path is a directory.

        Args:
            path (str): Path to check.

        Returns:
            bool: True if it is a directory, False otherwise.
        """
        return self._vfs.isdir(path)

    @property
    def vfs(self) -> VirtualFS:
        """
        Get the virtual file system (VFS) instance representing the RPack structure.

        Returns:
            VirtualFS: The virtual file system object.
        """
        return self._vfs

    def close(self) -> None:
        """
        Close the open file handle for the RPack.

        Should be called when the ResourcePack is no longer needed.
        """
        if self._fp:
            self._fp.close()
            self._fp = None

__all__ = ['ResourcePack']