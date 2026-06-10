import json
import struct
import sys
from pathlib import Path
from typing import BinaryIO, Optional
from .compressor import Compressor, CompressionType
from .vfs import VirtualFS
from .utils import CalculatedHash
from .core import MAGICHEADER

class ResourcePack:
    """
    Represents a read-only resource package (RPack) that stores and retrieves files
    from a compressed binary archive.

    The `ResourcePack` class provides methods for reading binary, text, and JSON
    files directly from a packed archive, using an internal virtual file system
    (VFS) and optional hash verification.

    Attributes:
        path (Path): The path to the RPack file.
        fp (Optional[BinaryIO]): The open file handle for reading the RPack.
        index (dict): Metadata index of all files within the pack.
        _vfs (Optional[VirtualFS]): Virtual file system instance based on the index.
        dataOffset (int): Byte offset where file data begins in the archive.
        compression (CompressionType): Compression method used in the pack.
        compressor (Compressor): Internal compressor for decompressing file data.
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
        self.path = self.resolvePath(path)
        self.fp: Optional[BinaryIO] = None
        self.index = {}
        self._vfs: Optional[VirtualFS] = None
        self.dataOffset = 0
        self.compression = compression
        self.compressor = Compressor(method=compression, **kwargs)
        
        self.loadIndex()

    def resolvePath(self, path: str) -> Path:
        """
        Resolve the correct path for the RPack file.

        If running in a frozen executable (e.g., PyInstaller), the method attempts
        to locate the resource inside the bundled environment.

        Args:
            path (str): Path to resolve.

        Returns:
            Path: The resolved file path.
        """
        pathObj = Path(path)
        
        if pathObj.exists():
            return pathObj
        
        if getattr(sys, 'frozen', False):
            meipass = Path(sys._MEIPASS)
            frozenPath = meipass / path
            if frozenPath.exists():
                return frozenPath
        
        return pathObj

    def loadIndex(self) -> None:
        """
        Load and decompress the metadata index from the RPack file.

        Raises:
            ValueError: If the file does not contain a valid RPack header.
        """
        self.fp = open(self.path, 'rb')

        magic = self.fp.read(len(MAGICHEADER))
        if magic != MAGICHEADER:
            raise ValueError('Invalid file format')

        indexSizeBytes = self.fp.read(4)
        indexSize = struct.unpack('<I', indexSizeBytes)[0]

        indexCompressed = self.fp.read(indexSize)
        indexJson = self.compressor.decompress(indexCompressed)
        self.index = json.loads(indexJson.decode('utf-8'))

        self.dataOffset = self.fp.tell()
        self._vfs = VirtualFS(self.index)

    def get(self, path: str, verifyHash: bool = False) -> bytes:
        """
        Retrieve and decompress a file from the RPack.

        Args:
            path (str): The virtual path to the file within the pack.
            verifyHash (bool, optional): Whether to verify file integrity using SHA-256. Defaults to False.

        Returns:
            bytes: The raw (decompressed) file data.

        Raises:
            FileNotFoundError: If the requested file does not exist in the pack.
            ValueError: If hash verification fails.
        """
        path = VirtualFS.normalizePath(path)
        
        if path not in self.index:
            raise FileNotFoundError(f'File not found: {path}')
        
        info = self.index[path]
        offset = self.dataOffset + info['offset']
        self.fp.seek(offset)
        compressedData = self.fp.read(info['size_compressed'])
        
        data = self.compressor.decompress(compressedData)
        
        if verifyHash:
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

    def listDir(self, path: str = '') -> list:
        """
        List all entries (files and directories) in a given virtual directory.

        Args:
            path (str, optional): Directory path to list. Defaults to root ('').

        Returns:
            list: A list of entries (names) in the directory.
        """
        return self._vfs.listDir(path)

    def isFile(self, path: str) -> bool:
        """
        Check if the given virtual path is a file.

        Args:
            path (str): Path to check.

        Returns:
            bool: True if it is a file, False otherwise.
        """
        return self._vfs.isFile(path)

    def isDir(self, path: str) -> bool:
        """
        Check if the given virtual path is a directory.

        Args:
            path (str): Path to check.

        Returns:
            bool: True if it is a directory, False otherwise.
        """
        return self._vfs.isDir(path)

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
        if self.fp:
            self.fp.close()
            self.fp = None

__all__ = ['ResourcePack']