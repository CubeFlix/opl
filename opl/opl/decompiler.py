"""Decompiler for the OPL language. Written by Kevin Chen."""


# Imports
from . import PRINTABLE, ENCODING

import struct


"""A decompiler for OPL."""

class OPLDecompiler:

	"""A decompiler for OPL
   Args: assumetype -> the type to assume an arg is
         trystring -> if we should try to check if an arg is a string"""

	def __init__(self, assumetype='b', trystring=True):

		"""A decompiler for OPL
	   Args: assumetype -> the type to assume an arg is
	         trystring -> if we should try to check if an arg is a string"""

		self.assumetype = assumetype
		self.trystring = trystring

	"""Decompiles compiled OPL code.
	   Args: compiled -> a bytearray containing compiled OPL code"""

	def decompile(self, compiled):

		"""Decompiles compiled OPL code.
	   Args: compiled -> a bytearray containing compiled OPL code"""

		decompiled = ''

		# Iterate over each byte in the compiled bytecode
		i = 0
		while i < len(compiled):
			# Get line number (4 bytes)
			line_num = compiled[i : i + 4]
			i += 4
			# Get command number (4 bytes)
			cmd_name = int.from_bytes(compiled[i : i + 4], byteorder='big')
			i += 4
			# Get number of args (4 bytes)
			num_args = int.from_bytes(compiled[i : i + 4], byteorder='big')
			i += 4
			# Get all args
			arg_string = ''
			for arg in range(num_args):
				# Get length of this arg (4 bytes)
				len_arg = int.from_bytes(compiled[i : i + 4], byteorder='big')
				i += 4
				# Get the arg data (len_arg bytes)
				arg_data = compiled[i : i + len_arg]
				i += len_arg
				# Find data type
				# Check if it is a string
				if self.trystring and all([(char in PRINTABLE) for char in arg_data]):
					arg_data = '\'' + str(arg_data, ENCODING).replace('\\', '\\\\').replace('\'', '\\\'') + '\''
					arg_type = 's'
				# Use the standard assumed type
				else:
					# Binary type
					if self.assumetype == 'b':
						# Use bytes
						arg_data = ','.join([str(byte) for byte in bytes(arg_data)])
						arg_type = 'b'
					# Int type
					elif self.assumetype == 'i':
						arg_data = str(int.from_bytes(arg_data, byteorder='big'))
						arg_type = 'i'
					# Float type
					elif self.assumetype == 'f':
						arg_data = str(struct.unpack('f', arg_data))
						arg_type = 'f'
					# String type
					elif self.assumetype == 's':
						arg_data = '\'' + str(arg_data, ENCODING).replace('\\', '\\\\').replace('\'', '\\\'') + '\''
						arg_type = 's'
				# Add the arg to the line's args
				arg_string += arg_type + arg_data + ' '
			# Add the line to the decompiled code
			decompiled += (str(cmd_name) + ' ' + arg_string).rstrip() + '\n'
		# Return the decompiled code
		return decompiled

