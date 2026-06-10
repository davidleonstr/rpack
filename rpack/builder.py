import json
import struct
from pathlib import Path
from typing import Dict, List, Optional, Union
from .compressor import Compressor, CompressionType
from .vfs import VirtualFS
from .core import MAGICHEADER
from .utils import GenericFile, CalculatedHash

class RPackBuilder:
    """
    Builds a binary resource package (RPack) from files in a directory or specific files.

    The RPack format stores files in a compressed binary structure, including
    metadata such as compression type, file sizes, and SHA-256 hashes. This
    class handles file discovery, compression, and package writing.

    Attributes:
        outputPath (Path): The destination file path for the generated package.
        inputPath (Optional[Path]): The source directory or file to pack (optional with files param).
        compression (CompressionType): The compression method used for all files.
        index (Dict[str, dict]): Metadata index for the packed files.
        specificFiles (Optional[List[str]]): List of specific files to include.
        compressor (Compressor): Internal compressor instance for file data.
        verbose (bool): Whether to print progress messages during the build.
    """

    def __init__(
            self,
            outputPath: str,
            inputPath: Optional[str] = None,
            compression: CompressionType = 'zlib',  # type: ignore
            files: Optional[Union[List[str], str]] = None,
            **kwargs,
        ):
        """
        Initialize the RPackBuilder with input and output paths and compression settings.

        Args:
            outputPath (str): Path to the output RPack file.
            inputPath (Optional[str]): Path to the source directory or file. 
                Required when not using 'files' parameter, or used as base path for relative files.
            compression (CompressionType, optional): Compression method. Defaults to 'zlib'.
            files (Optional[Union[List[str], str]], optional): Specific files to include. 
                Can be a list of paths or a space-separated string. 
                If paths are relative, they're resolved against inputPath (if provided) or current directory.
            **kwargs: Additional arguments for the compressor or verbosity.
        """
        self.outputPath = Path(outputPath)
        self.inputPath = Path(inputPath) if inputPath else None
        self.compression = compression
        self.index: Dict[str, dict] = {}
        self.compressor = Compressor(method=compression, **kwargs)
        self.verbose = kwargs.get('verbose', True)

        # Parse specific files if provided
        if files:
            if isinstance(files, str):
                # Split space-separated string
                self.specificFiles = [f.strip() for f in files.split() if f.strip()]
            else:
                self.specificFiles = files
        else:
            self.specificFiles = None

        # Validation
        if not self.specificFiles and not self.inputPath:
            raise ValueError('Either inputPath or files must be provided')
        
        if self.inputPath and not self.specificFiles and not self.inputPath.exists():
            raise FileNotFoundError(f'Input path not found: {inputPath}')

    def print(self, *kargs) -> None:
        """
        Print messages to the console if verbose mode is enabled.

        Args:
            *kargs: Arguments passed to the built-in `print` function.
        """
        if self.verbose:
            print(*kargs)

    def build(self) -> None:
        """
        Build the RPack file by scanning, compressing, and writing all data.

        Steps:
            1. Collect files recursively from the input path or use specific files.
            2. Compress each file and store its metadata.
            3. Write the RPack file with header, index, and compressed contents.

        Raises:
            FileNotFoundError: If the input path or specific files do not exist.
        """
        sourceFesc = ', '.join(self.specificFiles[:3]) if self.specificFiles else str(self.inputPath)
        if self.specificFiles and len(self.specificFiles) > 3:
            sourceFesc += f' (and {len(self.specificFiles) - 3} more)'
        
        self.print(f'Building {self.outputPath} from {sourceFesc}...')

        files = self.collectFiles()
        self.print(f'Found {len(files)} files')

        compressedData = []
        currentOffset = 0

        for fileInfo in files:
            filePath, virtualPath = fileInfo
            
            self.print(f'Compressing: {virtualPath}')

            originalData = GenericFile(filePath)
            originalData.readType = 'rb'
            originalData = originalData.readFile()

            compressed = self.compressor.compress(originalData)

            self.index[virtualPath] = {
                'offset': currentOffset,
                'size_original': len(originalData),
                'size_compressed': len(compressed),
                'hash': CalculatedHash(originalData).value,
                'compression': self.compression
            }

            compressedData.append(compressed)
            currentOffset += len(compressed)

        self.writeRpack(compressedData)
        self.print(f'Created file: {self.outputPath}')
        self.print(f'Total size: {self.outputPath.stat().st_size} bytes')

    def collectFiles(self) -> List[tuple]:
        """
        Recursively collect all files from the input path or use specific files.

        Returns:
            list: A sorted list of tuples (Path, virtualPath) representing files to be packed
                and their virtual paths in the archive.
        """
        if self.specificFiles:
            # Use specific files provided
            files = []
            for fileStr in self.specificFiles:
                filePath = Path(fileStr)
                
                # If path is relative, resolve against inputPath or current directory
                if not filePath.is_absolute():
                    if self.inputPath:
                        filePath = self.inputPath / filePath
                    else:
                        filePath = Path.cwd() / filePath
                
                if not filePath.exists():
                    raise FileNotFoundError(f'Specified file not found: {fileStr}')
                
                if not filePath.is_file():
                    raise ValueError(f'Path is not a file: {fileStr}')
                
                # Try to make it relative to inputPath if possible
                if self.inputPath:
                    try:
                        virtualPath = filePath.relative_to(self.inputPath)
                        virtualPath = VirtualFS.normalizePath(str(virtualPath))
                    except ValueError:
                        # File is outside inputPath, use the original fileStr
                        virtualPath = VirtualFS.normalizePath(fileStr)
                else:
                    # No inputPath, use the fileStr as-is
                    virtualPath = VirtualFS.normalizePath(fileStr)
                
                files.append((filePath, virtualPath))
            
            return sorted(files, key=lambda x: x[1])
        
        # Standard behavior: collect all files from inputPath
        if not self.inputPath:
            raise ValueError('inputPath is required when files are not specified')
        
        if self.inputPath.is_file():
            relPath = VirtualFS.normalizePath(self.inputPath.name)
            return [(self.inputPath, relPath)]

        files = []
        
        for item in self.inputPath.rglob('*'):
            if item.is_file():
                relPath = item.relative_to(self.inputPath)
                virtualPath = VirtualFS.normalizePath(str(self.inputPath / relPath))
                files.append((item, virtualPath))
        
        return sorted(files, key=lambda x: x[1])

    def writeRpack(self, compressedData: list) -> None:
        """
        Write the final RPack file, including header, index, and compressed data.

        Args:
            compressedData (list): List of byte sequences representing compressed files.
        """
        with open(self.outputPath, 'wb') as f:
            # Write file header
            f.write(MAGICHEADER)

            # Serialize and compress the file index
            indexJson = json.dumps(self.index, indent=None)
            indexCompressed = self.compressor.compress(indexJson.encode('utf-8'))

            # Write index length and data
            f.write(struct.pack('<I', len(indexCompressed)))
            f.write(indexCompressed)

            # Write each compressed file sequentially
            for data in compressedData:
                f.write(data)

__all__ = ['RPackBuilder']