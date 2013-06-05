# new_testbench_action.py
# A Replay New Testbench Action object
# written by Peter Gebhard, May 2013

import unittest
from datetime import datetime

import utilities
from action import Action

class NewTestbenchAction(Action):
    """ A Replay New Testbench Action object """

    def __init__(self, component, testbench):
        """ Initialize.

        Kwargs:

        """
        self.component = component
        self.testbench = testbench
        self.timestamp = self.testbench.timestamp

    def __str__(self):
        return 'NEW TESTBENCH ACTION - {0} (timestamp: {1}, comp: {2}, rev: {3})'.format(
            self.testbench.name,
            self.timestamp,
            self.component.name
            self.component.revision
        )

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
