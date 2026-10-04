# Offline Game Packages

These packages use `main.py`, the local game logic, AI, GUI, and the card images only. The network client and server are explicitly excluded.

## Download builds from GitHub

1. Open the repository's **Actions** tab.
2. Select **Build offline game**.
3. Choose **Run workflow**.
4. Download `LoveLetterOffline-Windows` and `LoveLetterOffline-Android` from the completed run.

GitHub stores workflow artifacts for 30 days. The Windows artifact contains `LoveLetterOffline.exe`; the Android artifact contains `LoveLetterOffline.apk`.

## Build the Windows EXE locally

Run this on Windows with Python 3.12:

```powershell
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean LoveLetterOffline.spec
```

The executable is created at `dist/LoveLetterOffline.exe`.

## Build the Android APK locally

Buildozer requires Linux. On Ubuntu, install the Android build prerequisites and then run:

```bash
python3 -m pip install buildozer "cython<3"
buildozer android debug
```

The APK is created under `bin/`. It requests no network permission and is a real Android package, unlike Pygbag's web archive format which also uses an `.apk` suffix.
