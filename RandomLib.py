from opl.opl import BaseModule
import dill

"""Random Number Generation for OPL"""

class RandomLib(BaseModule):

	"""Random Number Generation for OPL"""

	def __init__(self):

		"""Random Number Generation for OPL"""

		self.defined_opcodes = [200, 201]
		self.random = __import__('random')
		self.struct = __import__('struct')

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Get a random float in range (0, 1] and save to arg0
			runtime.memory[int.from_bytes(line_args[0], byteorder='big')] = self.struct.pack('f', self.random.random())
		elif cmd_name == 201:
			# Choose a random byte and save it to arg0
			byte = self.random.choice([b'\x00', b'\x01'])
			runtime.memory[int.from_bytes(line_args[0], byteorder='big')] = byte

# Create the .lib file
f = open('RandomLib.lib', 'wb')
dill.dump(RandomLib, f)
f.close()
