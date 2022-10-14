"""Creates documentation for each OPL command."""

# Get the file data
f = open('opl/executor.py')
filedata = f.read()
f.close()

documentation = \
'''OPL OPCODE DOCUMENTATION
------------------------

'''

# Iterate over each line in the file
command_num = 0
split_filedata = filedata.split('\n')
for line_num, line in enumerate(filedata.split('\n')):
	# Check if the line is a command line
	if ('elif cmd_name == ' in line) or ('if cmd_name == ' in line):
		# We got a line which starts a new command
		# Gather the next line, which contains the command documentation
		doc_line = split_filedata[line_num + 1][7 : ] + '.'
		# Get all the args the command takes
		if 'arg5' in doc_line:
			# We have 6 args
			num_args = 6
		elif 'arg4' in doc_line:
			# We have 5 args
			num_args = 5
		elif 'arg3' in doc_line:
			# We have 4 args
			num_args = 4
		elif 'arg2' in doc_line:
			# We have 3 args
			num_args = 3
		elif 'arg1' in doc_line:
			# We have 2 args
			num_args = 2
		elif 'arg0' in doc_line:
			# We have 1 arg
			num_args = 1
		else:
			# This command takes no args
			num_args = 0
		# Create the documentation line
		final_line = 'OPCODE ' + str(command_num)
		# Add the args
		final_line += ' ' + ' '.join(['arg' + str(i) for i in range(num_args)])
		# Add the documentation
		final_line += '\n' + doc_line + '\n\n'
		# Add the line to the final documentation
		documentation += final_line
		# Add 1 to the current OPCODE number
		command_num += 1

f = open('OPCODEDOCUMENTATION.txt', 'w')
f.write(documentation)
f.close()
