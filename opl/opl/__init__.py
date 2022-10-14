"""OPL (Operation Language) in Python. Written by Kevin Chen."""

__version__ = '4.3'


# Imports
import string


# Encoding type
ENCODING = 'utf-8'

# Printable bytes
PRINTABLE = bytes(string.printable, ENCODING)

# Load all files
from .executor import *
from .compiler import *
from .screenbuffer import *
from .decompiler import *
from .functions import *
from .module import *
from .ope import *

# All exports
__all__ = ['OPLExecutor', 'OPLCompiler', 'ScreenBuffer', 'OPLDecompiler', 'BaseModule', 'OPECompiler', 'OPEExecutor', 'ENCODING', 'PRINTABLE', 'write', 'getchars', 'list_to_bytes', 'bytes_to_list', 'split_code', '__version__']

