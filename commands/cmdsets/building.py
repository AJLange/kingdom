"""
Skills

Commands to make building stuff easier on staff. 
These commands are locked to staff and builders only.


"""

from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia import default_cmds, create_object
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from typeclasses.rooms import Room
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.cities import City
from typeclasses.cities import PersonalRoom
from world.groups.models import PlayerGroup


'''
Built attributes created by admin should be tamper-locked:
see here to add this later:
https://www.evennia.com/docs/0.9.5/Attributes.html#locking-and-checking-attributes
'''

class CmdMakeCity(MuxCommand):
    """
    
    +makecity
    A command to create a new city or factional base object.

    Usage:
      makecity <name>=<room>

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
        '''
        do I have build permissions?
        '''
        if not caller.check_permstring("builders"):
            caller.msg("Only staff can use this command. For players, see help construct.")
            return

        if not self.args:
            caller.msg("Usage: +makecity <Name>=<Landing Room>")
            return

        if "=" in self.args:
            cityname, enterroom = self.args.rsplit("=", 1)
            enterroom_valid = self.caller.search(enterroom, global_search=True)

            #should validate if this is a room

            if not enterroom_valid == ObjectDB.objects.filter(db_typeclass_path__contains="Room"):
                caller.msg("Not a valid room.")
                return

            city = create_object("cities.City",key=cityname,location=caller.location,locks="edit:id(%i) and perm(Builders);call:false()" % caller.id)
            '''
            link entry room to city created
            '''
            try:
                
                city.db.entry = enterroom
            except:
                caller.msg("Can't find a room called %s." % enterroom)
            caller.msg("Created the city: %s" % cityname)

        else: 
            caller.msg("Usage: +makecity <Name>=<Landing Room>")
            return

'''
Todo - return of the fix rooms command that makes rooms created into IC rooms 

'''

class CmdLinkTeleport(MuxCommand):
    """

    Usage:
       portalgrid <category>

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
            hub = self.args
            room.tags.add(hub, category ="portal")

            caller.msg("Added room %s to teleport category %s." % (room, hub) )
            return
        


class CmdPlotroom(MuxCommand):
    """
    
    Usage:
       plotroom

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


class CmdLockRoom(MuxCommand):
    """
    Lock your private room.

    Usage:
        +lock 

    When you are standing in a room you own, you can use
    +lock to prevent other people from entering the room.
    This is for if you need privacy for whatever reason.

    +lock does not prevent players from leaving your private
    room. You cannot +lock someone in. It prevents entrance 
    only. +lock will not lock the room owner out of their own
    room. Just everyone else.

    +lock only works on private rooms you own, but does not
    extend to rooms that you protect. (See help +protector)

    """

    key = "construct"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        here = caller.location

        #check if I own this room
        if here.db.owner == caller:
            if here.db.locked == False:
                here.db.locked = True
                # find the exit and make sure it doesn't work
            else:
                caller.msg("This room is already locked.")

        ''' to add: I can always enter my own private room even if it's locked'''


class CmdUnLockRoom(MuxCommand):
    """
    Unlock your private room.

    Usage:
        +unlock 

    A private room object looks like an object from the outside
    but behaves like a room on the inside.
    """

    key = "construct"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        here = caller.location

        #check if I own this room
        if here.db.owner == caller:
            if here.db.locked == True:
                here.db.locked = False
                # I can now move freely into this room.
            else:
                caller.msg("This room is already unlocked.")


class CmdProtector(MuxCommand):
    """
    See who is protecting a location.

    Usage:
        +protector

    This returns a list of the characters or groups that are protecting a 
    location on the grid.

    If you intend to do violence or scheming in a particular location,
    you should alert the protectors of a location before proceeding.

    If this returns the value 'Staff' in its list, that location
    is off-limits for violent scenes without asking staff first.

    """

    key = "construct"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller

        

class CmdSetProtector(MuxCommand):
    """
    Set the protector of a room.
    Staff only command.

    Usage:
        +setprotector <name>

    This command sets the protector of a current area, or adds
    to the list if there are muiltiple protectors. 

    A protector can be a Group, or a Player, or both.

    See help +protector.    
    
    """

    key = "construct"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args
        room = caller.location

        #am I staff? be sure.

        if not caller.check_permstring("builders"):
            caller.msg("Only staff can use this command. If you need to set a protector contact a staffer.")
            return

        if not args:
            caller.msg("Add what protector?")
            return

        #accept 'staff' as a value. Staff over-rides other protectors.
        if args == "staff" or args == "Staff":
            room.db.protector = "Staff"
            return


        #todo - is this location a viable room?

        #todo - is the assigned thing a valid group? if not a group, then player?



        room.db.protector.append = args
        caller.msg("Added %s to this location's Protectors." % args)
        return