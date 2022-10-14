"""File Buffer for the OPL OS. Written by Kevin Chen."""


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

