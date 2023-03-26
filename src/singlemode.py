import time # For sleep
import datetime # For unix time

from task import Task
from taskagent import TaskAgent

class SingleThreadMode:

	def __init__(self,):
		self.tasks = []

	def start(self):
		try:
			# Initiate our time variables at second -1
			current_datetime = datetime.datetime.now()
			current_unixtime = datetime.datetime.timestamp(current_datetime)
			latest_second = (current_unixtime // 1)
			last_minute = latest_second - (current_datetime.second)
			next_second = (latest_second + 1) - current_unixtime

			# Sleep until second 0
			time.sleep(next_second)

			# Effectively a second has passed
			seconds_passed = 1

			# Do our single loop
			loop = True
			
			# Create the agent that handles our tasks
			task_agent = TaskAgent()

			while loop:
				# Loop through each second that has passed
				for i in range(0, seconds_passed, 1):
					latest_second = latest_second + 1

					#Assuming the timers are more time sensitive
					for task in self.tasks:
						if task.checkinterval(latest_second):
							task_agent.run(task)

					#Check if minute has ticked over and check in with cron jobs
					if ((latest_second-last_minute) >=60):
						last_minute = last_minute + 60
						# print("A minute has ticked over")

						for task in self.tasks:
							if task.checkcron():
								task_agent.run(task)


				# We are now at second x so process our current times
				current_datetime = datetime.datetime.now()
				current_unixtime = datetime.datetime.timestamp(current_datetime)

				# Time since last second
				time_since_last_second = current_unixtime - latest_second
				current_second = (current_unixtime // 1)

				# If less than a second has passed we can wait until the next second
				if (time_since_last_second < 1):
					# Sleep until second x+1
					next_second = (current_second + 1) - current_unixtime
					time.sleep(next_second)
					#Reprocess times
					current_datetime = datetime.datetime.now()
					current_unixtime = datetime.datetime.timestamp(current_datetime)
					current_second = (current_unixtime // 1)

				# Calculate the amount of seconds that have passed
				seconds_passed = int((current_second) - latest_second)
		except KeyboardInterrupt:
			print("Detected keyboard interrupt, now exiting thread loop")
			loop = False


	def append(self, task):
		self.tasks.append(task)

	def count(self):
		return len(self.tasks)