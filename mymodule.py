from opl.opl import BaseModule
import dill

class MyModule(BaseModule):
	def __init__(self):
		self.defined_opcodes = [200]
	def on_begin_opcode(self, runtime, cmd_name, line_args):
		pass

	def on_end_opcode(self, runtime, cmd_name, line_args):
		pass
	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			runtime.memory[1] = line_args[0]
			self.write(str(line_args[0], self.ENCODING))

class runtime:
	def __init__(self):
		self.memory = {}
m = MyModule()
m.init_functions()
m.handle_command(runtime(), 200, [b'abc'])

dill.dump(MyModule, open('MyModule.lib', 'wb'))