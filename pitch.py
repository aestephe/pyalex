import math
import sys
import itertools
import statistics

class Pitch:

	def __init__(self, 
				midi_number, 
				overtone_class = 0, 
				is_harmonic_tone = True):
	
		self.midi_number = midi_number
		self.overtone_class = overtone_class
		self.is_harmonic_tone = is_harmonic_tone

	def __str__(self):

		out = (str(self.midi_number) + ",")
		out += (str(int(self.overtone_class)) + ",")
		if self.is_harmonic_tone:
			out += str(1)
		else:
			out += str(0)

		return out

	def from_string(s):

			n = s.split(",")
			if len(n) != 3:
				raise ValueError("list of unexpected format")
			b = True
			if int(n[2]) == 1:
				pass
			elif int(n[2]) == 0:
				b = False
			else:
				raise ValueError("list of unexpected format")
			return Pitch(float(n[0]), int(n[1]), b)

	def array_from_midi(midi_numbers):
		
		out = []
		for m in midi_numbers:
			out.append(Pitch(m))
		return out