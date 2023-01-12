from evennia.commands.default.muxcommand import MuxCommand


class CmdConstruct(MuxCommand):
    """
    Create a private room object.
    Players will have a limited quota of private room objects.
    Construct a room using 

    construct <name of room>
    eg
    construct Doctor's Office
    """

    key = "construct"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("What do yo want to construct?")
            return

        ''' to do: the rest of the command '''


class CmdCraft(MuxCommand):
    """
    Create a small object.
    Players will have a limited quota of miscellaneous objects.
    These objects can hold a desc, but have no other 
    functionality. 

    craft <name of object>
    eg
    craft Soccer Ball
    """

    key = "craft"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("What do yo want to craft?")
            return

        ''' to do: the rest of the command '''


'''
notes here on player quotas:
10 items
10 personal rooms
10 stages

per player character.
Pets can only be created by staff for now (may change later)

'''