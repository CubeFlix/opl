from opl.opl import BaseModule
import dill


class rscf(BaseModule):


	def __init__(self):


		self.defined_opcodes = [200]
		self.struct = __import__('struct')

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# parse
			s = self.split_code(str(runtime.memory[int.from_bytes(line_args[0], 'big')], self.ENCODNG))
			news = []
			for line in s:
				line = ['2'] + [line[0]] + ['i' + line[1]]
				news.append(line)
			code_split = self.remove_leading_spaces(news)
			# Iterate over all lines
			line_num = 0
			for line_code in code_split:
				if line_code == []:
					# We got a newline, ignore
					continue
				elif len(line_code[0]) >= 2 and line_code[0][0 : 2] == '//':
					# Comment line, ignore
					continue
				try:
					# Add line number, command type, and number of args to code
					compiled_code += int.to_bytes(line_num, 4, byteorder='big') + int.to_bytes(int(line_code[0]), 4, byteorder='big') + int.to_bytes(len(line_code) - 1, 4, byteorder='big')
					# Add each argument
					for arg in line_code[1 : ]:
						# Get data type
						dtype = arg[0]
						arg = arg[1 : ]
						if dtype == 'i':
							# Int
							arg = int.to_bytes(int(arg), 4, byteorder='big')
						elif dtype == 'f':
							# Float
							arg = self.struct.pack('f', float(arg))
						elif dtype == 's':
							# String
							arg = bytes(arg, ENCODING)
						elif dtype == 'b':
							# Byte numbers (a,b,c,d,etc.)
							if arg.split(',') == ['']:
								# No bytes
								arg = bytes(0)
							else:
								arg = bytes([int(i) for i in arg.split(',')])
						elif dtype == 'g':
							# Signed int
							arg = int.to_bytes(int(arg), 4, byteorder='big', signed=True)
						compiled_code += int.to_bytes(len(arg), 4, byteorder='big') + arg
					line_num += 1
				except Exception as e:
					self.write('ERROR: ' + str(e) + ' LINE: ' + str(line_num) + ' CODE: ' + str(line_code) + '\n')
					break
			runtime.memory[int.from_bytes(line_args[1], 'big')] = compiled_code

# Create the .lib file
f = open('rscf.lib', 'wb')
dill.dump(rscf, f)
f.close()
