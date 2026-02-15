# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Folder Catalog Mac .app bundle

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['database', 'scanner', 'gui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Folder Catalog',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Set True to see startup errors when app doesn't open; set False for release
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Folder Catalog',
)

app = BUNDLE(
    coll,
    name='Folder Catalog.app',
    icon=None,  # Add icon path here if you have a .icns file
    bundle_identifier='com.foldercatalog.app',
    info_plist={
        'CFBundleName': 'Folder Catalog',
        'CFBundleDisplayName': 'Folder Catalog',
        'CFBundleExecutable': 'Folder Catalog',
        'CFBundleIdentifier': 'com.foldercatalog.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': 'Folder Catalog',
    },
)
