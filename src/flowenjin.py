import platform # For OS detection
import json # For reading our JSON config file
import time # For sleep
import datetime # For unix time

import pycron # For cron style functionality

from singlemode import SingleThreadMode
from optree import OpTree
from flowthread import FlowThread
from flowhandlers import IntervalFlowHandler

class FlowEnjin:

	config_file = ""
	threads = []
	thread_model = "single"
	thread_count = 1
	thread_skip = 0

	def __init__(self, config_file):
		print("---")
		print("Initialising FlowEnjin")
		print("---")
		print("")

		# Get config file path
		self.config_file = config_file

		print("Config filename: %s" % self.config_file)

		# Load in config file data
		json_file = open(self.config_file, 'r')
		json_text = json_file.read()
		json_file.close()

		# Create object from config file
		json_obj = json.loads(json_text)
		
		# Load our settings
		if 'settings' in json_obj:
			if 'threadmodel' in json_obj['settings']:
				# Load our thread mode
				if json_obj['settings']['threadmodel'] == "fixed":
					self.thread_model = "fixed"
				elif json_obj['settings']['threadmodel'] == "dynamic":
					self.thread_model = "dynamic"
				else:
					print("Invalid thread mode in settings")

				# If thread mode is set then look at the other settings
				if 'threadcount' in json_obj['settings']:
					if isinstance(json_obj['settings']['threadcount'], int):
						if json_obj['settings']['threadcount'] > 1:
							self.thread_count = json_obj['settings']['threadcount']
					else:
						print("Thread count must be integer")
				if 'threadskip' in json_obj['settings']:
					if isinstance(json_obj['settings']['threadskip'], int):
						if json_obj['settings']['threadskip'] > 0:
							self.thread_skip = json_obj['settings']['threadskip']
					else:
						print("Thread skip must be integer")

		if self.thread_model == "single":
			print("Thread mode is: single")	
		else:
			print("Thread mode is: %s (count of %s, skipping %s)"  % (self.thread_model, self.thread_count, self.thread_skip))		

		# Detect the current OS and store it in config object
		system = platform.system().lower()
		if system.startswith('linux'):
			json_obj['ostype'] = 'linux'
		elif system.startswith('darwin'):
			json_obj['ostype'] = 'mac'
		elif system.startswith('windows'):
			json_obj['ostype'] = 'windows'
		print("Detected OS: %s" % json_obj['ostype'])
		print("")
		
		# If in single thread mode execution is straight forward
		if self.thread_model == "single":
			print("Preparing single-threaded FlowEnjin")
			thread = SingleThreadMode(json_obj['ostype'])

			# Load our optrees into our single thread
			if 'optrees' in json_obj:
				for id in json_obj['optrees'].keys():
					enabled = True
					if 'disabled' in json_obj['optrees'][id]:
						if json_obj['optrees'][id]['disabled']:
							enabled = False
							print("Skipping disabled OpTree: %s" % json_obj['optrees'][id]['description'])

					if enabled:
						optree = OpTree(id, json_obj)
						print("Creating OpTree: %s" % optree.description)
						thread.append(optree)

			if thread.count() > 0:
				print("Loaded %s OpTree(s)" % thread.count())
				print("")
				print("Running FlowEnjin")
				thread.run()
			else:
				print("No OpTrees to run")
				print("")
				print("Stopping FlowEnjin")
		else:
			print("Preparing multi-threaded FlowEnjin")

		'''
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
		'''
		print("")
		print("Exiting FlowEnjin")