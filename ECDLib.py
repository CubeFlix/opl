from opl.opl import BaseModule
import dill

"""An Execution, Decompilation, and Compilation library for OPL. (OEP 016)"""

class EDCLib(BaseModule):

	"""An Execution, Decompilation, and Compilation library for OPL. (OEP 016)"""

	def __init__(self):

		"""An Execution, Decompilation, and Compilation library for OPL. (OEP 016)"""

		self.defined_opcodes = [200, 201, 202]

	def on_begin_opcode(self, runtime, cmd_name, line_args):
		pass

	def on_end_opcode(self, runtime, cmd_name, line_args):
		pass

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Executes arg0, saves output buffer to arg1
			new_runtime = self.OPLExecutor()
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = new_runtime.execute(runtime.memory[int.from_bytes(line_args[0], byteorder='big')])
			del new_runtime
		elif cmd_name == 201:
			# Decompile arg0, save string to arg1
			new_runtime = self.OPLDecompiler()
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(new_runtime.decompile(runtime.memory[int.from_bytes(line_args[0], byteorder='big')]), self.ENCODING)
			del new_runtime
		elif cmd_name == 202:
			# Compile arg0, save bytecode to arg1
			new_runtime = self.OPLCompiler()
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = new_runtime.compile(str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING))
			del new_runtime


# Create the .lib file
f = open('EDCLib.lib', 'wb')
dill.dump(EDCLib, f)
f.close()
