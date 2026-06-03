# hook-black.py
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

hiddenimports = collect_submodules('black')
datas = copy_metadata('black')