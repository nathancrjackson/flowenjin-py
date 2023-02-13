import platform # For OS detection
import json # For reading our JSON config file
import time # For sleep

from optree import OpTree
from flowthread import FlowThread

class FlowEnjin:

	config_file = ""
	optrees = {}
	threads = []

	def __init__(self, config_file):
		print("Initialising FlowEnjin")
		
		#Get config file path
		self.config_file = config_file
		
		print("Config filename: %s" % self.config_file)
		
		#Load in config file data
		json_file = open(self.config_file, 'r')
		json_text = json_file.read()
		json_file.close()

		#Create object from config file
		json_obj = json.loads(json_text)

		#Detect the current OS and store it in config object
		system = platform.system().lower()
		if system.startswith('linux'):
			json_obj['ostype'] = 'linux'
		elif system.startswith('darwin'):
			json_obj['ostype'] = 'mac'
		elif system.startswith('windows'):
			json_obj['ostype'] = 'windows'
		print("Detected OS: %s" % json_obj['ostype'])
		
		#Load our optrees from the config object
		if 'optrees' in json_obj:
			for id in json_obj['optrees'].keys():
				enabled = True
				if 'disabled' in json_obj['optrees'][id]:
					if json_obj['optrees'][id]['disabled']:
						enabled = False
						print("Skipping disabled OpTree: %s" % json_obj['optrees'][id]['description'])

				if enabled:
					self.optrees[id] = OpTree(id, json_obj)
					thread = FlowThread(self.optrees[id], json_obj['ostype'])
					print("Starting running OpTree: %s" % self.optrees[id].description)
					thread.start()
					self.threads.append(thread)

		# Wait for kill signal
		print("Threads are running")
		loop = (True in [thread.is_alive() for thread in self.threads])
		try:
			while loop:
				time.sleep(1)
				loop = (True in [thread.is_alive() for thread in self.threads])
		except KeyboardInterrupt:
			for thread in self.threads:
				thread.stop()
			
		print("Threads stopped")