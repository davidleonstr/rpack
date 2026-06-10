import os

class GenericFile:
    """
    A generic file handler for reading, writing, and deleting files.

    This class provides a simple interface for common file operations with
    configurable read/write modes and encoding.

    Attributes:
        filePath (str): The path to the file to be managed.
        readType (str): The mode for reading files. Defaults to 'r'.
        encoding (str): The encoding used for file operations. Defaults to 'utf-8'.
        writeType (str): The mode for writing files. Defaults to 'w'.
    """

    def __init__(self, filePath) -> None:
        """
        Initializes the file handler with a specific filePath.

        Args:
            filePath (str): The path to the file to be managed.
        """
        self.filePath: str = filePath
        self.readType: str = 'r'
        self.encoding: str = 'utf-8'
        self.writeType: str = 'w'

    def readFile(self, lines: bool = False) -> str | list | None:
        """
        Reads the content of the file.

        Args:
            lines (bool, optional): If True, returns content as a list of lines.
                If False, returns content as a single string. Defaults to False.

        Returns:
            str | list | None: The file content as a string or list of lines,
                depending on the lines parameter.

        Raises:
            Exception: If the file is not found or an unexpected error occurs.
        """
        try:
            optionalArgs = {}
            if self.readType != 'rb' and self.writeType != 'wb':
                optionalArgs['encoding'] = self.encoding

            with open(file=self.filePath, mode=self.readType, **optionalArgs) as file:
                return file.read() if not lines else file.readlines()
        except FileNotFoundError:
            raise Exception(f"Error: File '{self.filePath}' does not exist.")
        except Exception as e:
            raise Exception(f'Unexpected error reading file: {e}')

    def writeFile(self, data: str) -> bool:
        """
        Writes data to the file.

        Args:
            data (str): The content to write to the file.

        Returns:
            bool: True if the write operation was successful.

        Raises:
            Exception: If there are permission issues or an unexpected error occurs.
        """
        try:
            with open(file=self.filePath, mode=self.writeType, encoding=self.encoding) as file:
                file.write(data)

            return True
        except PermissionError:
            raise Exception(f"Error: You do not have permissions to write to '{self.filePath}'.")
        except Exception as e:
            raise Exception(f'Unexpected error writing to file: {e}')

    def deleteFile(self) -> bool:
        """
        Deletes the file if it exists.

        Returns:
            bool: True if the file was successfully deleted, False if the file
                does not exist.
        """
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
            return True

        return False