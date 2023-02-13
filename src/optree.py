class OpTree:

	id = ''
	description = "OpTree"
	interval = 60
	datasets = {}
	variables = {}
	routines = {}
	tree = []

	def __init__(self, optree_id, config_obj):
		self.id = optree_id
		source_obj = config_obj['optrees'][optree_id]
		
		#Load in our data if applicable
		if 'description' in source_obj:
			self.description = source_obj['description']
		if 'interval' in source_obj:
			self.interval = source_obj['interval']
		if 'datasets' in source_obj:
			self.datasets = source_obj['datasets']
		if 'variables' in source_obj:
			self.variables = source_obj['variables']
		if 'routines' in source_obj:
			self.routines = source_obj['routines']
		if 'tree' in source_obj:
			self.tree = source_obj['tree']
		
		#Merge in our dictionaries making sure the local copies over the global
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