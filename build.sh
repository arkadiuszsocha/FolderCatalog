#!/bin/bash

# Build script for Folder Scanner Mac app

echo "Building Folder Scanner for macOS..."
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Building application bundle..."

# Build the app with all modules
pyinstaller --name="FolderScanner" \
    --windowed \
    --onefile \
    --add-data "database.py:." \
    --add-data "scanner.py:." \
    --add-data "gui.py:." \
    --osx-bundle-identifier=com.folderscanner.app \
    main.py

echo ""
echo "✓ Build complete!"
echo ""
echo "Your app is located at: dist/FolderScanner.app"
echo ""
echo "To run:     open dist/FolderScanner.app"
echo "To install: cp -r dist/FolderScanner.app /Applications/"
echo ""
