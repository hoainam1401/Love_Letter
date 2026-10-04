# -*- mode: python ; coding: utf-8 -*-

offline_images = [
    "Back.png",
    "Baron.png",
    "Countess.png",
    "crown.png",
    "Guard.png",
    "Handmaid.png",
    "King.png",
    "Priest.png",
    "Prince.png",
    "Princess.png",
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[(f"images/{name}", "images") for name in offline_images],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["client", "server", "test_game"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LoveLetterOffline",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
