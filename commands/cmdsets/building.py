"""
Skills

Commands to make building stuff easier on staff. 
These commands are locked to staff and builders only.


"""

from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia import default_cmds
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from typeclasses.rooms import Room
from evennia.commands.default.muxcommand import MuxCommand


'''
Built attributes created by admin should be tamper-locked:
see here to add this later:
https://www.evennia.com/docs/0.9.5/Attributes.html#locking-and-checking-attributes
'''

class CmdMakeCity(MuxCommand):
    """
    
    +makecity
    A command to create a new city or factional base object.

    usage:
    +makecity <name>=<room>

    To create a new city (or base, etc) just use +makecity and the name of 
    what you want to create. 

    The required attribute <room> is the entry point to the city, where 
    players who enter the city object will end up when entering the city.

    In future iterations, we may lock certain cities to existing groups.

    """

    key = "makecity"
    aliases = "+makecity"
    help_category = "Building"

    def func(self):
        """Implements command"""
        caller = self.caller
        


class CmdLinkTeleport(MuxCommand):
    """
    
    +portalgrid <category>

    This command adds a room to the teleportation grid, making it a
    location that can be accessed with the +portal command 
    (see help +portal).

    This adds the room to the grid for good, until it is removed.  
    It will add it under the category that you specify.

    To add a room to the grid temporarily, use +plotroom.

    Current portal grid categories: Asia, Africa, Europe, North America, 
    Oceania, South America, Mars, Solar System, Locales, Faction, Other

    """

    key = "portalgrid"
    aliases = "+portalgrid"
    locks = "cmd:all()"
    help_category = "Building"

    def func(self):
        """Implements command"""

        caller = self.caller
        room = caller.location
        if not self.args:
            caller.msg("You need to provide a portal category. See help +portalgrid.")
            return
        else:
            hub= self.args
            room.tags.add(hub, category ="portal")

            caller.msg("Added room %s to teleport category %s." % (room, hub) )
            return
        


class CmdPlotroom(MuxCommand):
    """
    
    +plotroom

    This command temporarily adds a room to the grid for +portal. 
    This command is only available to the active GM in a scene.
    It makes an announcement to the game so that
    everyone is aware of the plot room.

    If a game is already on the grid as a plotroom,
    using +plotroom again will remove it from the 
    grid. 

    This setting is temporary and will clear out 
    whenever the game is reset.

    """

    key = "plotroom"
    aliases = "+plotroom"
    locks = "cmd:all()"
    help_category = "Building"

    def func(self):
        """Implements command"""
        caller = self.caller

        #check. Am I an active GM? If so, do the thing:

        
        
