from opl.opl import BaseModule
import dill

"""Wikipedia Getter"""

class WikipediaLib(BaseModule):

	"""Wikipedia Getter"""

	def __init__(self):

		"""Wikipedia Getter"""

		self.defined_opcodes = [200]

		self.requests = __import__('requests')
		self.bs4 = __import__('bs4')

	def handle_command(self, runtime, cmd_name, line_args):
		if cmd_name == 200:
			# Download wikipedia article arg0 and save to arg1
			content = self.requests.get('https://en.wikipedia.org/w/index.php?title=' + str(runtime.memory[int.from_bytes(line_args[0], byteorder='big')], self.ENCODING) + '&action=edit').content
			output = self.bs4.BeautifulSoup(content)('textarea')[0].text
			runtime.memory[int.from_bytes(line_args[1], byteorder='big')] = bytes(output, self.ENCODING)

# Create the .lib file
f = open('WikipediaLib.lib', 'wb')
dill.dump(WikipediaLib, f)
f.close()
