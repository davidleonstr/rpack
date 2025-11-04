from typing import Literal
import zlib
import lzma

def nonemodify(data):
    """
    Return the same data without modification.

    This function is used as a placeholder when no compression or
    decompression should be applied.

    Args:
        data (bytes): The input data.

    Returns:
        bytes: The same data passed as input.
    """
    return data

modifiers = {
    'compression': {
        'zlib': zlib.compress,
        'lzma': lzma.compress,
        'none': nonemodify
    },
    'decompression': {
        'zlib': zlib.decompress,
        'lzma': lzma.decompress,
        'none': nonemodify
    }
}
"""
Dictionary that maps compression and decompression methods to their corresponding functions.
This mapping allows flexible method lookup by name.
"""

CompressionType = Literal[[*[k for k, _ in modifiers['compression'].items()]]]
"""
Type alias representing all valid compression method names.

Possible values are derived dynamically from the keys of `modifiers['compression']`.
"""
