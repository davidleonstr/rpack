from typing import Dict, List, Set

class VirtualFS:
    """
    Represents a virtual file system (VFS) built from an RPack index.

    The VirtualFS class simulates a hierarchical directory structure based
    on file paths contained in a resource pack's index. It allows path-based
    operations such as existence checks, directory listings, and file type
    identification without accessing the actual file data.

    Attributes:
        index (Dict[str, dict]): A dictionary mapping virtual file paths to metadata.
        dirs (Set[str]): A set of all virtual directories derived from file paths.
    """

    def __init__(self, index: Dict[str, dict]):
        """
        Initialize the VirtualFS using the file index from an RPack archive.

        Args:
            index (Dict[str, dict]): The metadata index containing file paths and their info.
        """
        self.index = index
        self.dirs = self._buildDirectoryStructure()

    def _buildDirectoryStructure(self) -> Set[str]:
        """
        Construct a set of all virtual directories based on the file index.

        Iterates through file paths in the index and builds a collection of
        all possible parent directory paths.

        Returns:
            Set[str]: A set of all virtual directory paths.
        """
        dirs = set()

        for path in self.index.keys():
            parts = path.split('/')
            for i in range(1, len(parts)):
                dirPath = '/'.join(parts[:i])
                dirs.add(dirPath)

        return dirs

    def exists(self, path: str) -> bool:
        """
        Check if a given path exists as either a file or a directory.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        path = VirtualFS.normalizePath(path)
        return path in self.index or path in self.dirs

    def isFile(self, path: str) -> bool:
        """
        Check if the given path corresponds to a file.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if it is a file, False otherwise.
        """
        path = VirtualFS.normalizePath(path)
        return path in self.index

    def isDir(self, path: str) -> bool:
        """
        Check if the given path corresponds to a directory.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if it is a directory, False otherwise.
        """
        path = VirtualFS.normalizePath(path)
        return path in self.dirs or path == ''

    def listDir(self, path: str = '') -> List[str]:
        """
        List all items (files and subdirectories) within a given virtual directory.

        Args:
            path (str, optional): Directory path to list. Defaults to the root ('').

        Returns:
            List[str]: A sorted list of file and directory names in the given path.

        Raises:
            NotADirectoryError: If the provided path is not a valid directory.
        """
        path = VirtualFS.normalizePath(path)

        if path and not self.isDir(path):
            raise NotADirectoryError(f"'{path}' is not a directory")

        items = set()
        prefix = path + '/' if path else ''

        for filePath in self.index.keys():
            if filePath.startswith(prefix):
                remainder = filePath[len(prefix):]
                if '/' not in remainder:
                    items.add(remainder)
                else:
                    subDir = remainder.split('/')[0]
                    items.add(subDir)

        for dirPath in self.dirs:
            if dirPath.startswith(prefix) and dirPath != path:
                remainder = dirPath[len(prefix):]
                if '/' not in remainder:
                    items.add(remainder)
                else:
                    subDir = remainder.split('/')[0]
                    items.add(subDir)

        return sorted(list(items))

    @staticmethod
    def normalizePath(path: str) -> str:
        """
        Normalize a path to use forward slashes and remove leading/trailing separators.

        Args:
            path (str): The path to normalize.

        Returns:
            str: The normalized path in a consistent format.
        """
        path = path.replace('\\', '/')
        path = path.strip('/')
        return path

__all__ = ['VirtualFS']