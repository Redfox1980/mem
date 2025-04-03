[app]

# (str) Title of your application
title = Gedaechtnispalast

# (str) Package name
package.name = gedaechtnispalast

# (str) Package domain (unique reverse domain-style string)
package.domain = org.deinname.gedaechtnispalast

# (str) Source code where your main.py is located
source.dir = .

# (list) Include these file extensions
source.include_exts = py,png,jpg,kv,json

# (list) Include patterns (z. B. Datenordner)
source.include_patterns = data/*.json, data/images/*.png

# (str) Application versioning
version = 0.1

# (list) Python dependencies
requirements = kivy

# (str) Orientation (portrait|landscape)
orientation = portrait

# (bool) Enable fullscreen (0 = no)
fullscreen = 0

# (int) Android API to use
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Architectures to build for (armeabi-v7a, arm64-v8a, x86, x86_64)
android.arch = armeabi-v7a

# (list) Permissions
android.permissions = INTERNET

# (bool) Copy library instead of using symlink
android.copy_libs = 1

# (str) Entry point, defaults to main.py
entrypoint = main.py

# (str) Supported screens (universal by default)
android.supported_screens = small, normal, large, xlarge

# (str) Icon (optional)
# icon.filename = data/icon.png
