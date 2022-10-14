"""Screen Buffer for the OPL language. Written by Kevin Chen."""


# Imports
import importlib
import numpy as np
import threading


"""Screen buffer for OPL OS.
   Args: size -> tuple containing size of the screen buffer
   	     runtime -> the runtime this buffer is ran in"""

class ScreenBuffer:

	"""Screen buffer for OPL OS.
   Args: size -> tuple containing size of the screen buffer
   	     runtime -> the runtime this buffer is ran in"""

	def __init__(self, size, runtime):

		"""Screen buffer for OPL OS.
	   Args: size -> tuple containing size of the screen buffer
	   	     runtime -> the runtime this buffer is ran in"""

		self.size = (int(size[0]), int(size[1]))
		self.runtime = runtime
		self.allow_close = False
		# Get our pygame
		self.pygame = importlib.import_module('pygame')
		# Create the buffer
		self.buffer = np.zeros((int(size[0]), int(size[1]), 3))

	"""Set the window name.
	   Args: name -> new name of the window"""

	def set_name(self, name):

		"""Set the window name.
	   Args: name -> new name of the window"""

		self.pygame.display.set_caption(name)

	"""Set screen buffer.
	   Args: buffer -> the new buffer for the window"""

	def set_buffer(self, buffer):

		"""Set screen buffer.
	   Args: buffer -> the new buffer for the window"""

		self.buffer = np.array(buffer)

	"""Set one pixel in the screen buffer.
	   Args: pixel -> the pixel position to modify
	         color -> the new color of the pixel"""

	def set_pixel(self, pixel, color):

		"""Set one pixel in the screen buffer.
	   Args: pixel -> the pixel position to modify
	         color -> the new color of the pixel"""

		self.buffer[int(pixel[0])][int(pixel[1])] = np.array(color)

	def _start(self):
		# Initialize pygame
		self.pygame.init()
		self.pygame.display.set_caption('')
		# Create the screen
		self.screen = self.pygame.display.set_mode(self.size)
		# Start the main loop
		self.running = True
		while self.running:
			# Render the buffer
			surface = self.pygame.surfarray.make_surface(self.buffer)
			self.screen.blit(surface, (0, 0))
			self.pygame.display.flip()
			# Get all events
			events = self.pygame.event.get()
			for event in events:
				if event.type == self.pygame.QUIT:
					# Quit
					if self.allow_close:
						self.running = False
				elif event.type == self.pygame.MOUSEBUTTONUP:
					# Mouse Up
					self._handle_up()
				elif event.type == self.pygame.MOUSEBUTTONDOWN:
					# Mouse Down
					self._handle_down()
		self.pygame.quit()

	def _handle_up(self):
		if hasattr(self, 'mouse_state_mem_add'):
			self.runtime.memory[self.mouse_state_mem_add] = b'\x00'

	def _handle_down(self):
		if hasattr(self, 'mouse_state_mem_add'):
			self.runtime.memory[self.mouse_state_mem_add] = b'\x01'

	"""Start the window"""

	def start(self):

		"""Start the window"""

		# Create a new thread with our starting function
		t = threading.Thread(target=self._start)
		# Start the thread
		t.start()

	"""Stop the window"""

	def stop(self):

		"""Stop the window"""

		self.running = False

