import pycron # For cron style functionality

class Task:

	def __init__(self, task_id, config_obj):
	
		# Load in our source data
		self.id = task_id
		source_obj = config_obj['tasks'][task_id]

		# Initialise our variables
		self.description = "TaskEnjin task"
		self.interval = 60
		self.cron = -1
		self.debug = False
		self.datasets = {}
		self.variables = {}
		self.routines = {}
		self.optree = []
		self.next_interval = 0

		# Load in data into our variables if applicable
		if 'description' in source_obj:
			self.description = source_obj['description']
		if 'interval' in source_obj:
			self.interval = source_obj['interval']
		if 'cron' in source_obj:
			self.cron = source_obj['cron']
		if 'datasets' in source_obj:
			self.datasets = source_obj['datasets']
		if 'variables' in source_obj:
			self.variables = source_obj['variables']
		if 'routines' in source_obj:
			self.routines = source_obj['routines']
		if 'optree' in source_obj:
			self.optree = source_obj['optree']
		if 'debug' in source_obj:
			self.debug = source_obj['debug']
		
		# Merge in our dictionaries making sure the local copies over the global
		if 'datasets' in config_obj:
			temp = config_obj['datasets'].copy()
			temp.update(self.datasets)
			self.datasets = temp
		if 'variables' in config_obj:
			temp = config_obj['variables'].copy()
			temp.update(self.variables)
			self.variables = temp
		if 'routines' in config_obj:
			temp = config_obj['routines'].copy()
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