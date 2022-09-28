"""
Combat Related Commands

"""


from calendar import c
from evennia import CmdSet
from commands.command import Command
from evennia.commands.default.muxcommand import MuxCommand
from server.utils import sub_old_ansi


"""
Combat is a type of scene called a Showdown which can be initiated via a showdown command

"""

class CmdShowdown(Command):
    """
    Starts a showdown.

    Usage:
        +showdown <name>
        +showdown <name>,<name>
        +showdown/boss


    +showdown with a single name challenges that person to a duel.
    +showdown with multiple targets invites everyone to partake.
    +showdown/boss begins a showdown with everyone in the room who is not
    set as observer.

    If a showdown is in progress between multiple people, initiating a 
    showdown with one of those targets invites you to combat with all
    of those targets.

    """
    
    key = "+showdown"
    help_category = "combat"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "You must supply a target, or choose +showdown/boss to attack everyone."
        
        occupied = False
        caller= self.caller
        if self.switches or self.args:
            if "boss" in self.switches:
                self.caller.msg("You start a boss fight in this location!")
                caller.location.msg_contents(caller.name + " has begun a Boss Showdown in this location!" )

                '''
                    what needs to happen:
                    Set HP based on the involved number of attackers
                '''

        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            self.caller.msg("You attack.")
        except ValueError:
            self.caller.msg(errmsg)
            return
        if not (occupied):
            occupied = True
            self.caller.msg(errmsg)
            return
        else:
            self.caller.msg("That person is already in a showdown.")
