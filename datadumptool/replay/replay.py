# replay.py
# A Replay object
# written by Peter Gebhard, March 2013

import unittest
from operator import attrgetter

from action import Action
from new_component_action import NewComponentAction
from new_testbench_action import NewTestbenchAction
from new_user_action import NewUserAction
from sortedcollection import SortedCollection

import trustmodel
from trustmodel.model import Component, User

class Replay(object):
    """ A Replay object """

    def __init__(self, timeline=None):
        """ Initialize.

        Kwargs:
            timeline (list of Actions): a timeline of all Replay Actions
        """
        if timeline is not None:
            self.timeline = timeline
        else:
            self.timeline = SortedCollection(key=attrgetter('timestamp'))

        self.repSets = [] #TODO: Define repset class

    def insertAction(self, action):
        if isinstance(action, Action):
            self.timeline.insert(action)

    def insertActions(self, actionList):
        for action in actionList:
            if isinstance(action, Action):
                self.insertAction(action)

    def playback(self):
        for action in self.timeline:
            print str(action)

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

#--------------------------------------------------------------------------------

# Test suite

class TestReplay(unittest.TestCase):
    def setUp(self):
        trustmodel.init_model()
        self.replay = Replay()
        for comp in Component.get_all():
            self.replay.insertAction(NewComponentAction(comp))
            for tb in comp.testbenches:
                self.replay.insertAction(NewTestbenchAction(comp,tb))
            for rep in comp.reputation_history:
                self.replay.addToRepSets(comp,rep)
        for user in User.get_all(active_only=False):
            self.replay.insertAction(NewUserAction(user))

        for repSet in self.replay.repSets:
            self.replay.insertAction(NewReputationAction(repSet))

    def test_playback(self):
        self.replay.playback()

    def tearDown(self):
        pass

#--------------------------------------------------------------------------------

# Module testing

if __name__ == "__main__":
    unittest.main()
