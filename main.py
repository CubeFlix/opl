"""OPL (Operation Language) in Python. Written by Kevin Chen."""

__version__ = '2.5'

# Imports
import sys, os
import time
import struct
import hashlib
import numpy as np
import threading
import importlib
import string
import socket


# Encoding type
ENCODING = 'utf-8'

# All exports
__all__ = ['write', 'OPLExecutor', 'OPLCompiler', 'OPLDecompiler', 'ScreenBuffer', 'getchars', 'list_to_bytes', 'bytes_to_list', 'ENCODING']

# Printable bytes
PRINTABLE = bytes(string.printable, ENCODING)


"""Splits written code to commands and args."""

def split_code(code):

	"""Splits written code to commands and args."""

	code_split = []
	temp_cmd = []
	temp_string = ''
	in_string = False
	escape = False
	# Iterate over each char
	for c in code:
		# If we get a string
		if c in ('"', '\''):
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
		# If we are to escape the next char
		elif c == '\\':
			if in_string and not escape:
				escape = True
			elif in_string and escape:
				escape = False
				temp_string += c
			else:
				temp_string += c
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


"""Screen buffer for OPL OS.
   Args: size -> tuple containing size of the screen buffer
   	     runtime -> the runtime this buffer is ran in"""

class ScreenBuffer:

	"""Screen buffer for OPL OS.
   Args: size -> tuple containing size of the screen buffer
   	     runtime -> the runtime this buffer is ran in"""

	def __init__(self, size, runtime):

		"""Screen buffer for OPL OS.
	   Args: size -> tuple containing size of the screen buffer
	   	     runtime -> the runtime this buffer is ran in"""

		self.size = (int(size[0]), int(size[1]))
		self.runtime = runtime
		self.allow_close = False
		# Get our pygame
		self.pygame = importlib.import_module('pygame')
		# Create the buffer
		self.buffer = np.zeros((int(size[0]), int(size[1]), 3))

	"""Set the window name.
	   Args: name -> new name of the window"""

	def set_name(self, name):

		"""Set the window name.
	   Args: name -> new name of the window"""

		self.pygame.display.set_caption(name)

	"""Set screen buffer.
	   Args: buffer -> the new buffer for the window"""

	def set_buffer(self, buffer):

		"""Set screen buffer.
	   Args: buffer -> the new buffer for the window"""

		self.buffer = np.array(buffer)

	"""Set one pixel in the screen buffer.
	   Args: pixel -> the pixel position to modify
	         color -> the new color of the pixel"""

	def set_pixel(self, pixel, color):

		"""Set one pixel in the screen buffer.
	   Args: pixel -> the pixel position to modify
	         color -> the new color of the pixel"""

		self.buffer[int(pixel[0])][int(pixel[1])] = np.array(color)

	def _start(self):
		# Initialize pygame
		self.pygame.init()
		self.pygame.display.set_caption('')
		# Create the screen
		self.screen = self.pygame.display.set_mode(self.size)
		# Start the main loop
		self.running = True
		while self.running:
			# Render the buffer
			surface = self.pygame.surfarray.make_surface(self.buffer)
			self.screen.blit(surface, (0, 0))
			self.pygame.display.flip()
			# Get all events
			events = self.pygame.event.get()
			for event in events:
				if event.type == self.pygame.QUIT:
					# Quit
					if self.allow_close:
						self.running = False
				elif event.type == self.pygame.MOUSEBUTTONUP:
					# Mouse Up
					self._handle_up()
				elif event.type == self.pygame.MOUSEBUTTONDOWN:
					# Mouse Down
					self._handle_down()
		self.pygame.quit()

	def _handle_up(self):
		if hasattr(self, 'mouse_state_mem_add'):
			self.runtime.memory[self.mouse_state_mem_add] = b'\x00'

	def _handle_down(self):
		if hasattr(self, 'mouse_state_mem_add'):
			self.runtime.memory[self.mouse_state_mem_add] = b'\x01'

	"""Start the window"""

	def start(self):

		"""Start the window"""

		# Create a new thread with our starting function
		t = threading.Thread(target=self._start)
		# Start the thread
		t.start()

	"""Stop the window"""

	def stop(self):

		"""Stop the window"""

		self.running = False


"""The executor for OPL."""

