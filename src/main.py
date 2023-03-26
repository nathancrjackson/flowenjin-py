#!/usr/bin/python

import platform # For OS detection
import json # For reading our JSON config file
import time # For sleep
import datetime # For unix time

from taskagent import TaskAgent
from task import Task
from singlemode import SingleThreadMode
from threadedmode import MultiThreadedMode


print("---")
print("Initialising TaskEnjin")
print("---")
print("")

# Initialise some variables
thread_model = "single"
thread_count = 1
thread_skip = 0

# Get config file path
config_file = "config.json"

print("Config filename: %s" % config_file)

# Load in config file data
json_file = open(config_file, 'r')
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
			thread_model = "fixed"
		elif json_obj['settings']['threadmodel'] == "dynamic":
			thread_model = "dynamic"
		else:
			print("Invalid thread mode in settings")

		# If thread mode is set then look at the other settings
		if 'threadcount' in json_obj['settings']:
			if isinstance(json_obj['settings']['threadcount'], int):
				if json_obj['settings']['threadcount'] > 0:
					thread_count = json_obj['settings']['threadcount']
			else:
				print("Thread count must be integer")
		if 'threadskip' in json_obj['settings']:
			if isinstance(json_obj['settings']['threadskip'], int):
				if json_obj['settings']['threadskip'] > 0:
					thread_skip = json_obj['settings']['threadskip']
			else:
				print("Thread skip must be integer")

if thread_model == "single":
	print("Thread mode is: single")	
else:
	print("Thread mode is: %s (count of %s, skipping %s)"  % (thread_model, thread_count, thread_skip))		

# Detect the current OS and store it in config object
system = platform.system().lower()
if system.startswith('linux'):
	json_obj['ostype'] = 'linux'
elif system.startswith('darwin'):
	json_obj['ostype'] = 'mac'
elif system.startswith('windows'):
	json_obj['ostype'] = 'windows'
	TaskAgent.ping_count_flag = 'n'
print("Detected OS: %s" % json_obj['ostype'])
print("")

# If in single thread mode execution is straight forward
if thread_model == "single":
	print("Preparing single-threaded TaskEnjin")
	thread = SingleThreadMode()

	# Load our tasks into our single thread
	if 'tasks' in json_obj:
		for id in json_obj['tasks'].keys():
			enabled = True
			if 'disabled' in json_obj['tasks'][id]:
				if json_obj['tasks'][id]['disabled']:
					enabled = False
					print("Skipping disabled task: %s" % json_obj['tasks'][id]['description'])

			if enabled:
				task = Task(id, json_obj)
				print("Creating Task: %s" % task.description)
				thread.append(task)

	if thread.count() > 0:
		print("Loaded %s task(s)" % thread.count())
		print("")
		print("Running TaskEnjin")
		thread.start()
	else:
		print("No tasks to run")

elif thread_model == "fixed" or thread_model == "dynamic":
	print("Preparing multi-threaded TaskEnjin")
	
	# Initialise our thread list and task counter
	threads = []
	task_counter = 0
	thread_counter = 0
	
	if thread_model == "fixed":
		# Create our fixed amount of threads
		threads = []
		for i in range(thread_count):
			threads.append(MultiThreadedMode(i))
		thread_counter = thread_count
		
		# Prep our variables for tracking which thread we're dropping tasks into
		count = 0
		minimum = thread_skip
		maximum = thread_count
		num = minimum
		maximum = maximum - minimum
		
		# Load our tasks into our threads
		if thread_skip >= thread_count:
			print("Cannot set skip value >= count value in fixed mode")
		elif 'tasks' in json_obj:
			for id in json_obj['tasks'].keys():
				enabled = True
				if 'disabled' in json_obj['tasks'][id]:
					if json_obj['tasks'][id]['disabled']:
						enabled = False
						print("Skipping disabled task: %s" % json_obj['tasks'][id]['description'])

				if enabled:
					task = Task(id, json_obj)
					task_counter = task_counter + 1
					print("Creating task: %s (in thread %s)" % (task.description, num))
					# Add to thread
					print(threads[num].thread_id)
					(threads[num]).append(task)
					# Move onto next thread
					count = (count + 1) % maximum
					num = count + minimum
	
	elif thread_model == "dynamic":
		# Create our threads we're going to skip
		threads = [MultiThreadedMode(i) for i in range(thread_skip)]
		thread_counter = thread_skip
		
		# Prep our first thread
		thread = MultiThreadedMode(thread_counter)
		thread_counter = thread_counter + 1
		
		# Track our number of threads while at it
		num = thread_skip + 1

		# Load our tasks into our threads
		if 'tasks' in json_obj:
			for id in json_obj['tasks'].keys():
				enabled = True
				if 'disabled' in json_obj['tasks'][id]:
					if json_obj['tasks'][id]['disabled']:
						enabled = False
						print("Skipping disabled task: %s" % json_obj['tasks'][id]['description'])

				if enabled:
					task = Task(id, json_obj)
					task_counter = task_counter + 1
					print("Creating task: %s (in thread %s)" % (task.description, num))
					# Add to thread
					thread.append(task)
					
					# Append our thread to our list and prep a new one if we hit our task count in our current thread
					if thread.count() == thread_count:
						threads.append(thread)
						thread = MultiThreadedMode(thread_counter)
						thread_counter = thread_counter + 1
						num = num + 1
		
		# Append our last thread
		threads.append(thread)

	# If we have threads to run then run them
	if (len(threads) > 0) and (task_counter > 0):
		print("Loaded %s task(s) into %s thread(s)" % (task_counter, thread_counter))
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