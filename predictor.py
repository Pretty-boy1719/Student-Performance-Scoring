from random import choice


def predict(data):
	"""
	Some ML
	"""

	result = {}
	counter = 0
	for sheet in data:
		for pupil in data[sheet]:
			counter += 1
			result[str(counter)] = choice(["отчислен", "не отчислен"])
	
	return result
