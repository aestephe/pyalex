import math
import sys
import itertools
import statistics

class Pitch:

	def __init__(self, midi_number, overtone_class = 0, is_harmonic_tone = True, harmonicity_score = 1.0, is_stable_tone = True):
	
		self.midi_number = midi_number
		self.overtone_class = overtone_class
		self.is_harmonic_tone = is_harmonic_tone
		self.harmonicity_score = harmonicity_score
		self.is_stable_tone = is_stable_tone
		
	def array_from_midi(midi_numbers):
		
		out = []
		for m in midi_numbers:
			out.append(Pitch(m))
		return out