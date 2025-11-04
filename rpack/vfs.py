from typing import Dict, List, Set

class VirtualFS:
    """
    Represents a virtual file system (VFS) built from an RPack index.

    The VirtualFS class simulates a hierarchical directory structure based
    on file paths contained in a resource pack's index. It allows path-based
    operations such as existence checks, directory listings, and file type
    identification without accessing the actual file data.

    Attributes:
        _index (Dict[str, dict]): A dictionary mapping virtual file paths to metadata.
        _dirs (Set[str]): A set of all virtual directories derived from file paths.
    """

    def __init__(self, index: Dict[str, dict]):
        """
        Initialize the VirtualFS using the file index from an RPack archive.

        Args:
            index (Dict[str, dict]): The metadata index containing file paths and their info.
        """
        self._index = index
        self._dirs = self._build_directory_structure()
    
    def _build_directory_structure(self) -> Set[str]:
        """
        Construct a set of all virtual directories based on the file index.

        Iterates through file paths in the index and builds a collection of
        all possible parent directory paths.

        Returns:
            Set[str]: A set of all virtual directory paths.
        """
        dirs = set()
        
        for path in self._index.keys():
            parts = path.split('/')
            for i in range(1, len(parts)):
                dir_path = '/'.join(parts[:i])
                dirs.add(dir_path)
        
        return dirs
    
    def exists(self, path: str) -> bool:
        """
        Check if a given path exists as either a file or a directory.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        path = VirtualFS.normalize_path(path)
        return path in self._index or path in self._dirs
    
    def isfile(self, path: str) -> bool:
        """
        Check if the given path corresponds to a file.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if it is a file, False otherwise.
        """
        path = VirtualFS.normalize_path(path)
        return path in self._index
    
    def isdir(self, path: str) -> bool:
        """
        Check if the given path corresponds to a directory.

        Args:
            path (str): The virtual path to check.

        Returns:
            bool: True if it is a directory, False otherwise.
        """
        path = VirtualFS.normalize_path(path)
        return path in self._dirs or path == ''
    
    def listdir(self, path: str = '') -> List[str]:
        """
        List all items (files and subdirectories) within a given virtual directory.

        Args:
            path (str, optional): Directory path to list. Defaults to the root ('').

        Returns:
            List[str]: A sorted list of file and directory names in the given path.

        Raises:
            NotADirectoryError: If the provided path is not a valid directory.
        """
        path = VirtualFS.normalize_path(path)
        
        if path and not self.isdir(path):
            raise NotADirectoryError(f"'{path}' is not a directory")
        
        items = set()
        prefix = path + '/' if path else ''
        
        # Collect files and subdirectories from the index
        for file_path in self._index.keys():
            if file_path.startswith(prefix):
                remainder = file_path[len(prefix):]
                if '/' not in remainder:
                    items.add(remainder)
                else:
                    subdir = remainder.split('/')[0]
                    items.add(subdir)
        
        # Collect directories that are children of the current path
        for dir_path in self._dirs:
            if dir_path.startswith(prefix) and dir_path != path:
                remainder = dir_path[len(prefix):]
                if '/' not in remainder:
                    items.add(remainder)
                else:
                    subdir = remainder.split('/')[0]
                    items.add(subdir)
        
        return sorted(list(items))
    
    @staticmethod
    def normalize_path(path: str) -> str:
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