"""Functions for the OPL OS. Written by Kevin Chen."""


# Imports
import sys
import opl.opl as opl
from . import ENCODING


"""Opens a text editor, and returns the output."""

def editor():

	"""Opens a text editor, and returns the output."""

	# Current line number
	l = 0
	# Current text
	text = ''
	# Keep taking input
	while True:
		# Take input
		d = input(str(l) + ': ')
		# Parse input
		if len(d) > 0 and d[0] == '\x07':
			# End
			break
		text += d
		l += 1
		# Add a newline char
		text += '\n'
	# Return the code/text
	return text


"""Writes directly to standard output."""

def write(data):

	"""Writes directly to standard output.
	   Args: data -> data to write"""

	sys.stdout.write(data)
	sys.stdout.flush()


"""Retrieves a password from input. (OEP 004)"""

def get_password():

	"""Retrieves a password from input. (OEP 004)"""

	password = ''
	# Print prompt
	sys.stdout.write('Password: ')
	sys.stdout.flush()
	# Get password
	while True:
		# Get a char
		char = opl.getchars(1)
		# If char is newline
		if char == '\r':
			# End
			sys.stdout.write('\n')
			sys.stdout.flush()
			break
		# If char is backspace
		elif char == '\b':
			# Backspace
			password = password[ : -1]
		# Else
		else:
			# Add the char
			password += char
			sys.stdout.write('*')
			sys.stdout.flush()
	# Return the password
	return password

