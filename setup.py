"""
Setup configuration for Folder Catalog application (Python).
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="folder-catalog",
    version="1.0.0",
    description="A simple Python application for scanning and managing folder structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    python_requires=">=3.7",
    py_modules=["main", "database", "scanner", "gui"],
    install_requires=[
        # No external dependencies for runtime
    ],
    extras_require={
        "build": [
            "pyinstaller>=6.3.0",
        ],
        "dev": [
            "mypy>=1.0",
            "pytest>=7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "folder-catalog=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
)
