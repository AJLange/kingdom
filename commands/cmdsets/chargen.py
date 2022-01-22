"""
Commands related to character creation.
For now lock these commands only to staff
and only in certain rooms flagged for chargen.

Later may add a monster-maker or something for
player GMs to use.
"""


from evennia import CmdSet


class CmdSetStat(Command):
    """
    Sets the stats on a character. 
    Staff creating characters only.

    Usage:
      +stat/set power <1-10>
      +stat/set <namestat> <1-10> 


    Stats in this system are 
    Power, Dex, Tenacity
    Cunning, Edu, Charisma, Aura

    """
    
    key = "+stat/set"
    help_category = "mush"

    def func(self):
        "This performs the actual command"
        errmsg = "You must supply a number between 1 and 10."
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            power = int(self.args)
        except ValueError:
            self.caller.msg(errmsg)
            return
        if not (1 <= power <= 10):
            self.caller.msg(errmsg)
            return
        # at this point the argument is tested as valid. Let's set it.
        self.caller.db.power = power
        self.caller.msg("Your Power was set to %i." % power)