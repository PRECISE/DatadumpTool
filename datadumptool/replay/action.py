# action.py
# A Replay Action object
# written by Peter Gebhard, March 2013

import unittest
from datetime import datetime

class Action(object):
    """ A Replay Action object """

    def __init__(self, timestamp=None):
        """ Initialize.

        Kwargs: timestamp (datetime): The time the action occurred.

        """
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.utcnow()

    def __gt__(self, other):
        if isinstance(other, Action):
            return self.timestamp > other.timestamp
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Action):
            return self.timestamp < other.timestamp
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Action):
            return self.timestamp <= other.timestamp
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Action):
            return self.timestamp >= other.timestamp
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Replay):
            # TODO: Is this good enough?
            return self.timeline == other.timeline
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self):
        return self.__str__()

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

    def tearDown(self):
        pass

#--------------------------------------------------------------------------------

# Module testing

if __name__ == "__main__":
    unittest.main()
