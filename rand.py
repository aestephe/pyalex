import random

class Randomizer:

	def __init__(self, clock_mod, output_range):

		if not len(output_range) == 2:
			raise ValueError("output_range must be an array of two numbers (min and max)")

		self._clock_mod = clock_mod
		self._output_range = output_range

		self._clock = 0
		self._value = 0

	def get_value(self):
		
		if self._clock % self._clock_mod == 0:
			self._value = random.randint(self._output_range[0], self._output_range[1])
		else:
			pass # don't update

		self._clock += 1

		return self._value

class RandomizerGroup:

	def __init__(self, nbr_randomizers, output_range, ban_repeat_average_value, seed_value = None):

		self.randomizers = []
		for i in range(0, nbr_randomizers):
			self.randomizers.append(Randomizer(clock_mod = 2 ** i, output_range = output_range))
		self.ban_repeat_average_value = ban_repeat_average_value
		self._last_average_value = None
		self._seed_value = seed_value

	def get_average_value(self):

		out = None
		should_try = True

		if self._seed_value is not None and self._last_average_value is None:
			out = self._seed_value
			self._last_average_value = self._seed_value
			should_try = False

		while should_try:
			sum = 0
			for randomizer in self.randomizers:
				sum += randomizer.get_value()
			out = int(sum/len(self.randomizers))
			if not self._last_average_value is None:
				if self.ban_repeat_average_value and out == self._last_average_value:
					should_try = True
				else:
					should_try = False
			else:
				should_try = False
		self._last_average_value = out

		return out
