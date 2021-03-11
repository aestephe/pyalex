
import math
import sys
import itertools
import statistics

from pyalex.pitch import *
from pyalex.utilities import *

class PitchClassPointer:
			
	def __init__(self, pitch_class_number):
		self.pitch_class_number = pitch_class_number
		self.indices = []

class Chord:

	def __str__(self):
		# produces strings of this format:
		# fund~pitch1;pitch2;pitch3...
		# each pitch is of format: midi_number,overtone_class,is_common_tone
		# (is_harmonic_tone boolean encoded as 0 or 1)
		out = (str(self.fundamental.midi_number)) + "~"
		for p in self.pitches:
			out += (str(p.midi_number) + ",")
			out += (str(int(p.overtone_class)) + ",")
			if p.is_harmonic_tone:
				out += str(1)
			else:
				out += str(0)
			out += (";")
		return out.rstrip(";")

	"""

	Constructor and factory methods.

	"""
	
	def __init__(self):
	
		self.pitches = []
		self.fundamental = Pitch(0)
		self.generate_pointers()	

	def from_pitches(pitches):
		
		out = Chord()
		out.fundamental = Pitch(0)
		out.pitches = pitches		
		out.sort_pitches_by_midi_number()
		out.generate_pointers()
		
		return out
		
	def from_fund(fund_pitch, 
				lower_bound, 
				upper_bound, 
				pitch_quantization = 1.0):
	
		out = Chord()
		out.fundamental = fund_pitch.midi_number
		out.pitches = []
		
		fund_freq = Utilities.mtof(fund_pitch.midi_number)
		x = 0
		#total_pitches = 0
		should_continue = True
	
		while should_continue:
			x += 1
			partial_freq = fund_freq * x
			#partial_midi = fund_pitch.midi_number + 12 * math.log(float(partial_freq/fund_freq), 2)
			partial_midi = Utilities.quantize_midi(Utilities.ftom(partial_freq), pitch_quantization)
			
			if partial_midi >= lower_bound:
				if partial_midi <= upper_bound:
					if (partial_midi in out.get_midi_numbers()) == False:
						out.pitches.append(Pitch(partial_midi, Utilities.get_overtone_class(x)))
					#total_pitches += 1
					#if total_pitches >= max_pitches:
					#	should_continue = False
				else:
					# we've exceeded the desired upper bound, so we should stop building
					should_continue = False 
			else:
				# do nothing - generated pitch is beneath desired lower bound, try the next pitch
				pass	
	
		out.sort_pitches_by_midi_number()
		out.generate_pointers()
		
		return out

	def from_fund_and_overtone_classes(
				fund_pitch, 
				overtone_classes, 
				lower_bound, 
				upper_bound,
				pitch_quantization = 1.0):
	
		out = Chord()
		out.fundamental = fund_pitch
		out.pitches = []
		
		fund_freq = Utilities.mtof(fund_pitch.midi_number)
		#print(fund_freq)

		for overtone_class in overtone_classes:

			should_continue = True
			m = -1
			
			while should_continue:
				m += 1
				partial_freq = fund_freq * overtone_class
				partial_midi = 12*m + Utilities.quantize_midi(Utilities.ftom(partial_freq), pitch_quantization)
											
				if partial_midi >= lower_bound:
					if partial_midi <= upper_bound:
						if (partial_midi in out.get_midi_numbers()) == False:
							out.pitches.append(Pitch(partial_midi, overtone_class, True, 1.0))
					else:
						should_continue = False 
							# we've exceeded the desired upper bound, so we should stop adding octave transpositions
							# of this partial, and move on to the next partial 
				else:
					pass 	# do nothing - generated pitch is beneath desired lower bound, try the next pitch
				
			
		out.sort_pitches_by_midi_number()
		out.generate_pointers()
		
		return out
		
	def from_string(str):
		# expects strings of this format:
		# fund~pitch1;pitch2;pitch3...
		# each pitch is of format: midi_number,overtone_class,is_common_tone
		# (is_harmonic_tone boolean encoded as 0 or 1)		
		out = Chord()
		
		l = str.split("~")
		if len(l) != 2:
			raise ValueError("list of unexpected format")
		
		out.fundamental = Pitch(float(l[0]), 1, True)
		
		m = l[1].split(";")
		
		for el in m:
			n = el.split(",")
			if len(n) != 3:
				raise ValueError("list of unexpected format")
			bool = True
			if int(n[2]) == 1:
				pass
			elif int(n[2]) == 0:
				bool = False
			else:
				raise ValueError("list of unexpected format")
			p = Pitch(float(n[0]), int(n[1]), bool)
			out.pitches.append(p)
		
		return out

	"""

	Pointer generator and pitch sorter
	(constructor and factory methods should call these where necessary).

	"""
	def generate_pointers(self):
		# generate the pitch class pointers
		self.pointers = []
		for pc in range(0, 12):
			pointer = PitchClassPointer(pc) # make a new pointer for this pitch class
			# now iterate through each of the pitches to find occurrence of the pitch class 
			# when we find an occurrence we'll add its index number to the pointer
			for i in range(0, len(self.pitches)):
				# round pitch to nearest semitone when calculating pitch class
				rounded_midi = 0
				if (float(self.pitches[i].midi_number) % 1) >= 0.5:
					rounded_midi = int(math.ceil(self.pitches[i].midi_number))
				else:
					rounded_midi = int(round(self.pitches[i].midi_number))
				if rounded_midi%12 == pc: 
					pointer.indices.append(i)
			self.pointers.append(pointer)	

	def sort_pitches_by_midi_number(self):
		s = sorted(self.pitches, key = lambda p: (p.midi_number))
		self.pitches = s

	"""

	Return various data about the chord.

	"""

	def get_midi_numbers(self):
		out = []
		self.sort_pitches_by_midi_number()
		for p in self.pitches:
			out.append(p.midi_number)
		return out

	def get_midi_intervals(self, exclude_ncts = False):
		self.sort_pitches_by_midi_number()
		out = []
		for i in range(0, len(self.pitches) - 1):
			int = self.pitches[i + 1].midi_number - self.pitches[i].midi_number
			if exclude_ncts and (self.pitches[i].is_harmonic_tone == False or self.pitches[i].is_harmonic_tone == False):
				pass
			else:
				out.append(int)
		if len(out) > 0:
			return out
		else:
			return [0]
	
	def get_common_tones(self, other_chord, count_ncts_as_common_tones = True):
		out = []
		for p in self.pitches:
			if p.midi_number in other_chord.get_midi_numbers():
				if p.is_harmonic_tone == False and count_ncts_as_common_tones == False:
					# ignore - don't add it as a common tone
					pass
				else:
					out.append(p)
		return out

	def contains_all_pitches(self, desired_pitches):
		out = True
		for p in desired_pitches:
			if (p.midi_number in self.get_midi_numbers()) == False:
				out = False
				break
		return out
	
	def contains_any_pitches(self, desired_pitches):
		out = False
		for p in desired_pitches:
			if p.midi_number in self.get_midi_numbers():
				out = True
				break
		return out

	def contains_all_intervals(self, intervals):
		out = True
		for int in intervals:
			if not int in self.get_midi_intervals():
				out = False
				break
		return out
		
	def contains_any_intervals(self, intervals):
		out = False
		for int in intervals:
			if  int in self.get_midi_intervals():
				out = True
				break
		return out

	def average_interval(self):
		return(statistics.mean(self.get_midi_intervals()))

	def median_interval(self):
		return(statistics.median(self.get_midi_intervals()))
		
	def interval_variety(self, exclude_ncts = False):
		return (max(self.get_midi_intervals(exclude_ncts)) - min(self.get_midi_intervals(exclude_ncts)))

	def largest_interval(self):
		return (max(self.get_midi_intervals()) - min(self.get_midi_intervals()))
		
	def total_span(self):
		return (max(self.get_midi_numbers()) - min(self.get_midi_numbers()))

	def missing_pitch_classes(self):
		self.generate_pointers()
		out = []
		for pointer in self.pointers:
			if len(pointer.indices) == 0:
				out.append(pointer.pitch_class_number)
		return out
		
	def get_harmonic_tone_status_of_pc(self, pc):
		true_count = 0
		false_count = 0
		for i in self.pointers[int(pc)].indices:
			if self.pitches[i].is_harmonic_tone:
				true_count += 1
			else:
				false_count += 1
				
		if true_count > 0 and false_count > 0:
			raise ValueError("There is a mixture of harmonic and non-harmonic tones for pc " +
						str(pc) + ", can't return status")
						
		if true_count > false_count:
			return True
		if false_count > true_count:
			return False
	
	"""

	Explodes the current chord given the condition that all pitch classes appear no more than once.
	All possible chords which arise under this condition will be returned.

	"""

	def get_unique_pc_voicings(self, force_fund_register = True):
		
		# eliminates all pitch class duplications in the inputted chord, in all possible combinations
		# returns a list of chords, each of which contains no duplications
	
		self.sort_pitches_by_midi_number()
		out = []
			
		# generate lists of indices
		# each list should contain exactly one index from each pointer...
		# ...assuming that pointer has at least one index!
		self.generate_pointers()
		l = []
		for pointer in self.pointers:
			if len(pointer.indices) > 0:
				l.append(pointer.indices)		
		unique_indices = list(itertools.product(*l))
			
		# each list of indices is used to extract pitches from the chord which contain no octave duplications
		# new chords are formed from these pitches
		for index_list in unique_indices:
		
			should_use = True
			if force_fund_register and (self.get_midi_numbers().index(self.fundamental.midi_number) in index_list) == False:
				should_use = False
					
			if should_use:
				new_chord_pitches = []
				for z in range (0, len(index_list)):
					new_chord_pitches.append(self.pitches[index_list[z]])
				c = Chord.from_pitches(new_chord_pitches)
				c.fundamental = self.fundamental
				c.generate_pointers()
				c.sort_pitches_by_midi_number()
				out.append(c)
			
		return out


	"""

	A method of adding "non-chord tones" to the chord, conceived as non-harmonic voicings 
	(i.e., one or more octaves too low) of specified overtone classes.

	"""
			
	def add_ncts_from_overtone_classes(self, nct_overtone_classes, nct_lower_bound, nct_upper_bound, pitch_quantization):

		fund_freq = Utilities.mtof(self.fundamental.midi_number)

		for nct_overtone_class in nct_overtone_classes:
			
			# the midi pitch value if the overtone class were voiced as a partial in the series 
			# (i.e. in the lowest possible "correct" octave)
			harmonic_midi = Utilities.quantize_midi(Utilities.ftom(fund_freq * nct_overtone_class), pitch_quantization)
			
			# add "incorrect" (inharmonic) versions of the pitch by transposing it down octave(s)
			should_continue = True
			octaver = 0
			
			while should_continue:
				octaver += 1
				candidate_midi = harmonic_midi - (12*octaver)
				if nct_lower_bound <= candidate_midi <= nct_upper_bound:
					self.pitches.append(Pitch(candidate_midi, nct_overtone_class, 
											is_harmonic_tone = False, harmonicity_score = 1/(octaver+1)))
				if candidate_midi < nct_lower_bound:
					should_continue = False
		
			self.sort_pitches_by_midi_number()
			self.generate_pointers()
