# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['client\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('common', 'common'), ('icon.png', '.')],
    hiddenimports=['shiboken2', 'PySide2.QtXml', 'PySide2.QtNetwork', 'PySide2.QtMultipart'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['sqlalchemy', 'aiosqlite', 'fastapi', 'uvicorn', 'starlette', 'pydantic_settings', 'tcl', 'tk', 'tkinter', 'unittest', 'test', 'pydoc', 'distutils', 'setuptools', 'numpy', 'pandas', 'matplotlib', 'jupyter', 'IPython', 'scipy', 'cv2', 'tensorflow', 'torch', 'PIL.ImageQt'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    exclude_binaries=True,
    name='game-saving-client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\python\\game_saving_cloud\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='game-saving-client',
)
