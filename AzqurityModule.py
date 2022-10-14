from opl.opl import BaseModule
import dill

"""Azqurity Sequrity"""

class AzqurityLib(BaseModule):

	"""Azqurity Sequrity"""

	def __init__(self):

		"""Azqurity Sequrity"""

		self.defined_opcodes = [200, 201, 202]
		self._level_1 = [101, 104, 117]
		self._level_2 = [55, 82, 109, 111, 118]
		self._level_3 = [47, 48, 97, 102, 106]

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Scan the OPC file at arg0 and save it to arg1
			filedata = runtime.memory[int.from_bytes(line_args[0], byteorder='big')]
			split_code, _ = self.OPLExecutor.split_code(None, filedata)
			# Look for illegal opcodes
			danger_level = 0
			for command in split_code:
				opcode = int.from_bytes(command[1], byteorder='big')
				if opcode in self._level_1:
					# Level 1 danger threat
					if danger_level >= 1:
						pass
					else:
						danger_level = 1
				elif opcode in self._level_2:
					# Level 2 danger threat
					if danger_level >= 2:
						pass
					else:
						danger_level = 2
				elif opcode in self._level_3:
					# Level 3 danger threat
					if danger_level >= 3:
						pass
					else:
						danger_level = 3
			# Save the danger level
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes([danger_level])
		elif cmd_name == 201:
			# Scan the OPL file at arg0 and save it to arg1
			filedata = str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING)
			split_code, _ = self.OPLExecutor.split_code(None, self.OPLCompiler().compile(filedata))
			# Look for illegal opcodes
			danger_level = 0
			for command in split_code:
				opcode = int.from_bytes(command[1], byteorder='big')
				if opcode in self._level_1:
					# Level 1 danger threat
					if danger_level >= 1:
						pass
					else:
						danger_level = 1
				elif opcode in self._level_2:
					# Level 2 danger threat
					if danger_level >= 2:
						pass
					else:
						danger_level = 2
				elif opcode in self._level_3:
					# Level 3 danger threat
					if danger_level >= 3:
						pass
					else:
						danger_level = 3
			# Save the danger level
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes([danger_level])
		elif cmd_name == 202:
			# Scan the OPE file arg0 and save it to arg1
			filedata = runtime.memory[int.from_bytes(line_args[0], byteorder='big')]
			maincode = filedata[4 : 4 + int.from_bytes(filedata[ : 4], byteorder='big')]
			split_code, _ = self.OPLExecutor.split_code(None, maincode)
			# Look for illegal opcodes
			danger_level = 0
			for command in split_code:
				opcode = int.from_bytes(command[1], byteorder='big')
				if opcode in self._level_1:
					# Level 1 danger threat
					if danger_level >= 1:
						pass
					else:
						danger_level = 1
				elif opcode in self._level_2:
					# Level 2 danger threat
					if danger_level >= 2:
						pass
					else:
						danger_level = 2
				elif opcode in self._level_3:
					# Level 3 danger threat
					if danger_level >= 3:
						pass
					else:
						danger_level = 3
			# Save the danger level
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes([danger_level])



# Create the .lib file
f = open('AzqurityLib.lib', 'wb')
dill.dump(AzqurityLib, f)
f.close()
