import pycron # For cron style functionality

class Task:

	def __init__(self, task_id, task_obj, datasets, variables, routines):
	
		# Load in our source data
		self.id = task_id

		# Initialise our variables
		self.description = "TaskEnjin task"
		self.interval = 60
		self.cron = -1
		self.debug = False
		self.datasets = {}
		self.variables = {}
		self.global_variables = variables
		self.routines = {}
		self.optree = []
		self.next_interval = 0

		# Load in data into our variables if applicable
		if 'description' in task_obj:
			self.description = task_obj['description']
		if 'interval' in task_obj:
			self.interval = task_obj['interval']
		if 'cron' in task_obj:
			self.cron = task_obj['cron']
		if 'datasets' in task_obj:
			self.datasets = task_obj['datasets']
		if 'variables' in task_obj:
			self.variables = task_obj['variables']
		if 'routines' in task_obj:
			self.routines = task_obj['routines']
		if 'optree' in task_obj:
			self.optree = task_obj['optree']
		if 'debug' in task_obj:
			self.debug = task_obj['debug']
		
		# Merge in our dictionaries making sure the local copies over the global
		if datasets:
			temp = datasets.copy()
			temp.update(self.datasets)
			self.datasets = temp
		''' VARS ARE NOW GLOBALLY LINKED
		if 'variables' in config_obj:
			temp = config_obj['variables'].copy()
			temp.update(self.variables)
			self.variables = temp
		'''
		if routines:
			temp = routines.copy()
			temp.update(self.routines)
			self.routines = temp

	def checkinterval(self, time):
		# Check if our time is greater than our next second
		if (time >= self.next_interval):
			# If so update our "next" interval to be the current time plus our interval
			# Note: we don't need to worry about missing intervals as that is handled higher so this works
			self.next_interval = time + self.interval
			return True
		return False
		
	def checkcron(self):
		if isinstance(self.cron, str):
			if pycron.is_now(self.cron):
				return True
		return False