# action.py
# A Replay Action object
# written by Peter Gebhard, March 2013

import unittest
from datetime import datetime

import utilities
from action import Action

class NewUserAction(Action):
    """ A Replay New User Action object """

    def __init__(self, user):
        """ Initialize.

        Kwargs:

        """
        self.user = user
        self.timestamp = utilities.determineCreationTime(self.user)

    def __str__(self):
        return 'NEW USER ACTION - {0} (timestamp: {1})'.format(
            self.user.name,
            self.timestamp
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
