from opl.opl import BaseModule
import dill

"""OEP 020 library for OPL. """

class OEP20Lib(BaseModule):

	"""OEP 020 library for OPL. """

	def __init__(self):

		"""OEP 020 library for OPL. """

		self.defined_opcodes = [200, 201, 202, 203]

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Take args 1 - end, use OEP 020, and save to arg0 (Uses direct string names as args)
			filenames = [str(i, self.ENCODING) for i in line_args[1 : ]]
			new_filename = str(line_args[0], self.ENCODING)
			if runtime.oplos == None:
				# Use the standard file protocol
				files = {}
				for filename in filenames:
					f = open(filename, 'rb')
					files[filename] = f.read()
					f.close()
				new_data = self.TO_OEP_20(files)
				f = open(new_filename, 'wb')
				f.write(new_data)
				f.close()
			else:
				# Use the OPL OS file protocol
				files = {}
				for filename in filenames:
					files[filename] = runtime.oplos.get_file(filename)
				new_data = self.TO_OEP_20(files)
				runtime.oplos.create_file(new_filename, new_data)	
		elif cmd_name == 201:
			# Take arg0 and expand it to the filesystem using OEP 020 (Uses direct string name as arg)
			if runtime.oplos == None:
				# Use the standard file protocol
				f = open(str(line_args[0], self.ENCODING), 'rb')
				files = self.FROM_OEP_20(f.read())
				f.close()
				for filename in files:
					f = open(filename, 'wb')
					f.write(files[filename])
					f.close()
			else:
				# Use the OPL OS file protocol
				files = self.FROM_OEP_20(runtime.oplos.get_file(str(line_args[0], self.ENCODING)))
				for filename in files:
					runtime.oplos.write_file(filename, files[filename])
		elif cmd_name == 202:
			# Take args 1 - end, use OEP 020, and save to arg0
			filenames = [str(runtime.memory[int.from_bytes(i, byteorder='big')], self.ENCODING) for i in line_args[1 : ]]
			new_filename = str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING)
			if runtime.oplos == None:
				# Use the standard file protocol
				files = {}
				for filename in filenames:
					f = open(filename, 'rb')
					files[filename] = f.read()
					f.close()
				new_data = self.TO_OEP_20(files)
				f = open(new_filename, 'wb')
				f.write(new_data)
				f.close()
			else:
				# Use the OPL OS file protocol
				files = {}
				for filename in filenames:
					files[filename] = runtime.oplos.get_file(filename)
				new_data = self.TO_OEP_20(files)
				runtime.oplos.create_file(new_filename, new_data)	
		elif cmd_name == 203:
			# Take arg0 and expand it to the filesystem using OEP 020
			if runtime.oplos == None:
				# Use the standard file protocol
				f = open(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING), 'rb')
				files = self.FROM_OEP_20(f.read())
				f.close()
				for filename in files:
					f = open(filename, 'wb')
					f.write(files[filename])
					f.close()
			else:
				# Use the OPL OS file protocol
				files = self.FROM_OEP_20(runtime.oplos.get_file(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING)))
				for filename in files:
					runtime.oplos.write_file(filename, files[filename])

# Create the .lib file
f = open('OEP20Lib.lib', 'wb')
dill.dump(OEP20Lib, f)
f.close()
