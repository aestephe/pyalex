import math
import threading

class LengthMultiplier:

	def __init__(self, value):
		self._value = value

	def get_value(self):
		return self._value

	def clone(lm, expon):
		return LengthMultiplier(lm.get_value() ** expon)

class LengthMultiplierManager:

	def __init__(self):
		self._dict = {}
		self._lock = threading.Lock()

	def set_length_multipliers(self, dictionary):
		with self._lock:
			for name in dictionary:
				self._dict[name] = dictionary[name]

	def get_length_multiplier(self, name):
		with self._lock:
			return self._dict[name]

	def get_all_length_multipliers(self):
		with self._lock:
			return [self._dict[key] for key in self._dict]


class Utilities:

	def mtof(midi):
		return 440 * 2**((float(midi-69))/12)
		

	def ftom(freq):
		return 69 + (12 * math.log(float(freq/440), 2))


	def get_numerical_pitch_class(midi_pitch):
		
		rounded_pitch = 0
		if (float(midi_pitch) % 1) >= 0.5:
			rounded_pitch = int(math.ceil(midi_pitch))
		else:
			rounded_pitch = int(round(midi_pitch))
		
		return rounded_pitch%12
	

	def get_register(midi_pitch):
		return str(int(round(midi_pitch, 0))/12 - 1)	
		

	def are_pcs_equal(midi_pitch1, midi_pitch2):
		if Utilities.get_numerical_pitch_class(midi_pitch1) == Utilities.get_numerical_pitch_class(midi_pitch2):
			return True
		else:
			return False
			

	def get_overtone_class(partial_number):
		out = partial_number
		while out%2 == 0:
			out = out/2
		return out
	

	def get_param_val(xml_root, parameter_name):
		out = ""
		results = xml_root.findall(parameter_name)
		if len(results) == 0:
			raise ValueError(parameter_name + " not found in parameter file")
		elif len(results) > 1:
			raise ValueError("Extraneous " + parameter_name + " in parameter file")
		else:
			result = results[0]
			out = result.text
		return out
	

	def string_to_list_of_float(string):
		out = []
		if string is not None:
			list = string.split(',')
			for i in range(0, len(list)):
				out.append(float(list[i]))
		return out
		

	def quantize_midi(midi, pitch_quantization):
		# 1 = semitones, 0.5 = quarter-tones etc.
		return round(midi * (1/pitch_quantization)) / (1/pitch_quantization)


	def ratio_to_midi_interval(ratio):
		return 12 * math.log(ratio, 2)


	def midi_interval_to_ratio(midi_interval):
		return pow(2, (midi_interval/12))


	def clip(value, minimum, maximum):
		if minimum <= value <= maximum:
			return value
		elif value < minimum:
			return minimum
		elif value > maximum:
			return maximum


	def clip_and_wrap(value, minimum, maximum, wrap_value):
		if minimum <= value <= maximum:
			return value
		elif value < minimum:
			while value < minimum:
				value += wrap_value
			return value
		elif value > maximum:
			while value > maximum:
				value -= wrap_value
			return value

 
	def scale(value, input_min, input_max, output_min, output_max):
		return output_min + (((value - input_min) * (output_max - output_min)) / (input_max - input_min))


	def get_anglophone_pitch_class(midi_pitch, accidentals = "b"):

		if accidentals != "b" and accidentals != "#":
			raise ValueError("Argument accidentals should be specified as 'b' or '#'")

		spell_with_flats = True
		if accidentals == "b":
			spell_with_flats = True
		elif accidentals == "#":
			spell_with_flats = False

		rounded_pitch = 0
		if (float(midi_pitch) % 1) >= 0.5:
			rounded_pitch = int(math.ceil(midi_pitch))
		else:
			rounded_pitch = int(round(midi_pitch))

		number = rounded_pitch%12

		if number == 0:
			return "C"
		elif number == 1:
			if spell_with_flats:
				return "Db"
			else:
				return "C#"
		elif number == 2:
			return "D"
		elif number == 3:
			if spell_with_flats:
				return "Eb"
			else:
				return "D#"
		elif number == 4:
			return "E"
		elif number == 5:
			return "F"
		elif number == 6:
			if spell_with_flats:
				return "Gb"
			else:
				return "F#"
		elif number == 7:
			return "G"
		elif number == 8:
			if spell_with_flats:
				return "Ab"
			else:
				return "G#"
		elif number == 9:
			return "A"
		elif number == 10:
			if spell_with_flats:
				return "Bb"
			else:
				return "A#"
		elif number == 11:
			return "B"