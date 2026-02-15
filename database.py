"""
Database module for Folder Catalog application.
Handles all SQLite operations with proper connection management.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class ScannedFolder:
    """Data class representing a scanned folder."""
    id: Optional[int]
    label: str
    path: str
    last_scan: Optional[datetime] = None
    file_count: int = 0
    folder_count: int = 0


@dataclass
class FolderItem:
    """Data class representing a file or folder item."""
    path: str
    name: str
    is_directory: bool
    size: int


class DatabaseManager:
    """Manages all database operations for the Folder Catalog application."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. Defaults to ~/.folder_scanner.db
        """
        if db_path is None:
            db_path = Path.home() / ".folder_scanner.db"
        self.db_path = db_path
        self._initialize_database()
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection cleanup.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for scanned folders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scanned_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    last_scan TIMESTAMP,
                    file_count INTEGER DEFAULT 0,
                    folder_count INTEGER DEFAULT 0
                )
            """)
            
            # Table for folder contents
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folder_contents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder_id INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    name TEXT NOT NULL,
                    is_directory INTEGER NOT NULL,
                    size INTEGER DEFAULT 0,
                    FOREIGN KEY (folder_id) REFERENCES scanned_folders(id) 
                        ON DELETE CASCADE
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_folder_contents_folder_id 
                ON folder_contents(folder_id)
            """)
    
    def add_folder(self, label: str, path: str) -> int:
        """
        Add a new folder to the database.
        
        Args:
            label: Display label for the folder
            path: Filesystem path to the folder
            
        Returns:
            ID of the newly created folder
            
        Raises:
            sqlite3.IntegrityError: If folder path already exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO scanned_folders (label, path) VALUES (?, ?)",
                (label, path)
            )
            return cursor.lastrowid
    
    def remove_folder(self, folder_id: int) -> None:
        """
        Remove a folder and all its contents from the database.
        
        Args:
            folder_id: ID of the folder to remove
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scanned_folders WHERE id = ?", (folder_id,))
            cursor.execute("DELETE FROM folder_contents WHERE folder_id = ?", (folder_id,))
    
    def get_all_folders(self) -> List[ScannedFolder]:
        """
        Get all scanned folders from the database.
        
        Returns:
            List of ScannedFolder objects
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, label, path, last_scan, file_count, folder_count 
                FROM scanned_folders
                ORDER BY label
            """)
            rows = cursor.fetchall()
            
            folders = []
            for row in rows:
                last_scan = None
                if row['last_scan']:
                    try:
                        last_scan = datetime.fromisoformat(row['last_scan'])
                    except (ValueError, TypeError):
                        pass
                
                folders.append(ScannedFolder(
                    id=row['id'],
                    label=row['label'],
                    path=row['path'],
                    last_scan=last_scan,
                    file_count=row['file_count'],
                    folder_count=row['folder_count']
                ))
            
            return folders
    
    def update_folder_scan(
        self, 
        folder_id: int, 
        items: List[FolderItem],
        file_count: int,
        folder_count: int
    ) -> None:
        """
        Update folder contents and scan metadata.
        
        Args:
            folder_id: ID of the folder being updated
            items: List of FolderItem objects to store
            file_count: Total number of files scanned
            folder_count: Total number of folders scanned
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear old data
            cursor.execute("DELETE FROM folder_contents WHERE folder_id = ?", (folder_id,))
            
            # Insert new data
            for item in items:
                cursor.execute("""
                    INSERT INTO folder_contents 
                    (folder_id, path, name, is_directory, size) 
                    VALUES (?, ?, ?, ?, ?)
                """, (folder_id, item.path, item.name, int(item.is_directory), item.size))
            
            # Update scan metadata
            cursor.execute("""
                UPDATE scanned_folders 
                SET last_scan = ?, file_count = ?, folder_count = ? 
                WHERE id = ?
            """, (datetime.now().isoformat(), file_count, folder_count, folder_id))
    
    def get_folder_contents(self, folder_id: int) -> List[FolderItem]:
        """
        Get all contents of a folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of FolderItem objects sorted by path
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT path, name, is_directory, size 
                FROM folder_contents 
                WHERE folder_id = ? 
                ORDER BY path
            """, (folder_id,))
            rows = cursor.fetchall()
            
            return [
                FolderItem(
                    path=row['path'],
                    name=row['name'],
                    is_directory=bool(row['is_directory']),
                    size=row['size']
                )
                for row in rows
            ]
    
    def get_folder_by_id(self, folder_id: int) -> Optional[ScannedFolder]:
        """
        Get a single folder by ID.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            ScannedFolder object or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, label, path, last_scan, file_count, folder_count 
                FROM scanned_folders 
                WHERE id = ?
            """, (folder_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            last_scan = None
            if row['last_scan']:
                try:
                    last_scan = datetime.fromisoformat(row['last_scan'])
                except (ValueError, TypeError):
                    pass
            
            return ScannedFolder(
                id=row['id'],
                label=row['label'],
                path=row['path'],
                last_scan=last_scan,
                file_count=row['file_count'],
                folder_count=row['folder_count']
            )
