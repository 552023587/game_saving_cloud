"""PyInstaller build script — server + client"""
import os
import PyInstaller.__main__

UNUSED = [
    "--exclude-module=tcl", "--exclude-module=tk", "--exclude-module=tkinter",
    "--exclude-module=unittest", "--exclude-module=test", "--exclude-module=pydoc",
    "--exclude-module=distutils", "--exclude-module=setuptools",
    "--exclude-module=numpy", "--exclude-module=pandas",
    "--exclude-module=matplotlib", "--exclude-module=jupyter",
    "--exclude-module=IPython", "--exclude-module=scipy",
    "--exclude-module=cv2", "--exclude-module=tensorflow",
    "--exclude-module=torch", "--exclude-module=PIL.ImageQt",
]

SHARED = [
    "--onedir",
    "--clean",
    "-y",
    "--noupx",
    "--optimize=2",
    "--noconfirm",
    "--log-level=WARN",
    *UNUSED,
]

def build_server():
    PyInstaller.__main__.run([
        "server/main.py",
        "--name=game-saving-server",
        "--add-data=common:common",
        "--hidden-import=aiosqlite",
        "--exclude-module=PySide2",
        "--exclude-module=PySide6",
        "--exclude-module=PyQt5",
        "--exclude-module=PyQt6",
        "--exclude-module=shiboken2",
        *SHARED,
    ])

def build_client():
    PyInstaller.__main__.run([
        "client/main.py",
        "--name=game-saving-client",
        "--add-data=common:common",
        "--add-data=icon.png:.",
        f"--icon={os.path.abspath('icon.ico')}",
        "--windowed",
        "--hidden-import=shiboken2",
        "--hidden-import=PySide2.QtXml",
        "--hidden-import=PySide2.QtNetwork",
        "--hidden-import=PySide2.QtMultipart",
        "--exclude-module=sqlalchemy",
        "--exclude-module=aiosqlite",
        "--exclude-module=fastapi",
        "--exclude-module=uvicorn",
        "--exclude-module=starlette",
        "--exclude-module=pydantic_settings",
        *SHARED,
    ])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        build_client()
    else:
        build_server()
