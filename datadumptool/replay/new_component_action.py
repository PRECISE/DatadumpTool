# action.py
# A Replay Action object
# written by Peter Gebhard, March 2013

import unittest
from datetime import datetime

import utilities
from action import Action

class NewComponentAction(Action):
    """ A Replay New Component Action object """

    def __init__(self, component):
        """ Initialize.

        Kwargs:

        """
        self.component = component
        self.timestamp = utilities.determineCreationTime(self.component)

    def __str__(self):
        return 'NEW COMPONENT ACTION - {0} (timestamp: {1}, rev: {2})'.format(
            self.component.name,
            self.timestamp,
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
        pass

    def tearDown(self):
        pass

#--------------------------------------------------------------------------------

# Module testing

if __name__ == "__main__":
    unittest.main()
