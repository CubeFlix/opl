"""Base class for a module in the OPL language. Written by Kevin Chen."""

# OEP 019


# Imports
from . import functions
from . import ENCODING, PRINTABLE
from .screenbuffer import ScreenBuffer
from .compiler import OPLCompiler
from .decompiler import OPLDecompiler


"""The base class for an OPL module."""

class BaseModule:

	"""The base class for an OPL module."""

	def __init__(self):

		"""The base class for an OPL module."""

		self.defined_opcodes = []

	"""Handles a command given a runtime.
	   Args: runtime -> the execution runtime
	         cmd_name -> the command name or OPCODE
	         line_args -> the arguments that are passed in"""

	@classmethod
	def handle_command(self, runtime, cmd_name, line_args):

		"""Handles a command given a runtime.
	   Args: runtime -> the execution runtime
	         cmd_name -> the command name or OPCODE
	         line_args -> the arguments that are passed in"""

		...

	"""Called after each OPCODE call
	   Args: runtime -> the execution runtime
	         cmd_name -> the command name or OPCODE
	         line_args -> the arguments that are passed in"""

	@classmethod
	def on_end_opcode(self, runtime, cmd_name, line_args):

		"""Called after each OPCODE call
	   Args: runtime -> the execution runtime
	         cmd_name -> the command name or OPCODE
	         line_args -> the arguments that are passed in"""

		...

	"""Called before each OPCODE call
	   Args: runtime -> the execution runtime
	         cmd_name -> the command name or OPCODE
	         line_args -> the arguments that are passed in"""

	@classmethod
	def on_begin_opcode(self, runtime, cmd_name, line_args):

		"""Called before each OPCODE call
	   Args: runtime -> the execution runtime
	         cmd_name -> the command name or OPCODE
	         line_args -> the arguments that are passed in"""

		...

	"""Initializes the functions for the module, so it can use write, etc."""

	def init_functions(self):

		"""Initializes the functions for the module, so it can use write, etc."""

		# Have to use these stupid imports because this whole thing uses circular imports. (Evil and bad)
		from .executor import OPLExecutor
		from .ope import OPECompiler, OPEExecutor

		self.__dict__ = {**self.__dict__, **functions.__dict__, 'ENCODING' : ENCODING, 'PRINTABLE' : PRINTABLE, 'ScreenBuffer' : ScreenBuffer, 'OPLExecutor' : OPLExecutor, 'OPLCompiler' : OPLCompiler, \
			'OPLDecompiler' : OPLDecompiler, 'OPECompiler' : OPECompiler, 'OPEExecutor' : OPEExecutor}

