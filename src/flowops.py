import threading # For multithreading inheritance
import time # For sleep
import requests # For webhook
import subprocess # For pings and any other system calls

from datetime import datetime # For unix time

class FlowThread (threading.Thread):

	ping_count_flag = 'c'
	ping_count = 1
	ping_timeout = 150
	optree = {}
	loop = True

	def __init__(self, optree, os_type):
		threading.Thread.__init__(self)
		self.optree = optree
		if os_type == 'windows':
			self.ping_count_flag = 'n'

	def run(self):
		current_time = 0
		next_run = int(datetime.now().timestamp())
	
		while self.loop:
			current_time = int(datetime.now().timestamp())
			if current_time >= next_run:
				self.run_ops(self.optree.tree)
				next_run = current_time + self.optree.interval
			
			time.sleep(1)
			
	def stop(self):
		print("Stopping %s" % self.optree.description)
		self.loop = False

	def run_ops(self, op):
		if op['function'] == 'ping':
			self.run_ping(op)
		elif op['function'] == 'log':
			self.run_log(op)
		elif op['function'] == 'if':
			self.run_if(op)
		elif op['function'] == 'webhook':
			self.run_webhook(op)

	def run_ping(self, op):
		ping_command = ['ping', "-%s" % self.ping_count_flag, str(self.ping_count), '-w', str(self.ping_timeout), op['address']]

		ping_result =  subprocess.run(ping_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

		print("Ping to %s result was %s" % (op['address'], ping_result.returncode))

		if 'output' in op:
			op['output']['result'] = ping_result.returncode

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

		if 'variablea' in op:
			variable_A = op['variablea']
		elif 'result' in op:
			variable_A = op['result']

		if 'variableb' in op:
			variable_B = op['variableb']

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
			self.run_ops(op['outputtrue'])
		else:
			self.run_ops(op['outputfalse'])


	def run_webhook(self, op):
		#print("WEBHOOK")
		#headers = { 'Content-Type': 'application/json' }

		#response = requests.post(op["url"], json = op["post"])

		#print(response.status_code)

		if 'output' in op:
			self.run_ops(op['output'])