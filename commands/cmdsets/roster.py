"""
commands related to groups and rosters
"""



from evennia import CmdSet
from evennia import Command

class CmdSetGroups(Command):
    """
    Adding a character to a particular group

    This is just stubbed out.

    Usage:
      +addgroup <person>=<group>

    """
    
    key = "+addgroup"
    help_category = "roster"

    def func(self):
        "This performs the actual command"
        errmsg = "What text?"
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            self.caller.msg(errmsg)
            return
        self.caller.db.quote = text
        self.caller.msg("Add the character to the group: %i" % text)

# to do above, make it a proper list you can add to


class CmdSetXWho(Command):

    """
    Full Who By Group
    Stubbed out only.

    Usage:
      xwho

    """
    
    key = "xwho"
    help_category = "roster"

    def func(self):
        
        self.caller.msg("Get Character List by Group")




class CmdSetWho(Command):

    """
    Full Who formatted nicely.
    Stubbed out only.

    Usage:
      who

    """
    
    key = "who"
    help_category = "roster"

    def func(self):
        
        self.caller.msg("Get Character List by Group")


"""


Syntax: who, +who                                                             
        who<Name, Letters>                                                    
        who <Faction>                                                         


        The 'who' command lists everyone online, their alias, the abbreviaton 
of the faction they're a part of, idle time, connect time, and function.      
        The who<Letters> will display only those online with the letters      
given; such as 'whot' would display everyone whose name starts with T.        
        The who <Faction> command will list only those on within that faction.
(Ex. who R, who W)                                                



"""