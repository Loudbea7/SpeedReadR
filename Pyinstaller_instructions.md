make sure 3d acceleration is on

install poetry, pyenv, python

```
poetry init
```

( set your python version to 3.10.10 EXACTLY, not ^3.10.10, skip the other steps)
```
pyenv shell 3.10.10

pyenv which python
```
output example:

"C:\Users\wind\.pyenv\pyenv-win\versions\3.10.10\python.exe"

`poetry env use <location from pyenv which python>`

```
poetry env use C:\Users\wind\.pyenv\pyenv-win\versions\3.10.10\python.exe
```

```
pip install poetry-add-requirements.txt

poeareq
```

```
poetry add kivy

poetry add pyinstaller
```

change .toml python = 3.10.10

```
poetry add auto-py-to-exe

poetry add kivy.deps.gstreamer

poetry install

poetry shell
```

(POETRY SHELL CONSOLE)

`python -m PyInstaller --onefile --name KIVYWINDOWAPP "full:\path\to\main.py"`

```
python -m PyInstaller --onefile --name SpeedReadR "C:\Users\wind\Desktop\reader\speed_read_r.py"
```

add to the beginning of the spec file:

`from kivy_deps import sdl2, glew`

add this in the right spot in the spec file:
```
exe = EXE(
    pyz, Tree('C:\\Users\\wind\\Desktop\\reader\\'),

*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],

console=False,
```

When the spec file is done do:
```
python -m PyInstaller main.spec
```



---
# Windows:

# .spec file example
```
# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from kivy_deps import sdl2, glew
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, \
    get_deps_all, hookspath, runtime_hooks
from kivymd import hooks_path as kivymd_hooks_path

path = os.path.abspath(".")

block_cipher = None

a = Analysis(
    ['C:\\Users\\wind\\Desktop\\speed_read_r\\speed_read_r.py'],
    pathex=[path],
    binaries=[],
    datas=[('C:\\Users\\wind\\Desktop\\speed_read_r\\speed_read_r.kv', '.'), ("C:\\Users\\wind\\Desktop\\speed_read_r\\assets\\*", "assets")],
    hiddenimports=[],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
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
	*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Speed_Read_R',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

```
--- 

# .toml file example

```
[tool.poetry]
name = "speed-read-r"
version = "1.1.0"
description = ""
authors = ["Loudbeat <loudbeatproductions@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "3.10.10"
beautifulsoup4 = "4.12.0"
ebooklib = "0.18"
kivy = "2.1.0"
kivymd = "1.1.1"
markdown = "3.4.1"
pypdf = "3.6.0"
sqlmodel = "0.0.8"
striprtf = "0.0.22"
wakepy = "0.6.0"
pyinstaller = "^5.8.0"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

```



`poetry add docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew`

---
# Linux:

# .spec file example
```
```
# .toml file example
```
```