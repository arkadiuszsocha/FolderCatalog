# Folder Scanner

A professional, lightweight Mac application for scanning and managing folder structures with SQLite persistence. Built with Python following best practices.

## Features

- **Two-panel interface**: Scanned folders list (left) + hierarchical folder tree (right)
- **SQLite persistence**: All data saved automatically between sessions
- **Easy management**: Add, remove, and scan folders with one click
- **Custom labels**: Name folders however you want for easy identification
- **Detailed view**: Complete folder structure with file types and human-readable sizes
- **Cross-platform**: Works on macOS, Windows, and Linux

## Architecture

The application follows clean architecture principles with proper separation of concerns:

```
main.py         - Application entry point
database.py     - Database operations (SQLite with context managers)
scanner.py      - Filesystem scanning logic
gui.py          - User interface components (MVC pattern)
```

### Key Design Patterns

- **MVC Pattern**: Clear separation between data, logic, and presentation
- **Context Managers**: Safe database connection handling
- **Type Hints**: Full type annotations for better code safety
- **Dataclasses**: Clean data models for ScannedFolder and FolderItem
- **Error Handling**: Proper exception handling throughout
- **Single Responsibility**: Each module has one clear purpose

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Option 1: Build Mac App Bundle (Recommended)

```bash
# 1. Navigate to project directory
cd folder_scanner

# 2. Build the app
./build.sh

# 3. Install to Applications
cp -r dist/FolderScanner.app /Applications/

# 4. Run
open /Applications/FolderScanner.app
```

### Option 2: Run Directly with Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Custom Database Path

```bash
# Specify custom database location
python main.py --db-path ~/Documents/my_scanner.db
```

## Usage

### Adding a Folder

1. Click the **"Add Folder"** button
2. Select a directory from the file browser
3. Enter a descriptive label (defaults to folder name)
4. Click **OK**

### Scanning a Folder

1. Select a folder from the left panel
2. Click **"Scan/Update"** button
3. Wait for scan completion
4. View results in the right panel

### Viewing Contents

1. Select any scanned folder from the left list
2. Browse the hierarchical tree in the right panel
3. Expand/collapse folders to explore structure
4. View file types and sizes in the columns

### Removing a Folder

1. Select the folder to remove
2. Click **"Remove"** button
3. Confirm deletion

## Development

### Project Structure

```
folder_scanner/
├── main.py              # Entry point, argument parsing
├── database.py          # DatabaseManager class, data models
├── scanner.py           # FolderScanner class, filesystem operations
├── gui.py              # All GUI components and controllers
├── requirements.txt     # Python dependencies
├── build.sh            # Build script for Mac
└── README.md           # Documentation
```

### Code Quality Features

- **Type Hints**: Complete type annotations throughout
- **Docstrings**: Google-style docstrings for all classes and methods
- **Context Managers**: Safe resource management
- **Dataclasses**: Clean, immutable data structures
- **Error Handling**: Graceful handling of filesystem and database errors
- **Separation of Concerns**: Clear module boundaries

### Running Tests (Future)

```bash
# Unit tests (to be implemented)
python -m pytest tests/

# Type checking
mypy main.py database.py scanner.py gui.py
```

## Data Storage

- **Location**: `~/.folder_scanner.db` (SQLite database)
- **Contents**: Folder labels, paths, scan metadata, and file/folder trees
- **Persistence**: Automatically saved, survives application restarts
- **Reset**: Delete `~/.folder_scanner.db` to start fresh

## Building for Other Platforms

### Windows

```bash
pip install pyinstaller
pyinstaller --name="FolderScanner" --windowed --onefile main.py
```

### Linux

```bash
pip install pyinstaller
pyinstaller --name="FolderScanner" --onefile main.py
```

## Performance

- Efficient scanning with `os.walk()`
- Database indexing for fast queries
- Lazy loading of tree contents
- Minimal memory footprint

## Troubleshooting

### Mac Security Warning

If macOS blocks the app:
1. Right-click the app → **Open**
2. Or: **System Preferences** → **Security & Privacy** → **Allow**

### Permission Errors

Grant the app permission to access folders when prompted by macOS.

### Database Issues

If you encounter database corruption:
```bash
rm ~/.folder_scanner.db
# Restart the application
```

### Python Not Found

Install Python from [python.org](https://www.python.org/downloads/) or use Homebrew:
```bash
brew install python
```

## Requirements

### Runtime
- Python 3.7+
- tkinter (included with Python)
- sqlite3 (included with Python)

### Build
- PyInstaller 6.3.0+

## License

Free to use and modify.

## Contributing

Contributions welcome! Please follow these guidelines:

1. Maintain type hints
2. Add docstrings to new functions
3. Follow existing code style
4. Keep modules focused and single-purpose
5. Handle errors gracefully

## Future Enhancements

- [ ] Export folder structure to JSON/CSV
- [ ] Search functionality
- [ ] Folder comparison
- [ ] File filtering by type/size
- [ ] Duplicate file detection
- [ ] Unit tests
- [ ] Dark mode support
- [ ] Folder statistics dashboard

## Technical Details

### Database Schema

**scanned_folders**
- id (INTEGER PRIMARY KEY)
- label (TEXT)
- path (TEXT UNIQUE)
- last_scan (TIMESTAMP)
- file_count (INTEGER)
- folder_count (INTEGER)

**folder_contents**
- id (INTEGER PRIMARY KEY)
- folder_id (INTEGER FOREIGN KEY)
- path (TEXT)
- name (TEXT)
- is_directory (INTEGER)
- size (INTEGER)

### Dependencies

- **PyInstaller**: For building standalone executables
- **Standard Library**: tkinter, sqlite3, pathlib, dataclasses, typing, contextlib

No external runtime dependencies required!
