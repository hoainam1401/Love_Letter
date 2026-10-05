# Offline Windows Package

The Windows executable uses `main.py`, the local game logic, AI, GUI, and the card images only. The network client and server are explicitly excluded.

## Download builds from GitHub

1. Open the repository's **Actions** tab.
2. Select **Build offline game**.
3. Choose **Run workflow**.
4. Download `LoveLetterOffline-Windows` from the completed run.

GitHub stores workflow artifacts for 30 days. The artifact contains `LoveLetterOffline.exe`.

## Build the Windows EXE locally

Run this on Windows with Python 3.12:

```powershell
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean LoveLetterOffline.spec
```

The executable is created at `dist/LoveLetterOffline.exe`.
