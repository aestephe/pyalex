import math

class Utilities:

	def get_numerical_pitch_class(midi_pitch):
		
		rounded_pitch = 0
		if (float(midi_pitch) % 1) >= 0.5:
			rounded_pitch = int(math.ceil(midi_pitch))
		else:
			rounded_pitch = int(round(midi_pitch))
		
		return rounded_pitch%12

	def get_anglophone_pitch_class(midi_pitch):
		rounded_pitch = 0
		if (float(midi_pitch) % 1) >= 0.5:
			rounded_pitch = int(math.ceil(midi_pitch))
		else:
			rounded_pitch = int(round(midi_pitch))

		number = rounded_pitch%12
		if number == 0:
			return "C"
		elif number == 1:
			return "Db"
		elif number == 2:
			return "D"
		elif number == 3:
			return "Eb"
		elif number == 4:
			return "E"
		elif number == 5:
			return "F"
		elif number == 6:
			return "Gb"
		elif number == 7:
			return "G"
		elif number == 8:
			return "Ab"
		elif number == 9:
			return "A"
		elif number == 10:
			return "Bb"
		elif number == 11:
			return "B"
	
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
		
	def mtof(midi):
		return 440 * 2**((float(midi-69))/12)
		
	def ftom(freq):
		return 69 + (12 * math.log(float(freq/440), 2))
		
	def quantize_midi(midi, pitch_quantization):
		# 1 = semitones, 0.5 = quarter-tones etc.
		return round(midi * (1/pitch_quantization)) / (1/pitch_quantization)

		