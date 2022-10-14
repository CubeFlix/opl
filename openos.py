from opl.oplos import OPLOS
import sys

if __name__ == '__main__':
	args = sys.argv[1 : ]
	if len(args) == 1:
		# Open system arg0
		os = OPLOS(args[0])
		os.start()
	elif len(args) == 2:
		if args[1] == '-f':
			# Open and format arg0 (Name: OPLOS Password: password)
			os = OPLOS(args[0])
			os.format('OPLOS', 'password')
			os.start()
	else:
		print('OPL OS OPENER')
		print('Help: openos <filename> -> opens OPL OS filename and starts it')
		print('      openos <filename> -f -> opens OPL OS filename, and formats it with name OPLOS and password \'password\'')
