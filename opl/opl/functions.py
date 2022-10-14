"""Functions for the OPL language. Written by Kevin Chen."""

# Imports
import sys, os
import struct
from . import ENCODING


"""Splits written code to commands and args."""

def split_code(code):

	"""Splits written code to commands and args."""

	code_split = []
	temp_cmd = []
	temp_string = ''
	in_string = False
	escape = False
	in_comment = False
	# Iterate over each char
	for i, c in enumerate(code):
		# If we get a string
		if c in ('"', '\''):
			if in_comment:
				temp_string += c
				continue
			if not escape:
				if in_string == c:
					in_string = False
				elif in_string == False:
					in_string = c
				else:
					temp_string += c
			else:
				escape = False
				temp_string += c
		# If we get a space
		elif c == ' ':
			if not in_string:
				temp_cmd.append(temp_string)
				temp_string = ''
			else:
				temp_string += c
		# If we get a newline
		elif c == '\n':
			if not in_string:
				temp_cmd.append(temp_string)
				temp_string = ''
				code_split.append(temp_cmd)
				temp_cmd = []
			else:
				temp_string += c
			if in_comment:
				in_comment = False
		# If we are to escape the next char
		elif c == '\\':
			if in_comment:
				temp_string += c
				continue
			if in_string and not escape:
				escape = True
			elif in_string and escape:
				escape = False
				temp_string += c
			else:
				temp_string += c
		# We got a comment
		elif c == '/' and code[i + 1] == '/' and not in_string:
			temp_string += '//'
			in_comment = True
		# If we get a normal char
		else:
			temp_string += c
	temp_cmd.append(temp_string)
	code_split.append(temp_cmd)
	# Return final split code
	return code_split


"""Get N chars from standard input. (WINDOWS ONLY)"""

def getcharswin(n):

	"""Get N chars from standard input. (WINDOWS ONLY)"""

	string = ""
	i = 0
	# Loop until we get N chars
	while True:
		c = msvcrt.getch()
		string += str(c, ENCODING)
		i += 1
		if i == n:
			break
	return string


"""Get N chars from standard input. (POSIX Systems ONLY)"""

def getcharsposix(n):

	"""Get N chars from standard input. (POSIX Systems ONLY)"""
	
	fd = sys.stdin.fileno()
	oldSettings = termios.tcgetattr(fd)
	string = ""
	i = 0
	# Loop until we get N chars
	while i <= n:
		# Do some magic
		try:
			tty.setcbreak(fd)
			answer = sys.stdin.read(1)
			string += str(answer, ENCODING)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)
			i += 1
	# Return string
	return string


# Get the correct system's getchar method
try:
	# Check Windows
	import msvcrt
	getchars = getcharswin
except:
	# Use POSIX
	import tty, sys, termios
	getchars = getcharsposix


"""Turns a list into bytes."""

def list_to_bytes(l):

	"""Turns a list into bytes."""

	b = bytearray()
	# Iterate through all items.
	for i in l:
		# Add length of the data.
		b += int.to_bytes(len(i), 4, byteorder='big').rjust(4, b'\x00')
		# Add the data
		b += i
	# Return final bytes
	return b

"""Turns bytes into a list of bytes."""

def bytes_to_list(b):

	"""Turns bytes into a list of bytes."""

	l = []
	# Iterate through bytes
	i = 0
	while i < len(b):
		# Get data length
		length = int.from_byteS(b[i : i + 4], byteorder='big')
		i += 4
		# Get data
		data = b[i : i + length]
		i += length
		l.append(data)
	# Return the list
	return l


"""Writes directly to standard output as a print handler."""

def write(data):

	"""Writes directly to standard output as a print handler.
	   Args: data -> data to write"""

	sys.stdout.write(data)
	sys.stdout.flush()



"""OEP 020 ENCODING FORMATS"""

def TO_OEP_20(files):

	"""Takes in files (dict) and encodes them using the OEP 20 encoding system."""

	buf = bytearray()
	# Iterate over each file
	for filename in files:
		# Add the length of the filename (4 bytes)
		buf += int.to_bytes(len(filename), 4, byteorder='big')
		# Add the filename
		buf += bytes(filename, ENCODING)
		# Add the length of the file data (4 bytes)
		buf += int.to_bytes(len(files[filename]), 4, byteorder='big')
		# Add the file data
		buf += files[filename]
	# Return the output buffer
	return buf

def FROM_OEP_20(buf):

	"""Takes in buffer and translates it into files (dict)"""

	files = {}
	# Iterate through the buffer
	i = 0
	while i < len(buf):
		# Get filename length (4 bytes)
		fname_len = int.from_bytes(buf[i : i + 4], byteorder='big')
		i += 4
		# Get filename
		fname = str(buf[i : i + fname_len], ENCODING)
		i += fname_len
		# Get file data length (4 bytes)
		fdata_len = int.from_bytes(buf[i : i + 4], byteorder='big')
		i += 4
		# Get the file data
		fdata = buf[i : i + fdata_len]
		i += fdata_len
		# Add to files
		files[fname] = fdata
	# Return the files
	return files

"""Removes leading spaces from split code."""

def remove_leading_spaces(code_split):

	"""Removes leading spaces from split code."""

	new_code = []
	# Iterate over each line
	for line in code_split:
		temp_line = []
		for part in line:
			# If this part is a '', don't add it
			if part == '':
				continue
			else:
				# Add it to the new code
				temp_line.append(part)
		new_code.append(temp_line)
	return new_code

