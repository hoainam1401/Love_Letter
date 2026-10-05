# -*- mode: python ; coding: utf-8 -*-

online_images = [
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

shared_gui = "../Love_Letter_Base_offline/gui.py"
datas = [(shared_gui, "shared_gui")]
datas.extend((f"images/{name}", "shared_gui/images") for name in online_images)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["server"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LoveLetterOnline",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
