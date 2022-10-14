from opl.opl import BaseModule
import dill


class soslb(BaseModule):

	def __init__(self):

		self.defined_opcodes = [200, 201, 202, 203]
		self.os = __import__('os')

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			file_buffer = open(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING), 'rb')
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = file_buffer.read()
			file_buffer.close()
		elif cmd_name == 201:
			file_buffer = open(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING), 'wb')
			file_buffer.write(runtime.memory[int.from_bytes(line_args[1], byteorder='big')])
			file_buffer.close()
		elif cmd_name == 202:
			self.os.remove(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING))
		elif cmd_name == 203:
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes([self.os.system(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING))])


# Create the .lib file
f = open('soslb.lib', 'wb')
dill.dump(soslb, f)
f.close()
