from opl.opl import BaseModule
import dill

"""Sockets for OPL"""

class SocketLib(BaseModule):

	"""Sockets for OPL"""

	def __init__(self):

		"""Sockets for OPL"""

		self.defined_opcodes = list(range(200, 210))
		self.socket = __import__('socket')
		self.sockets = {}
		self.connections = {}

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Create a socket designated arg0
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			self.sockets[socket_num] = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
		elif cmd_name == 201:
			# Connect socket arg0 to address arg1 and port arg2
			address = (str(runtime.memory[int.from_bytes(line_args[1], byteorder='big')], self.ENCODING), int.from_bytes(runtime.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big'))
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			self.sockets[socket_num].connect(address)
		elif cmd_name == 202:
			# Bind socket arg0 to address arg1 and port arg2
			address = (str(runtime.memory[int.from_bytes(line_args[1], byteorder='big')], self.ENCODING), int.from_bytes(runtime.memory[int.from_bytes(line_args[2], byteorder='big')], byteorder='big'))
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			self.sockets[socket_num].bind(address)
		elif cmd_name == 203:
			# Accept a connection from arg0 and save to connection arg1 and address to arg2 arg3
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			connection, address = self.sockets[socket_num].accept()
			conn_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
			self.connections[conn_num] = connection
			runtime.memory[int.from_bytes(line_args[2], byteorder='big')] = bytes(address[0], self.ENCODING)
			runtime.memory[int.from_bytes(line_args[3], byteorder='big')] = int.to_bytes(address[1], 4, byteorder='big')
		elif cmd_name == 204:
			# Recieve arg1 bytes from connection arg0 and save to arg2
			conn_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			num_bytes = int.from_bytes(runtime.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
			data = self.connections[conn_num].recv(num_bytes)
			runtime.memory[int.from_bytes(line_args[2], byteorder='big')] = data
		elif cmd_name == 205:
			# Send arg1 to connection arg0
			conn_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			data = runtime.memory[int.from_bytes(line_args[1], byteorder='big')]
			self.connections[conn_num].sendall(data)
		elif cmd_name == 206:
			# Close connection arg0
			conn_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			self.connections[conn_num].close()
		elif cmd_name == 207:
			# Send arg1 to socket arg0
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			data = runtime.memory[int.from_bytes(line_args[1], byteorder='big')]
			self.sockets[socket_num].sendall(data)
		elif cmd_name == 208:
			# Recieve arg1 bytes from socket arg0 and save to arg2
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			num_bytes = int.from_bytes(runtime.memory[int.from_bytes(line_args[1], byteorder='big')], byteorder='big')
			data = self.sockets[socket_num].recv(num_bytes)
			runtime.memory[int.from_bytes(line_args[2], byteorder='big')] = data
		elif cmd_name == 209:
			# Close socket arg0
			socket_num = int.from_bytes(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], byteorder='big')
			self.sockets[socket_num].close()


# Create the .lib file
f = open('SocketLib.lib', 'wb')
dill.dump(SocketLib, f)
f.close()
