"""The OPL Operating System in Python. Written by Kevin Chen."""

__version__ = '4.0'

# Encoding type
ENCODING = 'utf-8'


# Load all files
from .. import opl
from .filebuffer import *
from .operatingsystem import *
from .functions import *


# All exports
__all__ = ['FileBuffer', 'OPLOS', 'editor', '__version__', 'ENCODING']

