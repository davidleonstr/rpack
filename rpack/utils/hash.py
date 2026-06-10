import hashlib

class CalculatedHash:
    """
    Represents a SHA-256 hash calculated from a given byte sequence.

    This class provides a simple way to generate and store a hexadecimal
    hash value for any binary data.
    """

    def __init__(self, data: bytes):
        """
        Initialize the CalculatedHash instance and compute the SHA-256 hash.

        Args:
            data (bytes): The input data to be hashed.
        """
        self.value = hashlib.sha256(data).hexdigest()