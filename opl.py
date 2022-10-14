from main import *
import sys

if __name__ == '__main__':
	args = sys.argv[1 : ]
	if len(args) == 1:
		# Execute binary
		f = open(args[0], 'rb')
		c = f.read()
		f.close()
		e = OPLExecutor()
		print(e.execute(c))
	elif len(args) >= 2:
		if args[1] == '-e':
			# Execute binary with args
			f = open(args[0], 'rb')
			c = f.read()
			f.close()
			e = OPLExecutor()
			print(e.execute(c, args[2 : ]))
		elif args[1] == '-c':
			# Compile code
			f = open(args[0], 'r')
			c = f.read()
			f.close()
			e = OPLCompiler()
			c = e.compile(c)
			f = open(args[0] + '.opc', 'wb')
			f.write(c)
			f.close()
		elif args[1] == '-d':
			# Decompile code
			f = open(args[0], 'rb')
			c = f.read()
			f.close()
			e = OPLDecompiler()
			c = e.decompile(c)
			f = open(args[0] + '.opl', 'w')
			f.write(c)
			f.close()
		elif args[1] == '-h':
			print('OPL: arg1, optional arg2')
			print('arg1 -> file')
			print('arg2 -> flag (-e execute, -c compile, -h help, -d decompile)')
	else:
		print('OPL: arg1, optional arg2')
		print('arg1 -> file')
		print('arg2 -> flag (-e execute, -c compile, -h help)')
