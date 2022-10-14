"""Compiler for the OPL language. Written by Kevin Chen."""

# Imports
from . import ENCODING
from .functions import split_code, write, remove_leading_spaces

import struct


"""A compiler for OPL."""

class OPLCompiler:

	"""A compiler for OPL."""

	def __init__(self):

		"""A compiler for OPL."""

		pass

	"""Compiles OPL code to binary.
	   Args: code -> code to compile
	   Returns: compiled code"""

	def compile(self, code):

		"""Compiles OPL code to binary.
	   Args: code -> code to compile
	   Returns: compiled code"""

		compiled_code = bytearray()
		code_split = split_code(code)
		# Remove any leading spaces/tabs
		code_split = remove_leading_spaces(code_split)
		# Iterate over all lines
		line_num = 0
		for line_code in code_split:
			if line_code == []:
				# We got a newline, ignore
				continue
			elif len(line_code[0]) >= 2 and line_code[0][0 : 2] == '//':
				# Comment line, ignore
				continue
			try:
				# Add line number, command type, and number of args to code
				compiled_code += int.to_bytes(line_num, 4, byteorder='big') + int.to_bytes(int(line_code[0]), 4, byteorder='big') + int.to_bytes(len(line_code) - 1, 4, byteorder='big')
				# Add each argument
				for arg in line_code[1 : ]:
					# Get data type
					dtype = arg[0]
					arg = arg[1 : ]
					if dtype == 'i':
						# Int
						arg = int.to_bytes(int(arg), 4, byteorder='big')
					elif dtype == 'f':
						# Float
						arg = struct.pack('f', float(arg))
					elif dtype == 's':
						# String
						arg = bytes(arg, ENCODING)
					elif dtype == 'b':
						# Byte numbers (a,b,c,d,etc.)
						if arg.split(',') == ['']:
							# No bytes
							arg = bytes(0)
						else:
							arg = bytes([int(i) for i in arg.split(',')])
					elif dtype == 'g':
						# Signed int
						arg = int.to_bytes(int(arg), 4, byteorder='big', signed=True)
					elif dtype == 'h':
						# Hex int
						arg = int.to_bytes(int(arg, 16), 4, byteorder='big')
					compiled_code += int.to_bytes(len(arg), 4, byteorder='big') + arg
				line_num += 1
			except Exception as e:
				write('ERROR: ' + str(e) + ' LINE: ' + str(line_num) + ' CODE: ' + str(line_code) + '\n')
				break
		return compiled_code

