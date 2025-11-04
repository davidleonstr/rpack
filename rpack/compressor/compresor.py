from .properties import (
    modifiers, 
    CompressionType
)

class Compressor:
    """
    A flexible compressor and decompressor class that uses predefined
    compression and decompression methods.

    Attributes:
        method (CompressionType): The compression method to use (e.g., 'zlib', 'bz2', etc.).
        kwargs (dict): Additional keyword arguments passed to the compression or decompression function.
    """

    def __init__(
            self, 
            method: CompressionType = 'zlib',  # type: ignore
            **kwargs
        ):
        """
        Initialize the Compressor with a specific compression method.

        Args:
            method (CompressionType, optional): The compression method. Defaults to 'zlib'.
            **kwargs: Optional arguments passed to the chosen compression or decompression function.
        """
        self.method = method
        self.kwargs = kwargs
    
    def compress(self, data: bytes) -> bytes:
        """
        Compresses a given byte sequence using the specified compression method.

        Args:
            data (bytes): The raw data to be compressed.

        Returns:
            bytes: The compressed data.

        Raises:
            ValueError: If the specified compression method is not recognized.
        """
        if self.method in modifiers['compression']:
            return modifiers['compression'][self.method](data, **self.kwargs)
        else:
            raise ValueError(f'Unknown compression method: {self.method}')
    
    def decompress(self, data: bytes) -> bytes:
        """
        Decompresses a given byte sequence using the specified decompression method.

        Args:
            data (bytes): The compressed data to be decompressed.

        Returns:
            bytes: The decompressed (original) data.

        Raises:
            ValueError: If the specified decompression method is not recognized.
        """
        if self.method in modifiers['decompression']:
            return modifiers['decompression'][self.method](data, **self.kwargs)
        else:
            raise ValueError(f'Unknown decompression method: {self.method}')