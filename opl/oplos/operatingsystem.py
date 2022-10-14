"""File Buffer for the OPL OS. Written by Kevin Chen."""


# Imports
import sys, os
import hashlib
import shlex
from . import ENCODING, __version__
from .. import opl
from .functions import write, get_password, editor
from .filebuffer import FileBuffer


"""OPL Operating System.
	   Args: osfile -> the name of the file for the OS to use"""

class OPLOS:

	"""OPL Operating System.
	   Args: osfile -> the name of the file for the OS to use"""

	def __init__(self, osfile):

		"""OPL Operating System.
	   Args: osfile -> the name of the file for the OS to use"""

		self.file = FileBuffer(osfile, True, True)
		# Check for an empty file
		if len(self.file.data) == 0:
			pass
		else:
			self.binary_to_data()

	"""Start the OS."""

	def start(self):

		"""Start the OS."""

		self.data['shared_buffer'] = bytearray(self.data['shared_buffer'])
		self.data['shared_buffer'][1] += 1
		self.data_to_binary(self.data)

		try:
			self.running = True
			write('OPL Operating System - STARTING\n')
			write('NAME: ' + self.data['name'] + '\n')
			password_hash_input = hashlib.sha256(bytes(get_password(), ENCODING)).digest()
			if password_hash_input == self.data['password_hash']:
				# Correct password
				pass
			else:
				write('INCORRECT PASSWORD\n')
				sys.exit()
			# Try to run the initialization OPC, if it exists
			if '_BEGIN_SYSTEM_OPC' in self.data['files']:
				# Execute the file
				e = opl.opl.OPLExecutor(oplos=self)
				e.execute(self.get_file('_BEGIN_SYSTEM_OPC'))
			# Start main loop
			while self.running:
				try:
					command = input('OPLOS ' + self.data['name'] + ' >> ')
					try:
						self.run_command(command)
					except Exception as e:
						write('ERROR: ' + str(e) + '\n')
				except:
					write('ERROR\n')
		except:
			write('FATAL ERROR\n')

		self.data['shared_buffer'] = bytearray(self.data['shared_buffer'])
		self.data['shared_buffer'][1] -= 1
		self.data_to_binary(self.data)

	"""Run a command.
	   Args: command -> the command to run
	         sudo -> should we run with infinite power"""

	def run_command(self, command, sudo=False):

		"""Run a command.
		   Args: command -> the command to run
		         sudo -> should we run with infinite power"""

		# Get global OPL for updating
		global opl
		split_command = shlex.split(command)
		if split_command == []:
			return None
		command = split_command[0]
		args = split_command[1 : ]
		if command == 'exit':
			# Exit the system
			# Try to run the exit OPC, if it exists
			if '_EXIT_SYSTEM_OPC' in self.data['files']:
				# Execute the file
				e = opl.opl.OPLExecutor(oplos=self)
				e.execute(self.get_file('_EXIT_SYSTEM_OPC'))
			self.running = False
		elif command == 'ldir':
			# List the directory or files beginning with arg0
			if len(args) == 0:
				files_to_display = list(self.data['files'].keys())
			else:
				filenames = self.data['files'].keys()
				files_to_display = []
				for i in filenames:
					if i.startswith(args[0] + '/'):
						files_to_display.append(i)
			write('"' + '", "'.join(files_to_display) + '"\n')
		elif command == 'write':
			# Write the following string
			write(args[0] + '\n')
		elif command == 'view':
			# View the following file
			write(str(self.data['files'][args[0]], ENCODING) + '\n')
		elif command == 'rename':
			# Rename a file
			self.rename_file(args[0], args[1])
		elif command == 'edit':
			# Open an editor on a file
			text = editor()
			s = input('Save? ')[0].lower()
			if s == 'y':
				self.create_file(args[0], bytes(text, ENCODING))
		elif command == 'del':
			# Delete the file at arg0
			self.delete_file(args[0])
		elif command == 'opl':
			# Run the opl code at arg0
			e = opl.opl.OPLExecutor(oplos=self)
			e.execute(self.get_file(args[0]), runtime_args=args[1 : -1], sudo=sudo)
			if len(args[1 : ]) >= 1:
				if args[-1] == '-o':
					write(str(e.output) + '\n')
				else:
					self.create_file(args[-1], e.output)
		elif command == 'oplc':
			# Compile the OPL code at arg0, save to arg1
			e = opl.opl.OPLCompiler()
			self.create_file(args[1], e.compile(str(self.get_file(args[0]), ENCODING)))
		elif command == 'opld':
			# Decompile the OPLC code at arg0, save to arg1
			e = opl.opl.OPLDecompiler()
			self.create_file(args[1], bytes(e.decompile(self.get_file(args[0])), ENCODING))
		elif command == 'cname':
			# Change the OS name to arg0
			self.data['name'] = args[0]
			self.data_to_binary(self.data)
		elif command == 'cpass':
			# Change the OS password to arg0
			self.data['password_hash'] = hashlib.sha256(bytes(args[0], ENCODING)).digest()
			self.data_to_binary(self.data)
		elif command == 'ropl':
			# Reload the OPL language
			import importlib
			importlib.reload(opl.opl)
		elif command == 'vopl':
			# Get the OPL version
			write(opl.opl.__version__ + '\n')
		elif command == 'backup':
			# Backup the OS to osname.backup
			f = open(self.file.filename + '.backup', 'wb')
			f.write(self.file.data)
			f.close()
		elif command == 'vers':
			# Get the current OPL OS version (QFI 001)
			write(__version__ + '\n')
		elif command == 'ip':
			# Get the IP for this OS (OEP 002)
			import socket
			write(socket.gethostbyname(socket.gethostname()) + '\n')
		elif command == 'opec':
			# Compile main file arg1 and files arg2 - argn to file arg0 as an OPE
			c = opl.opl.OPECompiler()
			mainfile = self.get_file(args[1])
			files = {name : self.get_file(name) for name in args[2 : ]}
			self.create_file(args[0], c.compile(mainfile, files))
		elif command == 'clear':
			# Clear the sreen
			os.system('clear' if os.name == 'posix' else 'cls')
		elif command == 'safe':
			# Set safe mode to arg0 (on or off)
			self.data['shared_buffer'] = bytearray(self.data['shared_buffer'])
			if len(args) > 0 and args[0] == 'on':
				self.data['shared_buffer'][0] = 1
			elif len(args) > 0 and args[0] == 'off':
				self.data['shared_buffer'][0] = 0
			else:
				write('ON\n' if self.data['shared_buffer'][0] == 1 else 'OFF\n')
			self.data_to_binary(self.data)
		elif command == 'restore':
			# Restore the OS to the current saved state in memory
			self.data_to_binary(self.data)
		elif command == 'sudo':
			# Run the following command as superuser
			self.run_command(shlex.join(args), True)
		elif command == 'credits':
			# Display credits
			write('CREDITS: All work by Kevin Chen\n(C) Cubeflix 2021\n')
		elif command == 'sh':
			# Run the shell file (.shx) at arg0
			file = self.get_file(args[0])
			self.run_sh(str(file, ENCODING), args[1 : ], sudo)
		elif command == 'help':
			# Returns all commands and their descriptions
			write('''exit -> exit the os
ldir -> list the directory or files beginning with arg0
write -> echo the text back
view -> view the file
rename -> rename the file
edit -> edit the file in an editor
del -> delete the file
opl -> execute the file
oplc -> compile the file
opld -> decompile the file
cname -> change the os name
cpass -> change the os password
ropl -> update OPL to the newest version
vopl -> get the OPL version
backup -> backup the OS to osname.backup
vers -> get the current OPL OS version
ip -> get the IP address for the OS
opec -> compile main file arg1 and files arg2 - argn to file arg0 as an OPE
clear -> clear the screen
safe -> set safe mode to arg0 (on or off)
restore -> restore the OS to the current saved state in memory
sudo -> run the following command as superuser
credits -> display credits
sh -> run the shell file (.shx) at arg0
help -> display this message
''')
		else:
			# Check if this command is an OPE file
			if (command + '.ope') in self.data['files'].keys():
				# Run the OPE
				e = opl.opl.OPEExecutor(oplos=self)
				e.execute(self.get_file(command + '.ope'), runtime_args=args, sudo=sudo)
				if len(args) >= 1:
					if args[-1] == '-o':
						write(str(e.output) + '\n')
					else:
						self.create_file(args[-1], e.output)
			else:
				# Error
				raise Exception('No such command.')
				return 1
		return 0

	"""Create a file.
	   Args: name -> name of the file
	         data -> bytes data of the file"""

	def create_file(self, name, data):

		"""Create a file.
	   Args: name -> name of the file
	         data -> bytes data of the file"""

		self.data['files'][name] = data
		self.data_to_binary(self.data)

	"""Delete a file.
	   Args: name -> name of the file"""

	def delete_file(self, name):

		"""Delete a file.
	   Args: name -> name of the file"""

		del self.data['files'][name]
		self.data_to_binary(self.data)

	"""Get the data of a file.
	   Args: name -> name of the file"""

	def get_file(self, name):

		"""Get the data of a file.
	   Args: name -> name of the file"""

		return self.data['files'][name]

	"""Rename a file.
	   Args: name -> name of the file
	         new_name -> new name of the file"""

	def rename_file(self, name, new_name):

		"""Rename a file.
	   Args: name -> name of the file
	         new_name -> new name of the file"""

		data = self.get_file(name)
		self.create_file(new_name, data)

	"""Format the OS.
	   Args: name -> new name of the OS
	         password -> password for the new OS"""

	def format(self, name, password):

		"""Format the OS.
	   Args: name -> new name of the OS
	         password -> password for the new OS"""

		new_data = bytearray()
		new_data += int.to_bytes(len(name), 4, byteorder='big')
		new_data += bytes(name, ENCODING)
		new_data += hashlib.sha256(bytes(password, ENCODING)).digest()
		new_data += bytes(512)
		self.file.data = new_data
		self.binary_to_data()

	"""Gets a dict of the OS data using the binary representation of the data."""

	def binary_to_data(self):

		"""Gets a dict of the OS data using the binary representation of the data."""

		data = self.file.data
		# Get name
		len_name = int.from_bytes(data[ : 4], byteorder='big')
		name = str(data[4 : 4 + len_name], ENCODING)
		# Get password
		password_hash = data[4 + len_name : 4 + len_name + 32]
		# Get files
		i = 4 + len_name + 32
		files = {}
		while i < len(data) - 512:
			# Get file name
			file_name_len = int.from_bytes(data[i : i + 4], byteorder='big')
			i += 4
			file_name = data[i : i + file_name_len]
			i += file_name_len
			# Get file data
			file_len = int.from_bytes(data[i : i + 4], byteorder='big')
			i += 4
			file_data = data[i : i + file_len]
			i += file_len
			files[str(file_name, ENCODING)] = file_data
		# Get shared buffer (512 bytes)
		shared_buffer = data[i : ]
		# Set data
		self.data = {'name' : name, 'password_hash' : password_hash, 'files' : files, 'shared_buffer' : shared_buffer}

	"""Converts a data dict to binary data.
	   Args: data -> the data dict to convert"""

	def data_to_binary(self, data):

		"""Converts a data dict to binary data.
	   Args: data -> the data dict to convert"""

		new_data = bytearray()
		new_data += int.to_bytes(len(data['name']), 4, byteorder='big')
		new_data += bytes(data['name'], ENCODING)
		new_data += data['password_hash']
		# Add files
		for file in data['files']:
			new_data += int.to_bytes(len(file), 4, byteorder='big')
			new_data += bytes(file, ENCODING)
			new_data += int.to_bytes(len(data['files'][file]), 4, byteorder='big')
			new_data += data['files'][file]
		# Get shared buffer
		new_data += data['shared_buffer']
		# Update data
		self.file.data = new_data
		self.binary_to_data()

	"""Run a shell file.
	   Args: source -> shell file source
	   		 args -> given args
	   		 sudo -> should we run with infinite power"""

	def run_sh(self, source, args, sudo=False):

		"""Run a shell file.
		   Args: source -> shell file source
		   		 args -> given args
		   		 sudo -> should we run with infinite power"""

		# Replace args
		for i, arg in enumerate(args):
			argname = '$' + str(i)
			source = source.replace(argname, arg)
		# Split into commands
		split_source = source.split('\n')
		# Run each command
		for command in split_source:
			if command.startswith('#'):
				continue
			self.run_command(command, sudo)
		return 0
