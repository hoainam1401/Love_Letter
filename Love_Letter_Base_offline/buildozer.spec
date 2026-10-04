[app]
title = Love Letter Offline
package.name = loveletteroffline
package.domain = com.hoainam
source.dir = .
source.include_exts = py,png
source.exclude_dirs = build,bin,__pycache__,.venv,.git
source.exclude_patterns = client.py,server.py,test_game.py,.DS_Store,images/Assassin.png,images/Baroness.png,images/Bishop.png,images/Cardinal.png,images/Constable.png,images/Count.png,images/Dowager Queen.png,images/Gemini_Generated_Image_euqqpxeuqqpxeuqq.png,images/Jester.png,images/Sycophant.png
version = 1.0.0
requirements = python3,pygame
orientation = landscape
fullscreen = 0
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
