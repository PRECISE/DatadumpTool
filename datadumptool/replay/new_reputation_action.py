# new_reputation_action.py
# A Replay New Reputation Action object
# written by Peter Gebhard, May 2013

import unittest
from datetime import datetime

from repset import RepSet

class NewReputationAction(Action):
	""" A New Reputation Action Replay object """

	def __init__(self, repset):
		""" Initialize.

		Kwargs:

		"""
		if timestamp is not None:
		    self.timestamp = timestamp
		else:
		    self.timestamp = datetime.utcnow()

	def __gt__(self, other):
		if isinstance(other, Action):
			return self.name == other.name
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result

#--------------------------------------------------------------------------------

# Test suite

class TestAction(unittest.TestCase):
	def setUp(self):
	    self.time = datetime.now()
		self.action1 = Action()
		self.action2 = Action(self.time)
		self.action3 = Action(self.time)

	def test_initialization(self):
		self.assertEqual(self.action2.timestamp, self.time)

	def test_eq_ne(self):
		self.assertEqual(self.metric1, self.metric2)
		self.assertNotEqual(self.metric1, self.metric3)

	def tearDown(self):
		pass

#--------------------------------------------------------------------------------

# Module testing

if __name__ == "__main__":
	unittest.main()
