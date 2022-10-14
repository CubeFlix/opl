"""OPE (Operation Executables) for the OPL language. Written by Kevin Chen."""

# OEP 013


# Imports
from .functions import *
from .executor import OPLExecutor


"""The compiler for OPE."""

class OPECompiler:

	"""A compiler for OPE."""

	def __init__(self):

		"""A compiler for OPE."""

		pass

	"""Compiles OPC bytecode to an OPE binary. 
	   Args: main -> the starting point code for our binary
	         files -> additional files (dictionary) to compile with the binary
	   Returns: compiled OPE binary code"""

	def compile(self, main, files):

		"""Compiles OPC bytecode to an OPE binary. 
	   Args: main -> the starting point code for our binary
	         files -> additional files (dictionary) to compile with the binary
	   Returns: compiled OPE binary code"""

		compiled = bytearray()
		# Add the main code
		compiled += int.to_bytes(len(main), 4, byteorder='big') + main
		# Add all the files
		compiled += TO_OEP_20(files)
		# Return the compiled code
		return compiled


"""The executor for OPE."""

class OPEExecutor:

	"""The executor for OPE.
	   Args: oplos -> the OPL OS to use"""

	def __init__(self, oplos=None):

		"""The executor for OPE.
		   Args: oplos -> the OPL OS to use"""

		self.oplos = oplos

	"""Executes a compiled OPE binary.
	   Args: binary -> the OPE binary to execute
	         runtime_args -> runtime args
	         sudo -> run as superuser"""

	def execute(self, binary, runtime_args=[], sudo=False):

		"""Executes a compiled OPE binary.
		   Args: binary -> the OPE binary to execute
		         runtime_args -> runtime args
		         sudo -> run as superuser"""

		# Get the main code
		main_code_len = int.from_bytes(binary[ : 4], byteorder='big')
		main_code = binary[4 : 4 + main_code_len]
		# Get extra files
		files = FROM_OEP_20(binary[4 + main_code_len : ])
		# Execute the main code
		e = OPLExecutor(opefiles=files, oplos=self.oplos)
		e.execute(main_code, runtime_args=runtime_args, sudo=sudo)
		# Return the output
		self.output = e.output
		return e.output

