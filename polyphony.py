import math
import random
import sys
import itertools
import threading
import scamp

class VoiceId:

	'''
	A simple wrapper for encoding information about a polyphonic voice.
	'''

	def __init__(self, name, thread_id):
		self.name = name
		self.thread_id = thread_id

class QueuedVoiceManager:

	'''
	Voice manager for polyphonic situations in which multiple voices cannot play at the same time
		(e.g. in a piece for solo instrument).
	Voices should call the manager to enter a queue and check for permission to play.
	Only one voice is given permission to play at a time, and once a voice finishes and asks to leave
		the queue, the manager waits a controllable amount of time before granting another voice permission.
	N.B. this class is intended for use in projects deploying the SCAMP library
		(the dequeueing procedure is handled via calls to scamp.wait()).
	'''

	def are_voices_closely_related(self, voice1_name, voice2_name):
		out = False
		for pair in self.closely_related_voices:
			if pair[0] == voice1_name and pair[1] == voice2_name:
				out = True
			elif pair[0] == voice2_name and pair[1] == voice1_name:
				out = True
		return out

	def __init__(self):

		self.previous_voices = []
		self.should_try_play = True 
		self.closely_related_voices = []
		self.closely_related_dequeue_multiplier = 1.0

		self._q = []
		self._lock = threading.Lock()
		self._banned_voices = []
		self._vip_voice = None
		self._dequeue_times = []
		self._dequeue_iterator = 0

	def request_permission(self, my_id: VoiceId):

		with self._lock:

			should_append = True
			for elem in self._q:
				if elem.name == my_id.name and elem.thread_id == my_id.thread_id:
					should_append = False
			if my_id.name in self._banned_voices:
				should_append = False
			if not (self._vip_voice is None):
				if not (self._vip_voice == my_id.name):
					should_append = False

			if should_append:
				self._q.append(my_id)

			out = False
			if len(self._q) > 0:
				if self._q[0].thread_id == my_id.thread_id:
					out = True

			return out

	def leave_queue(self, my_id):

		new_q = [elem for elem in self._q if (not elem.name == my_id.name and not elem.thread_id == my_id.thread_id)]

		if len(new_q) > 0:

			if new_q[0].name == my_id.name:
				# no need to delay, because the next voice waiting to play is of the same type (has the same name)
				pass
			elif self.are_voices_closely_related(my_id.name, new_q[0].name):
				if self.closely_related_dequeue_multiplier > 0:
					scamp.wait(self._get_dequeue_time() * self.closely_related_dequeue_multiplier)
			else:
				scamp.wait(self._get_dequeue_time())

		else:
			scamp.wait(self._get_dequeue_time())

		with self._lock:
			self._q = new_q
			self.previous_voices.append(my_id.name)
			if len(self.previous_voices) > 2:
				self.previous_voices.pop(0)

	def set_dequeue_times(self, times):

		with self._lock:
			self._dequeue_times = times

	def block_voice(self, name):

		with self._lock:
			if not (name in self._banned_voices):
				self._banned_voices.append(name)

	def unblock_voice(self, name):

		with self._lock:
			if name in self._banned_voices:
				self._banned_voices.remove(name)

	def enter_vip_mode(self, name):

		with self._lock:
			self._vip_voice = name

	def exit_vip_mode(self):

		with self._lock:
			self._vip_voice = None

	def _get_dequeue_time(self):

		if len(self._dequeue_times) == 0:
			raise IndexError("No dequeue times have been set")

		with self._lock:
			self._dequeue_iterator = (self._dequeue_iterator + 1) % len(self._dequeue_times)
			return self._dequeue_times[self._dequeue_iterator]

