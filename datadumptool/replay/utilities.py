# utilities.py
# A set of utility methods used by the Replay library.
# written by Peter Gebhard, May 2013

import logging
from datetime import datetime

logger = logging.getLogger('trustforge-replay')

def determineCreationTime(tfObj):
    if len(tfObj.reputation_history) > 0:
        return tfObj.reputation_history[-1].timestamp
    return datetime.utcnow()
