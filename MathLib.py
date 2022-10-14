from opl.opl import BaseModule
import dill

"""Math library for OPL. """

class MathLib(BaseModule):

	"""Math library for OPL. """

	def __init__(self):

		"""Math library for OPL. """

		self.defined_opcodes = list(range(200, 211))
		self.math = __import__('math')
		self.struct = __import__('struct')

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Put PI into arg0
			runtime.memory[int.from_bytes(line_args[0], byteorder='big')] = self.struct.pack('f', self.math.pi)
		elif cmd_name == 201:
			# Put E into arg0
			runtime.memory[int.from_bytes(line_args[0], byteorder='big')] = self.struct.pack('f', self.math.e)
		elif cmd_name == 202:
			# Put inf into arg0
			runtime.memory[int.from_bytes(line_args[0], byteorder='big')] = self.struct.pack('f', self.math.inf)
		elif cmd_name == 203:
			# Put nan into arg0
			runtime.memory[int.from_bytes(line_args[0], byteorder='big')] = self.struct.pack('f', self.math.nan)
		elif cmd_name == 204:
			# arg1 = sin(arg0)
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = self.struct.pack('f', self.math.sin(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')])))
		elif cmd_name == 205:
			# arg1 = cos(arg0)
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = self.struct.pack('f', self.math.cos(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')])))
		elif cmd_name == 206:
			# arg1 = tan(arg0)
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = self.struct.pack('f', self.math.tan(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')])))
		elif cmd_name == 207:
			# arg1 = asin(arg0)
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = self.struct.pack('f', self.math.asin(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')])))
		elif cmd_name == 208:
			# arg1 = acos(arg0)
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = self.struct.pack('f', self.math.acos(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')])))
		elif cmd_name == 209:
			# arg1 = atan(arg0)
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = self.struct.pack('f', self.math.atan(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')])))
		elif cmd_name == 210:
			# arg2 = log(arg0, base=arg1)
			runtime.memory[int.from_bytes(line_args[2], byteorder='big')] = self.struct.pack('f', self.math.log(self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[0], byteorder='big')]), base=self.struct.unpack('f', runtime.memory[int.from_bytes(line_args[1], byteorder='big')])))



# Create the .lib file
f = open('MathLib.lib', 'wb')
dill.dump(MathLib, f)
f.close()
