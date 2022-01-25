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