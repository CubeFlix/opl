"""The OPL Operating System in Python. Written by Kevin Chen."""

__version__ = '2.3'

# Imports
import sys
import hashlib
import shlex
import main as opl


# Encoding type
ENCODING = 'utf-8'

# All exports
__all__ = ['FileBuffer', 'OPLOS', 'editor']


"""Opens a code/text editor, and returns the output."""

def editor():

	"""Opens a code/text editor, and returns the output."""

	# Current line number
	l = 0
	# If we are in a string
	in_string = False
	# Current code
	code = ''
	# Keep taking input
	while True:
		# Take input
		d = input(str(l) + ': ')
		# Parse input
		if len(d) == 0:
			# Newline
			pass
		elif d[0] == '/':
			# Comment
			code += d
		elif d[0] == '\x07':
			# Quit
			break
		else:
			# Any other string/code line
			code += d
			for char in d:
				if char in ('"', '\''):
				# We either break out of or enter a string
					if in_string == char:
						in_string = False
					elif in_string == False:
						in_string = char
			if in_string:
				# Don't add to the line count
				pass
			else:
				# Add to the line count
				l += 1
		# Add a newline char
		code += '\n'
	# Return the code/text
	return code


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
		# Else
		else:
			# Add the char
			password += char
			sys.stdout.write('*')
			sys.stdout.flush()
	# Return the password
	return password


"""A simple file buffer wrapper that saves automatically.
	   Args: filename -> name of the file
	         use_binary -> whether to use binary mode
	         autosave -> whether to autosave"""

class FileBuffer:

	"""A simple file buffer wrapper that saves automatically.
	   Args: filename -> name of the file
	         use_binary -> whether to use binary mode
	         autosave -> whether to autosave"""

	def __init__(self, filename, use_binary=True, autosave=True):
		self.filename = filename
		self.autosave = autosave
		self.use_binary = 'b' if use_binary else ''
		# Get current data
		try:
			temp_data_buf = open(filename, 'r' + self.use_binary)
			self._data = temp_data_buf.read()
			temp_data_buf.close()
		except:
			self._data = bytearray()
	
	"""A setter to set our data.
	   Args: new_data -> the new data to set to"""

	def set_data(self, new_data):

		"""A setter to set our data.
	   Args: new_data -> the new data to set to"""

		self._data = new_data
		if self.autosave:
			self.save()

	"""A getter for our data."""

	def get_data(self):

		"""A getter for our data."""

		return self._data

	"""Why delete data?"""

	def del_data(self):

		"""Why delete data?"""

		pass

	"""Data Property"""

	data = property(get_data, set_data, del_data)

	"""Saves the data to the file."""

	def save(self):

		"""Saves the data to the file."""

		new_buf = open(self.filename, 'w' + self.use_binary)
		new_buf.write(self._data)
		new_buf.close()


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

		self.running = True
		write('OPL Operating System - STARTING\n')
		write('NAME: ' + self.data['name'] + '\n')
		password_hash_input = hashlib.md5(bytes(get_password(), ENCODING)).digest()
		if password_hash_input == self.data['password_hash']:
			# Correct password
			pass
		else:
			write('INCORRECT PASSWORD\n')
			sys.exit()
		# Start main loop
		while self.running:
			command = input('OPLOS ' + self.data['name'] + ' >> ')
			try:
				self.run_command(command)
			except Exception as e:
				write('ERROR: ' + str(e) + ' \n')

	"""Run a command.
	   Args: command -> the command to run"""

	def run_command(self, command):

		"""Run a command.
	   Args: command -> the command to run"""

		# Get global OPL for updating
		global opl
		split_command = shlex.split(command)
		if split_command == []:
			return None
		command = split_command[0]
		args = split_command[1 : ]
		if command == 'exit':
			# Exit the system
			self.running = False
		elif command == 'ldir':
			# List the directory
			write('"' + '", "'.join(list(self.data['files'].keys())) + '"\n')
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
			e = opl.OPLExecutor(oplos=self)
			e.execute(self.get_file(args[0]), runtime_args=args[1 : -1])
			if len(args) > 1:
				if args[-1] == '-o':
					write(str(e.output) + '\n')
				else:
					self.create_file(args[-1], e.output)
		elif command == 'oplc':
			# Compile the OPL code at arg0, save to arg1
			e = opl.OPLCompiler()
			self.create_file(args[1], e.compile(str(self.get_file(args[0]), ENCODING)))
		elif command == 'opld':
			# Decompile the OPLC code at arg0, save to arg1
			e = opl.OPLDecompiler()
			self.create_file(args[1], bytes(e.decompile(self.get_file(args[0])), ENCODING))
		elif command == 'cname':
			# Change the OS name to arg0
			self.data['name'] = args[0]
			self.data_to_binary(self.data)
		elif command == 'cpass':
			# Change the OS password to arg0
			self.data['password_hash'] = hashlib.md5(bytes(args[0], ENCODING)).digest()
			self.data_to_binary(self.data)
		elif command == 'ropl':
			# Reload the OPL language
			import importlib
			opl = importlib.reload(opl)
		elif command == 'vopl':
			# Get the OPL version
			write(opl.__version__ + '\n')
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
		elif command == 'help':
			# Returns all commands and their descriptions
			write('''exit -> exit the os
ldir -> list the directory
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
help -> display this message
''')
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
		new_data += hashlib.md5(bytes(password, ENCODING)).digest()
		new_data += bytes(64)
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
		password_hash = data[4 + len_name : 4 + len_name + 16]
		# Get files
		i = 4 + len_name + 16
		files = {}
		while i < len(data) - 64:
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
		# Get shared buffer (64 bytes)
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

