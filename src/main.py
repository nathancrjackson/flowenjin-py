#!/usr/bin/python

import platform # For OS detection
import json # For reading our JSON config file
import time # For sleep
import datetime # For unix time
import copy # For copying objects

from taskagent import TaskAgent
from task import Task
from singlemode import SingleThreadMode
from threadedmode import MultiThreadedMode

class App:

	def __init__(self, config_file):
		print("---")
		print("Initialising TaskEnjin app")
		print("---")
		print("")

		# Detect our OS
		self.detectOS()

		# Initialise some variables
		self.thread_model = "single"
		self.thread_count = 1
		self.thread_skip = 0

		# Load our config file name
		print("Config filename: %s" % config_file)
		self.config_file = config_file

		#Prep some things we're going to load from our config file
		self.datasets = {}
		self.variables = {}
		self.routines = {}
		self.tasks = {}

	def main(self):
		# Start with our config
		self.loadConfig()

		# If in single thread mode execution is straight forward
		if self.thread_model == "single":
			print("Preparing single-threaded TaskEnjin")
			thread = SingleThreadMode()

			# Load our tasks into our single thread
			for id in self.tasks.keys():
				enabled = True
				if 'disabled' in self.tasks[id]:
					if self.tasks[id]['disabled']:
						enabled = False
						print("Skipping disabled task: %s" % self.tasks[id]['description'])

				if enabled:

					if 'foreachdataset' in self.tasks[id]:
						print("Creating tasks: %s using dataset %s" % (self.tasks[id]['description'], self.tasks[id]['foreachdataset']))
						datasetid = self.tasks[id]['foreachdataset']
						if datasetid in self.datasets:

							for key in self.datasets[datasetid]:
								print("Creating task for key: %s" % key)

								task_obj = copy.deepcopy(self.tasks[id])
								task_obj['description'] = task_obj['description'] + ": " + key

								if 'variables' not in task_obj:
									task_obj['variables'] = {}

								task_obj['variables']['datasetkey'] = key
								task_obj['variables']['datasetvalue'] = self.datasets[datasetid][key]

								task = Task(id, task_obj, self.datasets, self.variables, self.routines)
								thread.append(task)

						else:
							print("Dataset does not exist")

					else:
						task = Task(id, self.tasks[id], self.datasets, self.variables, self.routines)
						print("Creating Task: %s" % task.description)
						thread.append(task)

			if thread.count() > 0:
				print("Loaded %s task(s)" % thread.count())
				print("")
				print("Running TaskEnjin")
				thread.start()
			else:
				print("No tasks to run")

		elif self.thread_model == "fixed" or self.thread_model == "dynamic":
			print("Preparing multi-threaded TaskEnjin")

			# Initialise our thread list and task counter
			threads = []
			task_counter = 0
			self.thread_counter = 0

			if self.thread_model == "fixed":
				# Create our fixed amount of threads
				threads = []
				for i in range(self.thread_count):
					threads.append(MultiThreadedMode(i))
				self.thread_counter = self.thread_count

				# Prep our variables for tracking which thread we're dropping tasks into
				count = 0
				minimum = self.thread_skip
				maximum = self.thread_count
				num = minimum
				maximum = maximum - minimum

				# Load our tasks into our threads
				if self.thread_skip >= self.thread_count:
					print("Cannot set skip value >= count value in fixed mode")
				else:
					for id in self.tasks.keys():
						enabled = True
						if 'disabled' in self.tasks[id]:
							if self.tasks[id]['disabled']:
								enabled = False
								print("Skipping disabled task: %s" % self.tasks[id]['description'])

						if enabled:
							# If it uses a dataset
							if 'foreachdataset' in self.tasks[id]:
								print("Creating tasks: %s using dataset %s" % (self.tasks[id]['description'], self.tasks[id]['foreachdataset']))
								datasetid = self.tasks[id]['foreachdataset']
								# If the dataset exists
								if datasetid in self.datasets:
									# For each item in the dataset
									for key in self.datasets[datasetid]:

										print("Creating task for key: %s (in thread %s)" % (key, num))

										task_obj = copy.deepcopy(self.tasks[id])
										task_obj['description'] = task_obj['description'] + ": " + key

										if 'variables' not in task_obj:
											task_obj['variables'] = {}

										task_obj['variables']['datasetkey'] = key
										task_obj['variables']['datasetvalue'] = self.datasets[datasetid][key]

										task = Task(id, task_obj, self.datasets, self.variables, self.routines)
										task_counter = task_counter + 1
										print("Creating task: %s (in thread %s)" % (task.description, num))
										# Add to thread
										print(threads[num].thread_id)
										(threads[num]).append(task)
										# Move onto next thread
										count = (count + 1) % maximum
										num = count + minimum
								else:
									print("Dataset does not exist")

							# If no dataset involved
							else:
								task = Task(id, self.tasks[id], self.datasets, self.variables, self.routines)
								task_counter = task_counter + 1
								print("Creating task: %s (in thread %s)" % (task.description, num))
								# Add to thread
								(threads[num]).append(task)
								# Move onto next thread
								count = (count + 1) % maximum
								num = count + minimum
	

			elif self.thread_model == "dynamic":
				# Create our threads we're going to skip
				threads = [MultiThreadedMode(i) for i in range(self.thread_skip)]
				self.thread_counter = self.thread_skip

				# Prep our first thread
				thread = MultiThreadedMode(self.thread_counter)
				self.thread_counter = self.thread_counter + 1

				# Track our number of threads while at it
				num = self.thread_skip

				# Load our tasks into our threads
				for id in self.tasks.keys():
					enabled = True
					if 'disabled' in self.tasks[id]:
						if self.tasks[id]['disabled']:
							enabled = False
							print("Skipping disabled task: %s" % self.tasks[id]['description'])

					# If our task is enabled
					if enabled:
						# If it uses a dataset
						if 'foreachdataset' in self.tasks[id]:
							print("Creating tasks: %s using dataset %s" % (self.tasks[id]['description'], self.tasks[id]['foreachdataset']))
							datasetid = self.tasks[id]['foreachdataset']
							# If the dataset exists
							if datasetid in self.datasets:
								# For each item in the dataset
								for key in self.datasets[datasetid]:
									# First check if we need a new thread and create if required
									if thread.count() == self.thread_count:
										threads.append(thread)
										thread = MultiThreadedMode(self.thread_counter)
										self.thread_counter = self.thread_counter + 1
										num = num + 1

									print("Creating task for key: %s (in thread %s)" % (key, num))

									task_obj = copy.deepcopy(self.tasks[id])
									task_obj['description'] = task_obj['description'] + ": " + key

									if 'variables' not in task_obj:
										task_obj['variables'] = {}

									task_obj['variables']['datasetkey'] = key
									task_obj['variables']['datasetvalue'] = self.datasets[datasetid][key]

									task = Task(id, task_obj, self.datasets, self.variables, self.routines)
									task_counter = task_counter + 1
									thread.append(task)

							else:
								print("Dataset does not exist")

						# If no dataset involved
						else:
							if thread.count() == self.thread_count:
								threads.append(thread)
								thread = MultiThreadedMode(self.thread_counter)
								self.thread_counter = self.thread_counter + 1
								num = num + 1

							task = Task(id, self.tasks[id], self.datasets, self.variables, self.routines)
							task_counter = task_counter + 1
							print("Creating task: %s (in thread %s)" % (task.description, num))
							# Add to thread
							thread.append(task)

				# Don't forget to add our last thread into the pool
				threads.append(thread)

			# If we have threads to run then run them
			if (len(threads) > 0) and (task_counter > 0):
				print("Loaded %s task(s) into %s thread(s)" % (task_counter, self.thread_counter))
				print("")
				print("Running TaskEnjin")

				for thread in threads:
					thread.start()

				loop = (True in [thread.is_alive() for thread in threads])
				try:
					while loop:
						time.sleep(1)
						loop = (True in [thread.is_alive() for thread in threads])
				except KeyboardInterrupt:
					print("")
					print("Stopping TaskEnjin")
					for thread in threads:
						thread.stop()

				print("Threads stopped")

			else:
				print("No threads with tasks to run")


		else:
			print("Error: Thread model not recognised")

		print("Exiting TaskEnjin")

	def detectOS(self):
		# Detect the current OS and store it in config object
		system = platform.system().lower()
		if system.startswith('linux'):
			self.ostype = 'linux'
		elif system.startswith('darwin'):
			self.ostype = 'mac'
		elif system.startswith('windows'):
			self.ostype = 'windows'
			TaskAgent.ping_count_flag = 'n'
		print("Detected OS: %s" % self.ostype)
		print("")

	def loadConfig(self):
		# Load in config file data
		json_file = open(self.config_file, 'r')
		json_text = json_file.read()
		json_file.close()

		# Create object from config file
		json_obj = json.loads(json_text)

		# Load our settings
		if 'settings' in json_obj:

			# Let's first check out if we want to debug
			if 'debug' in json_obj['settings']:
				if json_obj['settings']['debug'] == True:
					TaskAgent.debug = True

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
						if json_obj['settings']['threadcount'] > 0:
							self.thread_count = json_obj['settings']['threadcount']
					else:
						print("Thread count must be integer")
				if 'threadskip' in json_obj['settings']:
					if isinstance(json_obj['settings']['threadskip'], int):
						if json_obj['settings']['threadskip'] > 0:
							self.thread_skip = json_obj['settings']['threadskip']
					else:
						print("Thread skip must be integer")

		# Share some settings
		if self.thread_model == "single":
			print("Thread mode is: single")
		else:
			print("Thread mode is: %s (count of %s, skipping %s)"  % (self.thread_model, self.thread_count, self.thread_skip))

		# Break the rest of our json_obj into more manageable chunks
		if 'datasets' in json_obj:
			self.datasets = json_obj['datasets']
		if 'variables' in json_obj:
			self.variables = json_obj['variables']
		if 'routines' in json_obj:
			self.routines = json_obj['routines']
		if 'tasks' in json_obj:
			self.tasks = json_obj['tasks']


app = App("config.json")
app.main()