
class IntervalFlowHandler:
	interval = 1
	next_second = 0
	thread = 0
	
	def __init__(self, interval, time, thread):
		self.interval = interval
		self.next_second = time + 1
		self.thread = thread

	def check(self, time):
		if (time >= self.next_second):
			self.next_second = self.next_second + self.interval
			return True
		return False

	def run(self):
		if (self.thread.is_alive()):
			print("Already running", self.thread.optree.description)
		else:
			self.thread.start()


# Prep our timers
#timers = [TimerObject(2, latest_second, "        Boop - 2 secs"), TimerObject(3, latest_second, "        Meow - 3 secs"), #TimerObject(5, latest_second, "        Wooo - 5 secs")]
