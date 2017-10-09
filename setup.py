from cx_Freeze import setup, Executable

import os
import sys

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'
    
addtional_mods = ['numpy.core._methods', 'numpy.lib.format']


executables = [Executable("jeoltiftodmtif.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'includes': addtional_mods,
        'packages':packages,
    },

}

setup(
    name = "jeoltodm",
    options = options,
    version = "0.10.0",
    description = 'Just some words',
    executables = executables
)