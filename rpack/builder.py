import json
import struct
from pathlib import Path
from typing import Dict, List, Optional, Union
from .compressor import Compressor, CompressionType
from .vfs import VirtualFS
from .core import MAGIC_HEADER
from .utils import GenericFile, CalculatedHash

class RPackBuilder:
    """
    Builds a binary resource package (RPack) from files in a directory or specific files.

    The RPack format stores files in a compressed binary structure, including
    metadata such as compression type, file sizes, and SHA-256 hashes. This
    class handles file discovery, compression, and package writing.

    Attributes:
        output_path (Path): The destination file path for the generated package.
        input_path (Optional[Path]): The source directory or file to pack (optional with files param).
        compression (CompressionType): The compression method used for all files.
        index (Dict[str, dict]): Metadata index for the packed files.
        specific_files (Optional[List[str]]): List of specific files to include.
        _compressor (Compressor): Internal compressor instance for file data.
        _verbose (bool): Whether to print progress messages during the build.
    """

    def __init__(
            self,
            output_path: str,
            input_path: Optional[str] = None,
            compression: CompressionType = 'zlib',  # type: ignore
            files: Optional[Union[List[str], str]] = None,
            **kwargs,
        ):
        """
        Initialize the RPackBuilder with input and output paths and compression settings.

        Args:
            output_path (str): Path to the output RPack file.
            input_path (Optional[str]): Path to the source directory or file. 
                Required when not using 'files' parameter, or used as base path for relative files.
            compression (CompressionType, optional): Compression method. Defaults to 'zlib'.
            files (Optional[Union[List[str], str]], optional): Specific files to include. 
                Can be a list of paths or a space-separated string. 
                If paths are relative, they're resolved against input_path (if provided) or current directory.
            **kwargs: Additional arguments for the compressor or verbosity.
        """
        self.output_path = Path(output_path)
        self.input_path = Path(input_path) if input_path else None
        self.compression = compression
        self.index: Dict[str, dict] = {}
        self._compressor = Compressor(method=compression, **kwargs)
        self._verbose = kwargs.get('verbose', True)

        # Parse specific files if provided
        if files:
            if isinstance(files, str):
                # Split space-separated string
                self.specific_files = [f.strip() for f in files.split() if f.strip()]
            else:
                self.specific_files = files
        else:
            self.specific_files = None

        # Validation
        if not self.specific_files and not self.input_path:
            raise ValueError('Either input_path or files must be provided')
        
        if self.input_path and not self.specific_files and not self.input_path.exists():
            raise FileNotFoundError(f'Input path not found: {input_path}')

    def _print(self, *kargs) -> None:
        """
        Print messages to the console if verbose mode is enabled.

        Args:
            *kargs: Arguments passed to the built-in `print` function.
        """
        if self._verbose:
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
        source_desc = ', '.join(self.specific_files[:3]) if self.specific_files else str(self.input_path)
        if self.specific_files and len(self.specific_files) > 3:
            source_desc += f' (and {len(self.specific_files) - 3} more)'
        
        self._print(f'Building {self.output_path} from {source_desc}...')

        files = self._collect_files()
        self._print(f'Found {len(files)} files')

        compressed_data = []
        current_offset = 0

        for file_info in files:
            file_path, virtual_path = file_info
            
            self._print(f'Compressing: {virtual_path}')

            original_data = GenericFile(file_path)
            original_data.read_type = 'rb'
            original_data = original_data.read_file()

            compressed = self._compressor.compress(original_data)

            self.index[virtual_path] = {
                'offset': current_offset,
                'size_original': len(original_data),
                'size_compressed': len(compressed),
                'hash': CalculatedHash(original_data).value,
                'compression': self.compression
            }

            compressed_data.append(compressed)
            current_offset += len(compressed)

        self._write_rpack(compressed_data)
        self._print(f'Created file: {self.output_path}')
        self._print(f'Total size: {self.output_path.stat().st_size} bytes')

    def _collect_files(self) -> List[tuple]:
        """
        Recursively collect all files from the input path or use specific files.

        Returns:
            list: A sorted list of tuples (Path, virtual_path) representing files to be packed
                  and their virtual paths in the archive.
        """
        if self.specific_files:
            # Use specific files provided
            files = []
            for file_str in self.specific_files:
                file_path = Path(file_str)
                
                # If path is relative, resolve against input_path or current directory
                if not file_path.is_absolute():
                    if self.input_path:
                        file_path = self.input_path / file_path
                    else:
                        file_path = Path.cwd() / file_path
                
                if not file_path.exists():
                    raise FileNotFoundError(f'Specified file not found: {file_str}')
                
                if not file_path.is_file():
                    raise ValueError(f'Path is not a file: {file_str}')
                
                # Try to make it relative to input_path if possible
                if self.input_path:
                    try:
                        virtual_path = file_path.relative_to(self.input_path)
                        virtual_path = VirtualFS.normalize_path(str(virtual_path))
                    except ValueError:
                        # File is outside input_path, use the original file_str
                        virtual_path = VirtualFS.normalize_path(file_str)
                else:
                    # No input_path, use the file_str as-is
                    virtual_path = VirtualFS.normalize_path(file_str)
                
                files.append((file_path, virtual_path))
            
            return sorted(files, key=lambda x: x[1])
        
        # Standard behavior: collect all files from input_path
        if not self.input_path:
            raise ValueError('input_path is required when files are not specified')
        
        if self.input_path.is_file():
            rel_path = VirtualFS.normalize_path(self.input_path.name)
            return [(self.input_path, rel_path)]

        files = []
        for item in self.input_path.rglob('*'):
            if item.is_file():
                rel_path = VirtualFS.normalize_path(str(item.relative_to(self.input_path)))
                files.append((item, rel_path))
        
        return sorted(files, key=lambda x: x[1])

    def _write_rpack(self, compressed_data: list) -> None:
        """
        Write the final RPack file, including header, index, and compressed data.

        Args:
            compressed_data (list): List of byte sequences representing compressed files.
        """
        with open(self.output_path, 'wb') as f:
            # Write file header
            f.write(MAGIC_HEADER)

            # Serialize and compress the file index
            index_json = json.dumps(self.index, indent=None)
            index_compressed = self._compressor.compress(index_json.encode('utf-8'))

            # Write index length and data
            f.write(struct.pack('<I', len(index_compressed)))
            f.write(index_compressed)

            # Write each compressed file sequentially
            for data in compressed_data:
                f.write(data)

__all__ = ['RPackBuilder']