class OPLExecutor:

	"""The executor for OPL.
	   Args: print_handler -> a function for printing
	         oplos -> the OS object to use, None is we use the standard OS
	         error_mode -> the error mode during runtime (ds -> display, stop : d -> display : s -> stop : None -> None)"""

	def __init__(self, print_handler=write, oplos=None, error_mode='ds'):

		"""The executor for OPL.
		   Args: print_handler -> a function for printing
		         oplos -> the OS object to use, None is we use the standard OS
		         error_mode -> the error mode during runtime (ds -> display, stop : d -> display : s -> stop : None -> None)"""

		self.print_handler = print_handler
		self.oplos = oplos
		self.error_mode = error_mode

	"""Runs a binary OPL program. 
	   Args: code -> bytearray containing OPL code.
	         runtime_args -> arguments given during runtime
	         do_split -> whether we should split the code, or if it is already split
	         set_namespace -> namespace to set to. False or None if we start normally
	         active_namespace -> the current active namespace
	   Returns: output bytearray."""

	def execute(self, code, runtime_args=[], do_split=True, set_namespace=None, active_namespace=0):

		"""Runs a binary OPL program. 
	   Args: code -> bytearray containing OPL code.
	         runtime_args -> arguments given during runtime
	         do_split -> whether we should split the code, or if it is already split
	         set_namespace -> namespace to set to. False or None if we start normally
	         active_namespace -> the current active namespace
	   Returns: output bytearray."""

		self.error = False
		# Create memory
		if not set_namespace:
			self.namespace = {0 : {}}
			self.memory = self.namespace[active_namespace]
		else:
			self.namespace = set_namespace
			self.memory = self.namespace[active_namespace]
		self.active_namespace = active_namespace
		# Create output bytearray
		self.output = bytearray()
		# Split the code into commands
		if do_split:
			split_code = self.split_code(code)
		else:
			split_code = code
		line_num = 0
		while line_num < len(split_code):
			# Get code for this line
			line_code = split_code[line_num]
			cmd_name = int.from_bytes(line_code[1], byteorder='big')
			line_args = line_code[2]
			try:
				if cmd_name == 0:
					# Start the program
					pass
				elif cmd_name == 1:
					# End the program, returning arg0
					self.output += line_args[0]
					break
				elif cmd_name == 2:
					# Set arg0 to memory address arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = line_args[0]
				elif cmd_name == 3:
					# Copy arg0 to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytearray(self.memory[int.from_bytes(line_args[0], byteorder='big')]).copy()
				elif cmd_name == 4:
					# Append data at arg0 to arg1 and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = bytearray(self.memory[int.from_bytes(line_args[1], byteorder='big')]).copy() + self.memory[int.from_bytes(line_args[0], byteorder='big')]
				elif cmd_name == 5:
					# Append data at arg0 to arg1 at position arg2
					data = self.memory[int.from_bytes(line_args[1], byteorder='big')]
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = data[ : int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big')] + self.memory[int.from_bytes(line_args[0], byteorder='big')] + data[int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big') : ]
				elif cmd_name == 6:
					# Truncate arg1 bytes from end of arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.memory[int.from_bytes(line_args[0], byteorder='big')][ : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
				elif cmd_name == 7:
					# Truncate arg1 bytes from start of arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.memory[int.from_bytes(line_args[0], byteorder='big')][int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big') : ]
				elif cmd_name == 8:
					# Truncate arg1 bytes from arg0 at arg2
					data = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					arg1 = int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
					arg2 = int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big')
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = data[ : arg2] + data[arg2 + arg1 : ]
				elif cmd_name == 9:
					# Get length of data at arg0 and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(len(self.memory[int.from_bytes(line_args[0], byteorder='big')]), 4, byteorder='big')
				elif cmd_name == 10:
					# Add the values at arg0 and arg1 and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] + struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 11:
					# Subtract the values at arg0 and arg1 and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] - struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 12:
					# Multiply the values at arg0 and arg1 and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] * struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 13:
					# Divide the values at arg0 and arg1 and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] / struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 14:
					# Raise arg0 to the power of arg1 and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] ** struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 15:
					# Preform an and gate on arg0 and arg1, save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] and struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 16:
					# Preform an or gate on arg0 and arg1, save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] or struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 17:
					# Preform an xor gate on arg0 and arg1, save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] ^ struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 18:
					# Preform a not gate on arg0, save to arg1
					output = not struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0]
					if output == False:
						output = b'/x00'
					else:
						output = b'/x01'
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = output
				elif cmd_name == 19:
					# Remove data at arg0
					del self.memory[int.from_bytes(line_args[0], byteorder='big')]
				elif cmd_name == 20:
					# Go to line arg0
					line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 21:
					# Go to line arg0 if arg1 == arg2
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] == self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 22:
					# Go to line arg0 if arg1 > arg2 (float)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) > struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 23:
					# Go to line arg0 if arg1 < arg2 (float)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) < struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 24:
					# Go to line arg0 if arg1 >= arg2 (float)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) >= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 25:
					# Go to line arg0 if arg1 <= arg2 (float)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) <= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 26:
					# Takes arg0 to arg1 from arg2, saves to arg3
					self.memory[int.from_bytes(line_args[3], byteorder='big')] = self.memory[int.from_bytes(line_args[2], byteorder='big')][int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
				elif cmd_name == 27:
					# Gets input from standard input, saves to arg0
					input_data = bytes(input(), ENCODING)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = input_data
				elif cmd_name == 28:
					# Gets arg0 of inputted cmd args and sets to arg1 (string)
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(runtime_args[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')], ENCODING)
				elif cmd_name == 29:
					# Print the memory
					self.print_handler(str(self.memory))
				elif cmd_name == 30:
					# Add data at arg0 to self.output
					print_data = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					if len(line_args) == 3:
						if line_args[2] == b'\x01':
							# Don't write to output
							pass
						elif line_args[2] == b'\x00':
							# Write to output
							self.output += print_data
					else:
						# Write to output
						self.output += print_data
					write_type = int.from_bytes(line_args[1], byteorder='big')
					# If we should print to shell
					if self.print_handler:
						# If we print directly
						if write_type == 0:
							self.print_handler(str(bytes(print_data)))
						elif write_type == 1:
							# If we print as a string
							self.print_handler(str(print_data, encoding=ENCODING))
						elif write_type == 2:
							# If we print as an int
							self.print_handler(str(int.from_bytes(print_data, byteorder='big')) + '\n')
						elif write_type == 3:
							# If we print as a float
							self.print_handler(str(struct.unpack('f', print_data)[0]) + '\n')
				elif cmd_name == 31:
					# Add the values at arg0 and arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') + int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 32:
					# Subtract the values at arg0 and arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 33:
					# Multiply the values at arg0 and arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') * int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 34:
					# Divide the values at arg0 and arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') / int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 35:
					# Raise arg0 to the power of arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') ** int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 36:
					# Preform an and gate on arg0 and arg1, save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') and int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 37:
					# Preform an or gate on arg0 and arg1, save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') or int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 38:
					# Preform an xor gate on arg0 and arg1, save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') ^ int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 39:
					# arg0 (int) to string and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(str(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')), ENCODING)
				elif cmd_name == 40:
					# arg0 (float) to string and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(str(struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0]), ENCODING)
				elif cmd_name == 41:
					# arg0 (string) to int and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(int(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING)), 4, byteorder='big')
				elif cmd_name == 42:
					# arg0 (string) to float and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = struct.pack('f', float(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING)))
				elif cmd_name == 43:
					# arg0 (int) to float and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = struct.pack('f', float(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')))
				elif cmd_name == 44:
					# arg0 (float) to int and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(int(struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0]), 4, byteorder='big')
				elif cmd_name == 45:
					# Duplicate arg0 arg1 times
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.memory[int.from_bytes(line_args[0], byteorder='big')] * int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
				elif cmd_name == 46:
					# Load file arg0 and read bytes to arg1
					if self.oplos == None:
						file_buffer = open(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING), 'rb')
						self.memory[int.from_bytes(line_args[1], byteorder='big')] = file_buffer.read()
						file_buffer.close()
					else:
						self.memory[int.from_bytes(line_args[1], byteorder='big')] = self.oplos.get_file(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
				elif cmd_name == 47:
					# Write data at arg1 to file arg0
					if self.oplos == None:
						file_buffer = open(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING), 'wb')
						file_buffer.write(self.memory[int.from_bytes(line_args[1], byteorder='big')])
						file_buffer.close()
					else:
						self.oplos.create_file(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING), self.memory[int.from_bytes(line_args[1], byteorder='big')])
				elif cmd_name == 48:
					# Delete file at arg0
					if self.oplos == None:
						os.remove(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
					else:
						self.oplos.delete_file(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
				elif cmd_name == 49:
					# Get the code buffer and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = code
				elif cmd_name == 50:
					# Change the code buffer to arg0 and set the line number to arg1
					code = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					split_code = self.split_code(code)
					line_num = int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 51:
					# Get the output buffer and set it to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.output
				elif cmd_name == 52:
					# Set the output buffer to arg0
					self.output = self.memory[int.from_bytes(line_args[0], byteorder='big')]
				elif cmd_name == 53:
					# Get binary representation of memory and set to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.get_binary_memory()
				elif cmd_name == 54:
					# Set memory using binary representation of memory at arg0
					self.set_binary_memory(self.memory[int.from_bytes(line_args[0], byteorder='big')])
				elif cmd_name == 55:
					# Run system command arg0, save output to arg1
					if self.oplos == None:
						self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes([os.system(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))])
					else:
						self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes([self.oplos.run_command(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))])
				elif cmd_name == 56:
					# Get arg0 chars from standard input, save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(getchars(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')), ENCODING)
				elif cmd_name == 57:
					# Get listdir and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = list_to_bytes([bytes(i, ENCODING) for i in os.listdir()])
				elif cmd_name == 58:
					# Pass
					pass
				elif cmd_name == 59:
					# Get time.time and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = struct.pack('f', time.time())
				elif cmd_name == 60:
					# Get time.asctime and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = bytes(time.asctime(), ENCODING)
				elif cmd_name == 61:
					# Wait arg0 (float) seconds
					time.sleep(struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0])
				elif cmd_name == 62:
					# Copy data at pointer of arg0 to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = self.memory[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')].copy()
				elif cmd_name == 63:
					# Set data at pointer at arg0 to arg1
					self.memory[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')] = line_args[1]
				elif cmd_name == 64:
					# Go to line arg0 if arg1 == arg2 else arg3
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] == self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 65:
					# Go to line arg0 if arg1 > arg2 (float) else arg3
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) > struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 66:
					# Go to line arg0 if arg1 < arg2 (float) else arg3
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) < struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 67:
					# Go to line arg0 if arg1 >= arg2 (float) else arg3
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) >= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 68:
					# Go to line arg0 if arg1 <= arg2 (float) else arg3
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) <= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 69:
					# Modulo arg0 and arg1 and save to arg2 (float)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] % struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 70:
					# Modulo arg0 and arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') % int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 71:
					# Go to line arg0 if arg1 == arg2 else arg3 (float)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) == struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 72:
					# Go to line arg0 if arg1 == arg2 (float)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) == struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 73:
					# Hash arg0 and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = hashlib.md5(self.memory[int.from_bytes(line_args[0], byteorder='big')]).digest()
				elif cmd_name == 74:
					# Create a screen with size arg0 by arg1
					self.screen = ScreenBuffer((struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0], struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0]), self)
				elif cmd_name == 75:
					# Start the screen
					self.screen.start()
				elif cmd_name == 76:
					# End the screen
					self.screen.stop()
				elif cmd_name == 77:
					# Set pixel arg0 arg1 to color (arg2 arg3 arg4)
					self.screen.set_pixel((struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0], struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0]), (struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')])[0] * 255, struct.unpack('f', self.memory[int.from_bytes(line_args[3], byteorder='big')])[0] * 255, struct.unpack('f', self.memory[int.from_bytes(line_args[4], byteorder='big')])[0] * 255))
				elif cmd_name == 78:
					# Set screen name to arg0
					self.screen.set_name(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
				elif cmd_name == 79:
					# Get the current screen buffer data and save to arg0
					buf = bytearray()
					# Iterate over all rows
					for i in self.screen.buffer:
						# Iterate over all columns
						for j in i:
							# Add the pixel
							buf += bytes([int(j[0]), int(j[1]), int(j[2])])
					# Save to memory
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = buf
				elif cmd_name == 80:
					# Set the current screen buffer using data at arg0
					# Get the buffer
					buf = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					# Iterate over rows
					p = 0
					for i in range(self.screen.buffer.shape[0]):
						for j in range(self.screen.buffer.shape[1]):
							# Set the pixel
							self.screen.set_pixel((i, j), (buf[p], buf[p + 1], buf[p + 2]))
							p += 3
				elif cmd_name == 81:
					# Get the shared OPL OS buffer and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.oplos.data['shared_buffer']
				elif cmd_name == 82:
					# Set the shared OPL OS buffer to arg0
					self.oplos.data['shared_buffer'] = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					assert len(self.oplos.data['shared_buffer']) == 64
					self.oplos.data_to_binary(self.oplos.data)
				elif cmd_name == 83:
					# Get all memory keys and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = b''.join([int.to_bytes(i, 4, byteorder='big') for i in list(self.memory.keys())])
				elif cmd_name == 84:
					# Delete all memory
					self.memory = {}
				elif cmd_name == 85:
					# Preform a bit shift left << on arg0 with arg1 bits, and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') << int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 86:
					# Preform a bit shift right >> on arg0 with arg1 bits, and save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') >> int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 87:
					# Reverse the data at arg0, save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytearray(reversed(self.memory[int.from_bytes(line_args[0], byteorder='big')]))
				elif cmd_name == 88:
					# Push code from arg0 to arg1 to a new thread. (asynchronous command) (OEP 001)
					new_code = split_code[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
					del split_code[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
					thread = threading.Thread(target=self.execute, args=(new_code, runtime_args, False, self.namespace, self.active_namespace))
					thread.start()
				elif cmd_name == 89:
					# Push code from arg0 to arg1 to a new thread. (non-async command) (OEP 001)
					new_code = split_code[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
					del split_code[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
					thread = threading.Thread(target=self.execute, args=(new_code, runtime_args, False, self.namespace, self.active_namespace))
					thread.start()
					thread.join()
				elif cmd_name == 90:
					# Switch to namespace arg0 (OEP 003)
					self.active_namespace = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
					self.memory = self.namespace[self.active_namespace]
				elif cmd_name == 91:
					# Create namespace arg0 (OEP 003)
					self.namespace[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')] = {}
				elif cmd_name == 92:
					# Delete namespace arg0 (OEP 003)
					if int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') == self.active_namespace:
						raise Exception('Cannot delete current namespace.')
					del self.namespace[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')]
				elif cmd_name == 93:
					# Get all namespace IDs and save to arg0 (OEP 003)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = b''.join([int.to_bytes(i, 4, byteorder='big') for i in list(self.namespace.keys())])
				elif cmd_name == 94:
					# Delete all but the current namespace (OEP 003)
					for key in list(self.namespace.keys()):
						if key == self.active_namespace:
							# Disregard this namespace
							pass
						else:
							# Delete this namespace
							del self.namespace[key]
				elif cmd_name == 95:
					# Copy data from arg0 in the current namespace to arg1 in namespace arg2 (OEP 007)
					self.namespace[int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big')][int.from_bytes(line_args[1], byteorder='big')] = self.memory[int.from_bytes(line_args[0], byteorder='big')]
				elif cmd_name == 96:
					# Import file at arg0 and load it into namespace arg1 (OEP 006, OEP 003)
					# Get file name
					filename = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					# Move to namespace arg1
					current_namespace = self.active_namespace
					self.active_namespace = int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
					self.memory = self.namespace[self.active_namespace]
					# Load the file
					if self.oplos == None:
						file_buffer = open(str(filename, ENCODING), 'rb')
						filedata = file_buffer.read()
						file_buffer.close()
					else:
						filedata = self.oplos.get_file(str(filename, ENCODING))
					# Execute the loaded file
					self.execute(filedata, runtime_args, True, self.namespace, self.active_namespace)
					# Move back to the original namespace
					self.active_namespace = current_namespace
					self.memory = self.namespace[self.active_namespace]
				elif cmd_name == 97:
					# Execute the code at arg0 in Python (OEP 011)
					exec(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
				elif cmd_name == 98:
					# Goto line arg0 if arg1 is in arg2 else arg3
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] in self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - 1
					else:
						line_num = int.from_bytes(self.memory[int.from_bytes(line_args[3], byteorder='big')], byteorder='big') - 1
				elif cmd_name == 99:
					# Allow closing the screen buffer (QUICK FIX)
					self.screen.allow_close = True
				elif cmd_name == 100:
					# Disallow closing the screen buffer (QUICK FIX)
					self.screen.allow_close = False
				elif cmd_name == 101:
					# Get the OPL OS system data buffer and save to arg0 (OEP 012)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.oplos.file.data
				elif cmd_name == 102:
					# Set the OPL OS system data buffer to arg0 (Dangerous function, raises a warning) (OEP 012)
					if self.print_handler:
						# Give a warning
						self.print_handler('WARNING: OPL WILL ATTEMPT TO MODIFY THE OPL OS FILE BUFFER. THIS COULD CAUSE CORRUPTION. CONTINUE? ')
						c = getchars(1).lower()
						self.print_handler('\n')
						if c == 'y':
							# Continue
							pass
						else:
							# Don't continue
							raise Exception('Program ended due to user blocking use of OPCODE 102')
					self.oplos.file.data = self.memory[int.from_bytes(line_args[0], byteorder='big')]
				elif cmd_name == 103:
					# Get the name of the OPL OS user and save to arg0 (OEP 012)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = bytes(self.oplos.data['name'], ENCODING)
				elif cmd_name == 104:
					# Set the name of the OPL OS user to arg0 (OEP 012)
					self.oplos.data['name'] = str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING)
					self.oplos.data_to_binary(self.oplos.data)
				elif cmd_name == 105:
					# Get the password hash of the OPL OS and save to arg0 (OEP 012)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.oplos.data['password_hash']
				elif cmd_name == 106:
					# Set the password hash of the OPL OS to arg0 (OEP 012)
					self.oplos.data['password_hash'] = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					self.oplos.data_to_binary(self.oplos.data)
				elif cmd_name == 107:
					# Get the current mouse x and y and set to arg0 and arg1 (OEP 017)
					pos = self.screen.pygame.mouse.get_pos()
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = int.to_bytes(pos[0], 4, byteorder='big')
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(pos[1], 4, byteorder='big')
				elif cmd_name == 108:
					# Set the memory address arg0 to be the address to use for handling mouse ups and downs (OEP 017)
					self.screen.mouse_state_mem_add = int.from_bytes(line_args[0], byteorder='big')
				elif cmd_name == 109:
					# Compile and run code at arg0 (OEP 016)
					c = OPLCompiler()
					code = c.compile(str(self.memory[int.from_bytes(line_args[0], byteorder='big')]))
					self.execute(code, runtime_args, True, self.namespace, self.active_namespace)
				elif cmd_name == 110:
					# Compile the code at arg0 and save to arg1 (OEP 016)
					c = OPLCompiler()
					code = c.compile(str(self.memory[int.from_bytes(line_args[0], byteorder='big')]))
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = code
				elif cmd_name == 111:
					# Run the code at arg0 (OEP 016)
					self.execute(self.memory[int.from_bytes(line_args[0], byteorder='big')], runtime_args, True, self.namespace, self.active_namespace)
				elif cmd_name == 112:
					# Set the error mode to DISPLAY STOP (OEP 015)
					self.error_mode = 'ds'
				elif cmd_name == 113:
					# Set the error mode to DISPLAY (OEP 015)
					self.error_mode = 'd'
				elif cmd_name == 114:
					# Set the error mode to STOP (OEP 015)
					self.error_mode = 's'
				elif cmd_name == 115:
					# Set the error mode to NONE (OEP 015)
					self.error_mode = ''
				elif cmd_name == 116:
					# Compare values arg0 and arg1 and set to arg2 (arg0 == arg1, arg2 = 0 : arg0 < arg1, arg2 = 1 : arg0 > arg1, arg2 = 2)
					arg0 = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					arg1 = self.memory[int.from_bytes(line_args[1], byteorder='big')]
					if arg0 == arg1:
						self.memory[int.from_bytes(line_args[2], byteorder='big')] = bytes([0])
					elif arg0 < arg1:
						self.memory[int.from_bytes(line_args[2], byteorder='big')] = bytes([1])
					elif arg0 > arg1:
						self.memory[int.from_bytes(line_args[2], byteorder='big')] = bytes([2])
				elif cmd_name == 117:
					# Get the IP address, and save to arg0 (OEP 002)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = bytes(socket.gethostbyname(socket.gethostname()), ENCODING)
				else:
					# If we encounter an error due to the cmd not being a cmd
					raise Exception('Not a command.')
				# Increment the line number
				line_num += 1
				# Update the namespace (OEP 003)
				self.namespace[self.active_namespace] = self.memory
			except Exception as e:
				if self.error_mode == 'ds':
					self.output += b'\x00\x00\x00\x01'
					if self.print_handler:
						self.print_handler('ERROR: ' + str(e) + ' LINE: ' + str(line_num) + ' CODE: ' + str(line_code) + '\n')
					self.error = True
					break
				elif self.error_mode == 'd':
					self.output += b'\x00\x00\x00\x01'
					if self.print_handler:
						self.print_handler('ERROR: ' + str(e) + ' LINE: ' + str(line_num) + ' CODE: ' + str(line_code) + '\n')
					line_num += 1
					self.error = True
				elif self.error_mode == 's':
					break
				elif self.error_mode == '':
					line_num += 1

		# Return output
		return self.output

	"""Splits code into commands.
	   Args: code -> bytearray containing OPL code to be split.
	   Returns: list containing lists of split commands."""

	def split_code(self, code):

		"""Splits code into commands.
	   Args: code -> bytearray containing OPL code to be split.
	   Returns: list containing lists of split commands."""

		split_code = []
		# Iterate over code
		i = 0
		while i < len(code):
			temp_cmd = []
			# Get line number (4 bytes)
			line_num = int.from_bytes(code[i : i + 4], byteorder='big')
			i += 4
			# Check which command it is (4 bytes)
			cmd_name = code[i : i + 4]
			i += 4
			# Get number of arguments (4 bytes)
			num_args = int.from_bytes(code[i : i + 4], byteorder='big')
			i += 4
			args = []
			for arg_num in range(num_args):
				# Get length of current argument (4 bytes)
				temp_arg_len = int.from_bytes(code[i : i + 4], byteorder='big')
				i += 4
				# Get the argument data
				arg_data = code[i : i + temp_arg_len]
				i += temp_arg_len
				# Add the data to args
				args.append(arg_data)
			# Add all code data to the split_code list
			split_code.append([line_num, cmd_name, args])
		# Return split_code
		return split_code

	"""Iterates through memory and returns a binary representation of memory."""

	def get_binary_memory(self):

		"""Iterates through memory and returns a binary representation of memory."""

		self.binary_memory = bytearray()
		# Iterate over memory
		for key in self.memory:
			# Add key number (4 bytes)
			self.binary_memory += int.to_bytes(key, 4, byteorder='big').rjust(4, b'\x00')
			# Add length of memory data (4 bytes)
			self.binary_memory += int.to_bytes(len(self.memory[key]), 4, byteorder='big').rjust(4, b'\x00')
			# Add binary data
			self.binary_memory += self.memory[key]
		# Return final binary memory
		return self.binary_memory

	"""Sets memory using a binary representation of memory.
	   Args: binary_memory -> the binary representation of memory"""

	def set_binary_memory(self, binary_memory):

		"""Sets memory using a binary representation of memory.
	   Args: binary_memory -> the binary representation of memory"""

		self.binary_memory = binary_memory
		new_memory = {}
		# Iterate through all memory
		i = 0
		while i < len(self.binary_memory):
			# Get memory address (4 bytes)
			adress = int.from_bytes(self.binary_memory[i : i + 4], byteorder='big')
			i += 4
			# Get length of data (4 bytes)
			length = int.from_bytes(self.binary_memory[i : i + 4], byteorder='big')
			i += 4
			# Get data
			data = self.binary_memory[i : i + length]
			i += length
			# Set new memory
			new_memory[adress] = data
		# Set new memory
		self.memory = new_memory


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
		# Iterate over all lines
		line_num = 0
		for line_code in code_split:
			if line_code == ['']:
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
						arg = bytes([int(i) for i in arg.split(',')])
					compiled_code += int.to_bytes(len(arg), 4, byteorder='big') + arg
				line_num += 1
			except Exception as e:
				write('ERROR: ' + str(e) + ' LINE: ' + str(line_num) + ' CODE: ' + str(line_code) + '\n')
				break
		return compiled_code


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

