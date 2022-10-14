"""Executor for the OPL language. Written by Kevin Chen."""


# Imports
from .functions import *
from .screenbuffer import ScreenBuffer
from . import ENCODING
from .module import BaseModule

import sys, os
import time
import struct
import hashlib
import numpy as np
import threading
import socket
import dill
import math


"""The executor for OPL."""

class OPLExecutor:

	"""The executor for OPL.
	   Args: print_handler -> a function for printing
	         oplos -> the OS object to use, None is we use the standard OS
	         error_mode -> the error mode during runtime (ds -> display, stop : d -> display : s -> stop : None -> None)
	         opefiles -> the files to use if we are running in an ope"""

	def __init__(self, print_handler=write, oplos=None, error_mode='ds', opefiles=None):

		"""The executor for OPL.
		   Args: print_handler -> a function for printing
		         oplos -> the OS object to use, None is we use the standard OS
		         error_mode -> the error mode during runtime (ds -> display, stop : d -> display : s -> stop : None -> None)
		         opefiles -> the files to use if we are running in an ope"""

		self.print_handler = print_handler
		self.oplos = oplos
		self.error_mode = error_mode
		self.opefiles = opefiles

	"""Runs a binary OPL program. 
	   Args: code -> bytearray containing OPL code.
	         runtime_args -> arguments given during runtime
	         do_split -> whether we should split the code, or if it is already split
	         set_namespace -> namespace to set to. False or None if we start normally
	         active_namespace -> the current active namespace
	         labels -> any extra labels to use
	         sudo -> run as superuser
	   Returns: output bytearray."""

	def execute(self, code, runtime_args=[], do_split=True, set_namespace=None, active_namespace=0, labels={}, sudo=False):

		"""Runs a binary OPL program. 
	   Args: code -> bytearray containing OPL code.
	         runtime_args -> arguments given during runtime
	         do_split -> whether we should split the code, or if it is already split
	         set_namespace -> namespace to set to. False or None if we start normally
	         active_namespace -> the current active namespace
	         labels -> any extra labels to use
	         sudo -> run as superuser
	   Returns: output bytearray."""

		# Increment the IN_PROCESS OPL OS flag if OPLOS exists.
		if self.oplos:
			self.oplos.data['shared_buffer'] = bytearray(self.oplos.data['shared_buffer'])
			self.oplos.data['shared_buffer'][1] += 1
			self.oplos.data_to_binary(self.oplos.data)
	
		self.running = True
		self.error = False
		self.useopefiles = False
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
			split_code, labels = self.split_code(code)
		else:
			split_code = code
			labels = labels
		line_num = 0
		while line_num < len(split_code) and self.running:
			# Get code for this line
			line_code = split_code[line_num]
			cmd_name = int.from_bytes(line_code[1], byteorder='big')
			line_args = line_code[2]
			try:
				# Check for a module (OEP 019)
				if 'loaded_module' in self.memory.keys():
					# Execute the begin call
					self.memory['loaded_module'].on_begin_opcode(self, cmd_name, line_args)
					# Update the namespace (OEP 003)
					self.namespace[self.active_namespace] = self.memory
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
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] & struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 16:
					# Preform an or gate on arg0 and arg1, save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] or struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 17:
					# Preform an xor gate on arg0 and arg1, save to arg2
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = struct.pack('f', struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0] ^ struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')])[0])
				elif cmd_name == 18:
					# Preform a not gate on arg0, save to arg1
					output = not int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
					if output == False:
						output = b'\x00\x00\x00\x00'
					else:
						output = b'\x00\x00\x00\x01'
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
							self.print_handler(str(int.from_bytes(print_data, byteorder='big')))
						elif write_type == 3:
							# If we print as a float
							self.print_handler(str(struct.unpack('f', print_data)[0]))
						elif write_type == 4:
							# If we print as a signed int
							self.print_handler(str(int.from_bytes(print_data, byteorder='big', signed=True)))
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
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') / int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')), 4, byteorder='big')
				elif cmd_name == 35:
					# Raise arg0 to the power of arg1 and save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') ** int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
				elif cmd_name == 36:
					# Preform an and gate on arg0 and arg1, save to arg2 (int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') & int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big'), 4, byteorder='big')
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
					if not self.useopefiles:
						if self.oplos == None:
							file_buffer = open(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING), 'rb')
							self.memory[int.from_bytes(line_args[1], byteorder='big')] = file_buffer.read()
							file_buffer.close()
						else:
							self.memory[int.from_bytes(line_args[1], byteorder='big')] = self.oplos.get_file(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
					else:
						self.memory[int.from_bytes(line_args[1], byteorder='big')] = self.opefiles[str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING)]
				elif cmd_name == 47:
					# Write data at arg1 to file arg0
					if self.oplos == None:
						file_buffer = open(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING), 'wb')
						file_buffer.write(self.memory[int.from_bytes(line_args[1], byteorder='big')])
						file_buffer.close()
					else:
						if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
							self.oplos.create_file(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING), self.memory[int.from_bytes(line_args[1], byteorder='big')])
				elif cmd_name == 48:
					# Delete file at arg0
					if self.oplos == None:
						os.remove(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING))
					else:
						if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
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
						if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
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
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytearray(self.memory[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')]).copy()
				elif cmd_name == 63:
					# Set data at pointer at arg0 to arg1
					self.memory[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')] = self.memory[int.from_bytes(line_args[1], byteorder='big')]
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
					# Hash arg0 and save to arg1 (sha256)
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = hashlib.sha256(self.memory[int.from_bytes(line_args[0], byteorder='big')]).digest()
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
					# Ensure bit 0 didn't change
					if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
						self.oplos.data['shared_buffer'] = self.memory[int.from_bytes(line_args[0], byteorder='big')]
						assert len(self.oplos.data['shared_buffer']) == 512
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
					thread = threading.Thread(target=self.execute, args=(new_code, runtime_args, False, self.namespace, self.active_namespace, labels, sudo))
					thread.start()
				elif cmd_name == 89:
					# Push code from arg0 to arg1 to a new thread. (non-async command) (OEP 001)
					new_code = split_code[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
					del split_code[int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') : int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')]
					thread = threading.Thread(target=self.execute, args=(new_code, runtime_args, False, self.namespace, self.active_namespace, labels, sudo))
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
					if self.oplos.data['shared_buffer'][0] != 0:
						raise Exception('Loading modules in safe mode is not permitted.')
					# Get file name
					filename = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					# Move to namespace arg1
					current_namespace = self.active_namespace
					self.active_namespace = int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
					self.memory = self.namespace[self.active_namespace]
					# Load the file
					if not self.useopefiles:
						if self.oplos == None:
							file_buffer = open(str(filename, ENCODING), 'rb')
							filedata = file_buffer.read()
							file_buffer.close()
						else:
							filedata = self.oplos.get_file(str(filename, ENCODING))
					else:
						filedata = self.opefiles[str(filename, ENCODING)]
					# Execute the loaded file
					self.execute(filedata, runtime_args, True, self.namespace, self.active_namespace, sudo=sudo)
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
					if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
						self.oplos.file.data = self.memory[int.from_bytes(line_args[0], byteorder='big')]
				elif cmd_name == 103:
					# Get the name of the OPL OS user and save to arg0 (OEP 012)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = bytes(self.oplos.data['name'], ENCODING)
				elif cmd_name == 104:
					# Set the name of the OPL OS user to arg0 (OEP 012)
					if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
						self.oplos.data['name'] = str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING)
						self.oplos.data_to_binary(self.oplos.data)
				elif cmd_name == 105:
					# Get the password hash of the OPL OS and save to arg0 (OEP 012)
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = self.oplos.data['password_hash']
				elif cmd_name == 106:
					# Set the password hash of the OPL OS to arg0 (OEP 012)
					if self.oplos.data['shared_buffer'][0] == 0 or sudo == True:
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
					from . import OPLCompiler
					c = OPLCompiler()
					code = c.compile(str(self.memory[int.from_bytes(line_args[0], byteorder='big')]))
					self.execute(code, runtime_args, True, self.namespace, self.active_namespace, sudo=sudo)
				elif cmd_name == 110:
					# Compile the code at arg0 and save to arg1 (OEP 016)
					from . import OPLCompiler
					c = OPLCompiler()
					code = c.compile(str(self.memory[int.from_bytes(line_args[0], byteorder='big')]))
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = code
				elif cmd_name == 111:
					# Run the code at arg0 (OEP 016)
					self.execute(self.memory[int.from_bytes(line_args[0], byteorder='big')], runtime_args, True, self.namespace, self.active_namespace, sudo=sudo)
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
				elif cmd_name == 118:
					# Load a binary module at arg0 to the current active namespace (Overwrites the current loaded module) (OEP 019)
					filename = self.memory[int.from_bytes(line_args[0], byteorder='big')]
					# Get the file data
					if not self.useopefiles:
						if self.oplos == None:
							file_buffer = open(str(filename, ENCODING), 'rb')
							filedata = file_buffer.read()
							file_buffer.close()
						else:
							filedata = self.oplos.get_file(str(filename, ENCODING))
					else:
						filedata = self.opefiles[str(filename, ENCODING)]
					# Load the module              \/ Load the class   \/ Create an instance
					self.memory['loaded_module'] = dill.loads(filedata)()
					# Initialize the functions for the module, so it can use write, etc.
					self.memory['loaded_module'].init_functions()
				elif cmd_name == 119:
					# Remove the current loaded module for the active namespace (OEP 019)
					del self.memory['loaded_module']
				elif cmd_name == 120:
					# Set the use OPE files mode to true (OEP 013)
					self.useopefiles = True
				elif cmd_name == 121:
					# Set the use OPE files mode to false (OEP 013)
					self.useopefiles = False
				elif cmd_name == 122:
					# Get the number of runtime args and save it to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = bytes([len(runtime_args)])
				elif cmd_name == 123:
					# Add arg0 and arg1 and save it to arg2 without 4 byte length restriction
					number = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') + int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
					number_len = int(math.log(n, 256)) + 1
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(number, number_len, byteorder='big')
				elif cmd_name == 124:
					# Subtract arg0 from arg1 and save it to arg2 without 4 byte length restriction
					number = int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big') - int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
					number_len = int(math.log(n, 256)) + 1
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(number, number_len, byteorder='big')
				elif cmd_name == 125:
					# Create a label at the current line named arg0 (OEP 022)
					pass
				elif cmd_name == 126:
					# Go to label arg0 (OEP 022)
					line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 127:
					# Go to label arg0 if arg1 == arg2 (OEP 022)
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] == self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 128:
					# Go to label arg0 if arg1 != arg2 (OEP 022)
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] != self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 129:
					# Go to label arg0 if arg1 > arg2 (float) (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) > struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 130:
					# Go to label arg0 if arg1 < arg2 (float) (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) < struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 131:
					# Go to label arg0 if arg1 >= arg2 (float) (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) >= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 132:
					# Go to label arg0 if arg1 <= arg2 (float) (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) <= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
				elif cmd_name == 133:
					# Go to label arg0 if arg1 == arg2 else arg3 (OEP 022)
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] == self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 134:
					# Go to label arg0 if arg1 > arg2 (float) else arg3 (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) > struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 135:
					# Go to label arg0 if arg1 < arg2 (float) else arg3 (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) < struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 136:
					# Go to label arg0 if arg1 >= arg2 (float) else arg3 (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) >= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 137:
					# Go to label arg0 if arg1 <= arg2 (float) else arg3 (OEP 022)
					if struct.unpack('f', self.memory[int.from_bytes(line_args[1], byteorder='big')]) <= struct.unpack('f', self.memory[int.from_bytes(line_args[2], byteorder='big')]):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 138:
					# Go to label arg0 if arg1 > arg2 (int) else arg3 (OEP 022)
					if int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big') > int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big'):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 139:
					# Go to label arg0 if arg1 < arg2 (int) else arg3 (OEP 022)
					if int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big') < int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big'):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 140:
					# Go to label arg0 if arg1 >= arg2 (int) else arg3 (OEP 022)
					if int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big') >= int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big'):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 141:
					# Go to label arg0 if arg1 <= arg2 (int) else arg3 (OEP 022)
					if int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big') <= int.from_bytes(self.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big'):
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 142:
					# Go to label arg0 if arg1 != arg2 else arg3 (OEP 022)
					if self.memory[int.from_bytes(line_args[1], byteorder='big')] != self.memory[int.from_bytes(line_args[2], byteorder='big')]:
						line_num = labels[bytes(line_args[0])] - 1
					else:
						line_num = labels[bytes(line_args[3])] - 1
				elif cmd_name == 143:
					# Push code from labels arg0 to arg1 to a new thread. (asynchronous command) (OEP 001) (OEP 022)
					new_code = split_code[labels[bytes(line_args[0])] : labels[bytes(line_args[1])]]
					del split_code[labels[bytes(line_args[0])] : labels[bytes(line_args[1])]]
					thread = threading.Thread(target=self.execute, args=(new_code, runtime_args, False, self.namespace, self.active_namespace, labels, sudo))
					thread.start()
				elif cmd_name == 144:
					# Push code from labels arg0 to arg1 to a new thread. (non-async command) (OEP 001) (OEP 022)
					new_code = split_code[labels[bytes(line_args[0])] : labels[bytes(line_args[1])]]
					del split_code[labels[bytes(line_args[0])] : labels[bytes(line_args[1])]]
					thread = threading.Thread(target=self.execute, args=(new_code, runtime_args, False, self.namespace, self.active_namespace, labels, sudo))
					thread.start()
					thread.join()
				elif cmd_name == 145:
					# Add the values at arg0 and arg1 and save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) + int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 146:
					# Subtract the values at arg0 and arg1 and save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) - int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 147:
					# Multiply the values at arg0 and arg1 and save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) * int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 148:
					# Divide the values at arg0 and arg1 and save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) / int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 149:
					# Raise arg0 to the power of arg1 and save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) ** int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 150:
					# Preform an and gate on arg0 and arg1, save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) & int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 151:
					# Preform an or gate on arg0 and arg1, save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) or int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 152:
					# Preform an xor gate on arg0 and arg1, save to arg2 (signed int)
					self.memory[int.from_bytes(line_args[2], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True) ^ int.from_bytes(self.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big', signed=True)
				elif cmd_name == 153:
					# arg0 (signed int) to string and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(str(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True)), ENCODING)
				elif cmd_name == 154:
					# arg0 (signed int) to float and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = struct.pack('f', int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True))
				elif cmd_name == 155:
					# arg0 (signed int) to int and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big', signed=True), 4, byteorder='big')
				elif cmd_name == 156:
					# arg0 (string) to signed int and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(int(str(self.memory[int.from_bytes(line_args[0], byteorder='big')], ENCODING)), 4, byteorder='big', signed=True)
				elif cmd_name == 157:
					# arg0 (float) to signed int and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(int(struct.unpack('f', self.memory[int.from_bytes(line_args[0], byteorder='big')])[0]), 4, byteorder='big', signed=True)
				elif cmd_name == 158:
					# arg0 (int) to signed int and save to arg1
					self.memory[int.from_bytes(line_args[1], byteorder='big')] = int.to_bytes(int.from_bytes(self.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big'), 4, byteorder='big', signed=True)
				elif cmd_name == 159:
					# Stop the program suddenly, including all subprocesses
					self.running = False
				elif cmd_name == 160:
					# Get shared buffer byte 1 (IN_PROCESS) and save to arg0
					self.memory[int.from_bytes(line_args[0], byteorder='big')] = bytes([self.oplos.data['shared_buffer'][1]])
				else:
					# Check if the OPCODE is defined in a module (OEP 019)
					if 'loaded_module' in self.memory.keys() and cmd_name in self.memory['loaded_module'].defined_opcodes:
						# Attempt to execute the the command
						self.memory['loaded_module'].handle_command(self, cmd_name, line_args)
					else:
						# If we encounter an error due to the OPCODE not being a OPCODE
						raise Exception('Not a command.')
				# Check for a module (OEP 019)
				if 'loaded_module' in self.memory.keys():
					# Execute the end call
					self.memory['loaded_module'].on_end_opcode(self, cmd_name, line_args)
					# Update the namespace (OEP 003)
					self.namespace[self.active_namespace] = self.memory
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

		# Decrement the IN_PROCESS OPL OS flag if OPLOS exists.
		if self.oplos:
			self.oplos.data['shared_buffer'] = bytearray(self.oplos.data['shared_buffer'])
			self.oplos.data['shared_buffer'][1] -= 1
			self.oplos.data_to_binary(self.oplos.data)
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
		labels = {}
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
			# Check if the command is 125 (OEP 022)
			if int.from_bytes(cmd_name, byteorder='big') == 125:
				# This is a label
				labels[bytes(args[0])] = line_num
		# Return split_code
		return split_code, labels

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

