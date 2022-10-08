"""
Skills

Commands to make building stuff easier on staff. 
These commands are locked to staff and builders only.


"""

from math import floor
from math import randint
#from typing import AwaitableGenerator
from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia import default_cmds
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from evennia.comms.models import Msg
from world.scenes.models import Scene, LogEntry
from typeclasses.rooms import Room
from world.supplemental import *


'''
Built attributes created by admin should be tamper-locked:
see here to add this later:
https://www.evennia.com/docs/0.9.5/Attributes.html#locking-and-checking-attributes
'''