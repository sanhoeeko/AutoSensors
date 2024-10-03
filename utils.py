import ctypes
import os
import sys


def modifyPythonIcon():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")


def getRootDir():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.abspath(".")


assets_dir = os.path.join(getRootDir(), 'assets')
sys.path.append(os.path.join(os.path.dirname(__file__), assets_dir))


def existingFile(path: str) -> str:
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError


def getFile(file: str):
    return existingFile(os.path.join(assets_dir, file))


def existingUserFile(path: str, error_to_throw):
    if os.path.exists(path):
        return path
    else:
        raise error_to_throw
