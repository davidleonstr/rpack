import json
import struct
from pathlib import Path
from typing import Dict
from .compressor import Compressor, CompressionType
from .vfs import VirtualFS
from .core import MAGIC_HEADER
from .utils import GenericFile, CalculatedHash

class RPackBuilder:
    """
    Builds a binary resource package (RPack) from files in a directory.

    The RPack format stores files in a compressed binary structure, including
    metadata such as compression type, file sizes, and SHA-256 hashes. This
    class handles file discovery, compression, and package writing.

    Attributes:
        input_path (Path): The source directory or file to pack.
        output_path (Path): The destination file path for the generated package.
        compression (CompressionType): The compression method used for all files.
        index (Dict[str, dict]): Metadata index for the packed files.
        _compressor (Compressor): Internal compressor instance for file data.
        _verbose (bool): Whether to print progress messages during the build.
    """

    def __init__(
            self,
            input_path: str,
            output_path: str,
            compression: CompressionType = 'zlib',  # type: ignore
            **kwargs,
        ):
        """
        Initialize the RPackBuilder with input and output paths and compression settings.

        Args:
            input_path (str): Path to the source directory or file.
            output_path (str): Path to the output RPack file.
            compression (CompressionType, optional): Compression method. Defaults to 'zlib'.
            **kwargs: Additional arguments for the compressor or verbosity.
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.compression = compression
        self.index: Dict[str, dict] = {}
        self._compressor = Compressor(method=compression, **kwargs)

        self._verbose = kwargs.get('verbose', True)

        if not self.input_path.exists():
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
            1. Collect files recursively from the input path.
            2. Compress each file and store its metadata.
            3. Write the RPack file with header, index, and compressed contents.

        Raises:
            FileNotFoundError: If the input path does not exist.
        """
        self._print(f'Building {self.output_path} from {self.input_path}...')

        files = self._collect_files()
        self._print(f'Found {len(files)} files')

        compressed_data = []
        current_offset = 0

        for file_path in files:
            file_path: Path  # type

            rel_path = VirtualFS.normalize_path(str(file_path.relative_to(self.input_path)))
            self._print(f'Compressing: {rel_path}')

            original_data = GenericFile(file_path)
            original_data.read_type = 'rb'
            original_data = original_data.read_file()

            compressed = self._compressor.compress(original_data)

            self.index[rel_path] = {
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

    def _collect_files(self) -> list:
        """
        Recursively collect all files from the input path.

        Returns:
            list: A sorted list of `Path` objects representing files to be packed.
        """
        if self.input_path.is_file():
            return [self.input_path]

        files = []
        for item in self.input_path.rglob('*'):
            if item.is_file():
                files.append(item)
        return sorted(files)

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
