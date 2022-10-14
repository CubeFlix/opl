from opl.opl import BaseModule
import dill


class WGETModule(BaseModule):

	def __init__(self):

		self.defined_opcodes = [200]

		self.requests = __import__('requests')

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# wget arg0 save to arg1
			content = self.requests.get(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING)).content
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = content


# Create the .lib file
f = open('WGETLIB.lib', 'wb')
dill.dump(WGETModule, f)
f.close()
