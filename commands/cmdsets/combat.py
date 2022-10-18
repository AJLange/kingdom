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
    help_category = "Combat"

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


class CmdGMRoll(Command):
    """
    GM free rolls a certain amount of dice.

    +gmroll <number from 1-10>

    """
    
    key = "+gmroll"
    aliases = ["gmroll"]
    help_category = "Combat"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdGMRoll(Command):
    """
    GM free rolls a certain amount of dice.

    +gmroll <number from 1-10>

    """
    
    key = "+gmroll"
    aliases = ["gmroll"]
    help_category = "Combat"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return

class CmdAttack(Command):
    """
    GM free rolls a certain amount of dice.

    +attack <target>

    """
    
    key = "+attack"
    aliases = ["ttack"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdAttack(Command):
    """
    GM free rolls a certain amount of dice.

    +attack <target>

    """
    
    key = "+attack"
    aliases = ["ttack"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdRollSkill(Command):
    """
    Roll a Stat + Skill combo.

    +check <stat> <skill>

    """
    
    key = "+check"
    aliases = ["check"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return

'''

+Aim - sacrifice a round for a higher chance of hitting next round.
+Charge - sacrifice around for a higher crit chance next round. If a charge crit hits 
a weakness it does triple damage.
+Assist - sacrifice your round to add your dice to another player's roll.
+Heal (this has several varieties)
+Guard - sacrifice a round to counter/deflect
+Taunt - presence roll to do damage. Makes it slightly harder for target to 
hit other people next round
+intimidate - presence roll to do damage. Makes it slightly harder for 
target to hit you next round
+Persuade/+negotiate/+moralhighground - make a convince roll to do damage

'''


class CmdAim(Command):

    """

    +aim

    Sacrifice a combat round for a higher chance of hitting next round.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+aim"
    aliases = ["aim"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdCharge(Command):

    """

    +charge

    Sacrifice a combat round for a higher crit chance next round.
    If a charge crit hits a weakness, it does triple damage.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+charge"
    aliases = ["charge"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdTaunt(Command):

    """

    +taunt <target>

    This type of assail makes a presence roll to do damage. Using this makes 
    it slightly harder for your target to hit other people next round, 
    but slightly easier to hit you.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+taunt"
    aliases = ["taunt"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdIntimidate(Command):

    """

    +intimidate <target>

    This type of assail makes a presence roll to do damage. Using this makes 
    it slightly harder for your target to hit you next round.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+intimidate"
    aliases = ["intimidate", "spook", "+spook"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return

class CmdTaunt(Command):

    """

    +guard <target>

    Go fully defensive against a target, making it quite a bit
    harder for them to hit and damage you, but at the cost of
    any other meaningful action for the turn.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+guard"
    aliases = ["guard"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return

class CmdHeal(Command):

    """

    +heal <target>

    Don't really know how to balance this yet, won't 
    implement in early alpha.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+heal"
    aliases = ["heal"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdPersuade(Command):

    """

    +persuade <target>

    This type of assail uses your convince skill to do damage to a target.

    Only can be used in a Sequence or Showdown.

    """
    
    key = "+persuade"
    aliases = ["persuade", "negotiate" ,"+negotiate", "moralhighground" , "+moralhighground"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return
