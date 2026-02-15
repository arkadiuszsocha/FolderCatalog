# Quick Start Guide

## For Users

### Run the App (Quick)
```bash
python main.py
```

### Build Mac App
```bash
./build.sh
open dist/FolderScanner.app
```

### Install
```bash
cp -r dist/FolderScanner.app /Applications/
```

## For Developers

### Project Structure
```
main.py      → Entry point, CLI arguments
database.py  → SQLite operations, data models
scanner.py   → Filesystem scanning
gui.py       → User interface components
```

### Key Classes

**DatabaseManager** (database.py)
- Manages all SQLite operations
- Uses context managers for safe connections
- Methods: add_folder(), remove_folder(), get_all_folders(), etc.

**FolderScanner** (scanner.py)
- Scans directories recursively
- Returns file/folder metadata
- Static methods for utilities

**FolderScannerGUI** (gui.py)
- Main application controller
- Connects UI events to business logic
- Manages all panels and widgets

### Adding Features

1. **New database operation**: Add method to `DatabaseManager`
2. **New scan feature**: Extend `FolderScanner`
3. **New UI component**: Add to `gui.py` following existing patterns

### Code Style

- Use type hints everywhere
- Add docstrings (Google style)
- Handle errors with try/except
- Use context managers for resources
- Keep functions focused and small

### Testing Locally

```bash
# Syntax check
python -m py_compile *.py

# Run directly
python main.py

# Type checking (optional)
pip install mypy
mypy main.py database.py scanner.py gui.py
```

## Common Tasks

### Change Database Location
```bash
python main.py --db-path /path/to/custom.db
```

### Reset Database
```bash
rm ~/.folder_scanner.db
```

### Build for Windows
```bash
pyinstaller --name="FolderScanner" --windowed --onefile main.py
```

### Build for Linux
```bash
pyinstaller --name="FolderScanner" --onefile main.py
```

## Best Practices Implemented

✅ **Separation of Concerns**: Database, business logic, and UI are separate
✅ **Type Safety**: Full type hints throughout
✅ **Resource Management**: Context managers for database connections
✅ **Error Handling**: Graceful error handling with user feedback
✅ **Documentation**: Comprehensive docstrings
✅ **Data Classes**: Clean, typed data models
✅ **Single Responsibility**: Each class has one clear purpose
✅ **DRY Principle**: No code duplication
✅ **Modular Design**: Easy to extend and test

## Architecture Diagram

```
┌─────────────┐
│   main.py   │  (Entry point)
└──────┬──────┘
       │
       ├──────────────┬──────────────┬
       │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│ database.py │ │scanner.py│ │   gui.py    │
│             │ │          │ │             │
│ - DB ops    │ │ - Scan   │ │ - UI        │
│ - Models    │ │ - Utils  │ │ - Events    │
└─────────────┘ └──────────┘ └─────────────┘
```

## What Makes This "Best Practice"?

1. **Type Hints**: Catches errors before runtime
2. **Dataclasses**: Clean, immutable data structures
3. **Context Managers**: No leaked connections
4. **Docstrings**: Self-documenting code
5. **Error Handling**: User-friendly error messages
6. **Modularity**: Easy to test individual components
7. **Single Responsibility**: Each file has one job
8. **No Globals**: All state properly encapsulated
9. **Resource Cleanup**: Proper file/connection handling
10. **Extensibility**: Easy to add new features
