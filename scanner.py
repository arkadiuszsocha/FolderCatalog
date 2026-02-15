"""
File system scanner module.
Handles scanning directories and collecting file/folder information.
"""

import os
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from database import FolderItem


class FolderScanner:
    """Scans filesystem directories and collects information about contents."""
    
    @staticmethod
    def scan_directory(
        root_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[List[FolderItem], int, int]:
        """
        Scan a directory and return all files and folders.
        
        Args:
            root_path: Root directory to scan
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (items_list, file_count, folder_count)
            
        Raises:
            FileNotFoundError: If root_path doesn't exist
            PermissionError: If directory is not accessible
        """
        root = Path(root_path)
        
        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root_path}")
        
        if not root.is_dir():
            raise NotADirectoryError(f"Not a directory: {root_path}")
        
        items: List[FolderItem] = []
        file_count = 0
        folder_count = 0
        
        try:
            for current_dir, directories, files in os.walk(root_path):
                current_path = Path(current_dir)
                
                # Update progress if callback provided
                if progress_callback:
                    progress_callback(str(current_path))
                
                # Process directories
                folder_count += len(directories)
                for dir_name in directories:
                    dir_path = current_path / dir_name
                    rel_path = dir_path.relative_to(root)
                    
                    items.append(FolderItem(
                        path=str(rel_path),
                        name=dir_name,
                        is_directory=True,
                        size=0
                    ))
                
                # Process files
                file_count += len(files)
                for file_name in files:
                    file_path = current_path / file_name
                    rel_path = file_path.relative_to(root)
                    
                    # Get file size safely
                    size = FolderScanner._get_file_size(file_path)
                    
                    items.append(FolderItem(
                        path=str(rel_path),
                        name=file_name,
                        is_directory=False,
                        size=size
                    ))
        
        except PermissionError as e:
            raise PermissionError(f"Permission denied accessing: {e.filename}")
        
        return items, file_count, folder_count
    
    @staticmethod
    def _get_file_size(file_path: Path) -> int:
        """
        Get file size safely, handling errors.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes, or 0 if unable to determine
        """
        try:
            return file_path.stat().st_size
        except (OSError, PermissionError):
            return 0
    
    @staticmethod
    def format_size(size: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size_float = float(size)
        
        for unit in units:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        
        return f"{size_float:.1f} {units[-1]}"
    
    @staticmethod
    def validate_path(path: str) -> bool:
        """
        Validate if a path exists and is accessible.
        
        Args:
            path: Path to validate
            
        Returns:
            True if valid and accessible, False otherwise
        """
        try:
            p = Path(path)
            return p.exists() and p.is_dir() and os.access(path, os.R_OK)
        except (OSError, PermissionError):
            return False
