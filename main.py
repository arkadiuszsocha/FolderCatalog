#!/usr/bin/env python3
"""
Folder Catalog - Main Application Entry Point

A simple Python application for scanning and managing folder structures with SQLite persistence.

Usage:
    python main.py [--db-path PATH]
"""

import tkinter as tk
import sys
import traceback
from pathlib import Path
from argparse import ArgumentParser

# Log crashes to file when running as frozen .app (no terminal)
def _log_crash(exc: BaseException) -> None:
    log_path = Path.home() / "FolderCatalog_crash.log"
    try:
        with open(log_path, "a") as f:
            f.write("\n---\n")
            f.write(traceback.format_exc())
    except Exception:
        pass


def parse_arguments():
    """Parse command line arguments."""
    parser = ArgumentParser(
        description="Folder Catalog - Scan and manage folder structures (Python)"
    )
    parser.add_argument(
        '--db-path',
        type=str,
        help='Path to SQLite database file (default: ~/.folder_scanner.db)',
        default=None
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    # Use module refs so frozen .app always has the class (PyInstaller namespace issue)
    import database
    import gui
    DatabaseManager = database.DatabaseManager
    FolderScannerGUI = gui.FolderScannerGUI

    # Parse arguments
    args = parse_arguments()
    
    # Determine database path
    db_path = None
    if args.db_path:
        db_path = Path(args.db_path)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager(db_path)
        
        # Create main window
        root = tk.Tk()
        
        # Initialize GUI
        app = FolderScannerGUI(root, db_manager)
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        _log_crash(e)
        print(f"Fatal error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # Try to show a message box so user sees the error when launched from Finder
        try:
            root = tk.Tk()
            root.withdraw()
            from tkinter import messagebox
            messagebox.showerror("Folder Catalog Error", f"{e}\n\nSee ~/FolderCatalog_crash.log for details.")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
