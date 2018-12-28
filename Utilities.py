import time

# Decorator function for logging time to execute function
# Reference: https://realpython.com/primer-on-python-decorators/#timing-functions
# Reference: https://www.guru99.com/reading-and-writing-files-in-python.html
def log(inputFunction):
	def wrapper(*args, **kwargs):
		f= open("logging.txt","a+")
		startTime = time.time()
		inputFunction(*args, **kwargs)
		durationTime = time.time() - startTime
		f.write(f"\n{inputFunction.__name__} executed in {durationTime: .4f}\tStart: {startTime}, \tEnd: {startTime + durationTime}")
		f.close()
	return wrapper
