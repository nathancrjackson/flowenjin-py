import threading # For multithreading inheritance
import time # For sleep
import requests # For webhook
import subprocess # For pings and any other system calls

from datetime import datetime # For unix time

class FlowThread (threading.Thread):

	debug = False
	ping_count_flag = 'c'
	ping_count = 1
	ping_timeout = 150
	optree = {}
	#loop = True

	def __init__(self, optree, os_type):
		threading.Thread.__init__(self)
		self.optree = optree
		if os_type == 'windows':
			self.ping_count_flag = 'n'

	def run(self):
		# Should just need to run this now that the timing is handled by the main thread
		self.run_ops(self.optree.tree)
		
		time.sleep(0)
	
		#current_time = 0
		#next_run = int(datetime.now().timestamp())
		#
		#while self.loop:
		#	current_time = int(datetime.now().timestamp())
		#	if current_time >= next_run:
		#		self.run_ops(self.optree.tree)
		#		next_run = current_time + self.optree.interval
		#	
		#	time.sleep(1)
	
	# TODO: Is this required?
	def stop(self):
		print("Stopping %s" % self.optree.description)
		#self.loop = False
			
	def debuglog(self, string):
		if self.debug:
			print(string)

	def run_ops(self, op):
		if isinstance(op, list):
			for listitem in op:
				self.run_ops(listitem)
		else:
			if op['function'] == 'if':
				self.run_if(op)
			elif op['function'] == 'setvariable':
				self.run_setvariable(op)
			elif op['function'] == 'variableincrease':
				self.run_variableincrease(op)
			elif op['function'] == 'variabledecrease':
				self.run_variabledecrease(op)
			elif op['function'] == 'variablereset':
				self.run_variablereset(op)
			elif op['function'] == 'ping':
				self.run_ping(op)
			elif op['function'] == 'log':
				self.run_log(op)
			elif op['function'] == 'webhook':
				self.run_webhook(op)

	def run_ping(self, op):
	
		ping_target = "127.0.0.1"
	
		if 'targetaddress' in op:
			ping_target = op['targetaddress']
		elif 'targetvariable' in op:
			ping_target = self.optree.variables[op['targetvariable']]
		elif 'result' in op:
			ping_target = op['result']
	
		ping_command = ['ping', "-%s" % self.ping_count_flag, str(self.ping_count), '-w', str(self.ping_timeout), ping_target]

		ping_result =  subprocess.run(ping_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

		self.debuglog("Ping to %s result was %s" % (ping_target, ping_result.returncode))

		if 'output' in op:
			op['output']['result'] = ping_result.returncode

			self.run_ops(op['output'])

	def run_setvariable(self, op):
		#print("setvariable")
		value = ""

		if 'value' in op:
			value = op['value']
		elif 'result' in op:
			value = op['result']

		if 'name' in op:
			self.optree.variables[op['name']] = value
			self.debuglog("%s set to %s" % (op['name'], self.optree.variables[op['name']]))
			
		if 'output' in op:
			self.run_ops(op['output'])
		

	def run_variableincrease(self, op):
		#print("variableincrease")
		
		if 'name' in op:
			self.optree.variables[op['name']] = self.optree.variables[op['name']] + 1
			self.debuglog("%s set to %s" % (op['name'], self.optree.variables[op['name']]))
			
		if 'output' in op:
			self.run_ops(op['output'])

	def run_variabledecrease(self, op):
		#print("variabledecrease")
		
		if 'name' in op:
			self.optree.variables[op['name']] = self.optree.variables[op['name']] - 1
			self.debuglog("%s set to %s" % (op['name'], self.optree.variables[op['name']]))
			
		if 'output' in op:
			self.run_ops(op['output'])

	def run_variablereset(self, op):
		#print("variablereset")
		
		if 'name' in op:
			self.optree.variables[op['name']] = 0
			self.debuglog("%s set to %s" % (op['name'], 0))
			
		if 'output' in op:
			self.run_ops(op['output'])

	def run_log(self, op):
		#print("LOG")
		print(op['message'])
		if 'output' in op:
			self.run_ops(op['output'])

	def run_if(self, op):
		variable_A = ""
		variable_B = True
		operation = '='

		if 'valuea' in op:
			variable_A = op['valuea']
		elif 'variablea' in op:
			variable_A = self.optree.variables[op['variablea']]
		elif 'result' in op:
			variable_A = op['result']

		if 'valueb' in op:
			variable_B = op['valueb']
		elif 'variableb' in op:
			variable_B = self.optree.variables[op['variableb']]

		if 'operation' in op:
			operation = op['operation']

		result = False

		if operation == '=':
			result = (variable_A == variable_B)
		elif operation == '==':
			result = (variable_A == variable_B)
		elif operation == '!=':
			result = (variable_A != variable_B)
		elif operation == '<':
			result = (variable_A < variable_B)
		elif operation == '>':
			result = (variable_A > variable_B)
		elif operation == '<=':
			result = (variable_A <= variable_B)
		elif operation == '>=':
			result = (variable_A >= variable_B)

		if result == True:
			if 'outputtrue' in op:
				self.debuglog("%s %s %s is True" % (variable_A, operation, variable_B))
				self.run_ops(op['outputtrue'])
		else:
			if 'outputfalse' in op:
				self.debuglog("%s %s %s is False" % (variable_A, operation, variable_B))
				self.run_ops(op['outputfalse'])


	def run_webhook(self, op):
		#print("WEBHOOK")
		headers = { 'Content-Type': 'application/json' }

		response = requests.post(op["url"], json = op["post"])

		self.debuglog("Webhook response code: %s" % response.status_code)

		if 'output' in op:
			op['output']['result'] = response.status_code
			self.run_ops(op['output'])