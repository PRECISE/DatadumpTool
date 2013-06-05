# -*- coding: utf-8 -*-

"""
Datadump Tool
~~~~~~~~~~~~~~~~~~~~~

The PRECISE Lab Datadump Tool is a Python-based command-line utility for deploying, querying,
and generating statistics from MongoDB datadumps. Basic usage:

   TODO...

:copyright: (c) 2013 by Peter Gebhard.
:license: TBD, see LICENSE for more details.

"""

__title__ = 'datadumptool'
__version__ = '0.2'
__author__ = 'Peter Gebhard'
__license__ = 'TBD'
__copyright__ = 'Copyright 2013 Peter Gebhard'

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
