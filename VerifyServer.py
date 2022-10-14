"""Server for OPE Verification"""

import serverprocessor
import time
import socket
import uuid



def worker():
	# Iterate through requests
	while True:
		if requests:
			try:
				# Handle the first item in requests
				current_request_key = list(requests.keys())[0]
				current_request = requests.pop(current_request_key)
				if current_request[0] == 'verify':

				outputs[current_request_key] = current_request[0] + current_request[1]
			except Exception as e:
				# Print the error, add error
				print(time.asctime() + ' ERROR: ' + str(e))
				outputs[current_request_key] = time.asctime() + ' ERROR: ' + str(e)
		else:
			pass

ready = True
requests = {}
outputs = {}

def handler(commandtype, ope):
	this_key = uuid.uuid1()
	requests[this_key] = (commandtype, ope)
	while not (this_key in outputs.keys()):
		pass
	# Now we got a result
	return outputs.pop(this_key)


h = serverprocessor.Processor(handler, socket.gethostbyname(socket.gethostname()), 20000)
time.sleep(0.1)
h.begin_server()
time.sleep(0.1)
while True:
	worker()
