# PyInstaller spec for Pac-Man. Build with: pyinstaller pac-man.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pac-man.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('pacman/assets', 'pacman/assets'),
    ],
    hiddenimports=['mazegenerator', 'mazegenerator.mazegenerator'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pac-man',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
