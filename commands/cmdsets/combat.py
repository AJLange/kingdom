"""
Combat Related Commands

"""


from calendar import c
from evennia import CmdSet
from commands.command import Command
from evennia.commands.default.muxcommand import MuxCommand
from server.utils import sub_old_ansi
from random import randint
from evennia import Command, InterruptCommand

'''
constants set here for testing purposes
'''

DUEL_HP = 9
STANDARD_HP = 6


def do_roll(stat, skill):

    '''
    roll a particular stat-skill combo. Used in combat commands.
    These are pooled rolls so return a list.

    '''

    '''
    to-do: exploding 10s
    K&T as written: 10s explode for PCs but not for GMs/NPCs.
    dice are also success if 7 or higher - use colors.
    '''
    stat_roll = list(range(stat))
    skill_roll = list(range(skill))
    for i in range(0, stat):
        random = randint(1,10)
        stat_roll[i] = random
    for j in range(0,skill):
        random = randint(1,10)
        skill_roll[j] = random
    return stat_roll, skill_roll

"""
Combat is a type of scene called a Showdown which can be initiated via a showdown command

"""

class CmdShowdown(Command):
    """
    Starts a showdown.

    Usage:
        +showdown <name>
        +showdown/boss

    +showdown with a single name challenges that person to a duel.
    +showdown/boss begins a showdown with everyone in the room who is not
    set as observer.

    This is currently not balanced for 2 on 1 or other configurations.
    A duel in progress can't be third-partied. However, multiple
    boss fights can be initiated in the same location.

    """
    
    key = "+showdown"
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.

        to-do: test balance for other configurations.
        occupied check needs to sync with db in case of reset.

        '''
        errmsg = "You must supply a target, or choose +showdown/boss to attack everyone."
        
        occupied = False
        caller= self.caller
        if self.switches or self.args:
            if "boss" in self.switches:
                caller.msg("You start a boss fight in this location!")
                caller.location.msg_contents(caller.name + " has begun a Boss Showdown in this location!" )

                '''
                    what needs to happen:
                    Set HP based on the involved number of attackers
                '''
            

        if not self.args:
            caller.msg(errmsg)
            return
        try:
            '''
            do-to: error check - is target a character? are they in the room?
            '''
            target = self.args
            caller.msg(f"You start a showdown with {target.name}.")
            target.msg(f"{caller.name} has challenged you a duel!")
            ''' 
            set duel HP
            '''
            target.db.hp = DUEL_HP
            caller.db.hp = DUEL_HP

            if not (occupied):
                occupied = True
                return
            else:
                caller.msg("That person is already in a duel.")
        except ValueError:
            caller.msg(errmsg)
            return


class CmdGMRoll(Command):
    """
    GM free rolls a certain amount of dice.

    Usage:
       +gmroll <number from 1-10>

    This is for if you just need to roll D10s for whatever reason in a 
    scene you may be running.

    To roll a die with an arbitrary amount of sides, see +roll.

    """
    
    key = "+gmroll"
    aliases = ["gmroll"]
    help_category = "Dice"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Roll how many dice?")
            return
        '''convert argument to a number'''
        args = self.args.lstrip()
        try:
            numdice = int(args)
            if not 1 <= numdice <=10:
                raise ValueError
        except ValueError:
            caller.msg("Number of dice must be an integer between 1 and 10.")
            raise InterruptCommand

        result = list(range(numdice))
        outputmsg = (f"{caller.name} rolls:")
        errmsg = "An error occured."
        for i in range(0, numdice):
            random = randint(1,10)
            result[i] = random
            outputmsg = outputmsg + " " + str(result[i])

        try:
            caller.location.msg_contents(outputmsg, from_obj=caller)
        except ValueError:
            caller.msg(errmsg)
            return

        '''
        to-do: parse this to an amount of successes
        '''


class CmdRoll(Command):
    """
    Roll an arbitrary die.

    Usage:
       +roll <number from 1-100>

    This will choose a random integer, depending on the 
    size of the die you choose to roll. This is a purely 
    random choice to be used for arbitrary decision making.

    Rolling a die other than 1d10 is not an official game 
    mechanic or part of the combat system, but can sometimes
    be useful.

    """
    
    key = "+roll"
    aliases = ["roll"]
    help_category = "Dice"

    def func(self):
        errmsg = "An error occured."
        caller = self.caller

        if not self.args:
            caller.msg("Roll what size die?")
            return
        '''convert argument to a number'''
        args = self.args.lstrip()
        try:
            dice = int(args)
            if not 1 <= dice <=100:
                raise ValueError
        except ValueError:
            self.msg("Please choose a die size as an integer between 1 and 100.")
            raise InterruptCommand

        result = randint(1,dice)
        name = caller.name
        try:
            message = (f"{name} rolls a D{dice} and rolls a {result}.")
            caller.location.msg_contents(message, from_obj=caller)

        except ValueError:
            caller.msg(errmsg)
            return


class CmdFlip(Command):
    """
    Flip a coin.

    Usage:
       +flip

    This command flips a coin, with a result of heads or tails.

    There are two uses for this command. One is of an OOC nature, when
    you may just be trying to choose between two outcomes. If you 
    need to choose between more than two possible outcomes, see +roll.

    This command may also be used to indicate an IC flip of a coin, as 
    in the opening round of a Battle and Chase sporting match, or for
    other dramatic reasons.

    Please note that when the coin flip mechanic is used IC, some characters
    do have the ability to cheat on the coin flip.

    """
    
    key = "+flip"
    aliases = ["flip"]
    help_category = "Dice"

    def func(self):
        caller = self.caller
        errmsg = "An error occured."

        '''
        to do: the rest of the command
        '''

        try:
            caller.msg(f"You flipped a coin.")
        except ValueError:
            caller.msg(errmsg)
            return


'''

holding this space, might not use this command

class CmdStatRoll(Command):
    """
    Stat roll an individual stat. Useful for a quick check.

    Usage:
      +statroll <stat>
      +statroll Aur


    """
    
    key = "+statroll"
    aliases = ["statroll"]
    help_category = "Dice"

    def func(self):

        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Roll which stat?")
            return
        try:
            self.caller.msg("You Roll.")
        except ValueError:
            caller.msg(errmsg)
            return
'''

class CmdRollSkill(Command):
    """
    Roll a Stat + Skill combo.

    Usage:
        +check <stat> + <skill>

    This allows any combination of rolls. Can be used to check any two stats.
    Useful in one-off confrontations, if trying to do something unusual, or
    if a particular roll is called by a GM in a Sequence.

    Currently it is not possible to check just a stat. Always choose
    which skill you want to roll. See news files for combo examples.

    """
    
    key = "+check"
    aliases = ["check"]
    help_category = "Dice"


    def func(self):

        #todo: any bonus dice that need added might be added?

        caller = self.caller
        errmsg = "Wrong syntax. Please enter a valid stat and skill seperated by +."
        if not self.args:
            caller.msg(errmsg)
            return
        args = self.args
        try:
            stat, skill = args.split("+",1)
            stat = stat.strip()
            skill = skill.strip()
        except ValueError:
            caller.msg(errmsg)
            return
        
        errmsg = "An error occured. Contact staff to help debug this."
        
        try:
            stat_check = caller.get_a_stat(stat)
            skill_check = caller.get_a_skill(skill)

            # build the string

            result = do_roll(stat_check,skill_check)
            if len(result[0]) == 0 or len(result[1]) == 0:
                caller.msg("Skill + stat combination invalid. Try again.")
                return
            else:
                str_result = str(result)
                outputmsg = (f"{caller.name} rolls {stat} and {skill}: {str_result}" )
                caller.location.msg_contents(outputmsg, from_obj=caller)
            
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

'''
            
todo: the assail commands below are stubs, need to take an argument (target)
'''

class CmdAttack(Command):
    """
    Attacking a particular target. 

    +attack <target>

    """
    
    key = "+attack"
    aliases = ["attack"]
    help_category = "Dice"

    def func(self):
        '''
        doesn't function yet just stubbing out commands.
        '''
        errmsg = "An error occured."
        
        caller= self.caller
        
        if not self.args:
            caller.msg("Attack who?")
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

        errmsg = "An error occured."        
        caller= self.caller

        if not self.args:
            caller.msg("Taunt who?")
            return
        '''
        todo: get cunning, charisma, aura, tenacity, use highest value
        '''
        stat = caller.get_a_stat("chr")
        skill = caller.get_a_skill("presence")

        try:
            result = do_roll(stat, skill)
            str_result = str(result)
            outputmsg = (f"{caller.name} rolls to taunt: {str_result}" )
            caller.location.msg_contents(outputmsg, from_obj=caller)
        except ValueError:
            caller.msg(errmsg)
            return


class CmdIntimidate(Command):

    """

    +intimidate <target>

    This type of assail makes a presence roll to do damage. Using this makes 
    it slightly harder for your target to hit you next round.

    Only can be used in a Sequence or Showdown.
    
    Only can be used once per target per Sequence/Showdown. The effect
    does not stack.

    """
    
    key = "+intimidate"
    aliases = ["intimidate", "spook", "+spook"]
    help_category = "Dice"

    def func(self):

        errmsg = "An error occured."        
        caller= self.caller
        
        if not self.args:
            caller.msg("Intimidate who?")
            return
        '''
        todo: get power, charisma, aura, and use the highest value
        '''
        stat = caller.get_a_stat("chr")
        skill = caller.get_a_skill("presence")

        try:
            result = do_roll(stat, skill)
            str_result = str(result)
            outputmsg = (f"{caller.name} rolls to intimidate: {str_result}" )
            caller.location.msg_contents(outputmsg, from_obj=caller)
        except ValueError:
            caller.msg(errmsg)
            return

class CmdGuard(Command):

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

        errmsg = "An error occured."        
        caller= self.caller
        
        # does not function yet
        if not self.args:
            caller.msg("Guard who?")
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

        errmsg = "An error occured."        
        caller= self.caller
        
        if not self.args:
            caller.msg("Persuade who?")
            return

        '''
        todo: charisma, cunning, education, get the highest value
        apply any bonus dice for pose or circumstance
        '''
        stat = caller.get_a_stat("chr")
        skill = caller.get_a_skill("convince")

        try:
            result = do_roll(stat, skill)
            str_result = str(result)
            outputmsg = (f"{caller.name} rolls to persuade: {str_result}" )
            caller.location.msg_contents(outputmsg, from_obj=caller)
        except ValueError:
            caller.msg(errmsg)
            return


class CmdRollSet(MuxCommand):
    """
    Usage:
      +rollset
      +rollset/verbose
      +rollset/basic

    Swap between die view modes. Setting rollset to 'verbose' will show all of the 
    individual roles that lead to a die result. Setting to 'basic' will only show
    the final narrative result. 

    +rollset on its own toggles between these two readout modes.

    """
    
    key = "+rollset"
    aliases = ["rollset"]
    help_category = "Dice"

    def func(self):
        '''
        Doesn't function yet. Just sets the value to allow this to function in the future.
        '''
        errmsg = "A value error occured. Contact staff about this error."
        
        caller = self.caller

        '''
        rollset 1 is verbose. rollset 2 is basic.

        if there's no switch, check current value and toggle.
        '''

        if not self.switches:
            if caller.db.rollset == 1:
                caller.db.rollset = 2
                caller.msg("Set roll view type to basic.")
                return
            elif caller.db.rollset == 2:
                caller.db.rollset = 1
                caller.msg("Set roll view type to verbose.")
                return
            else:
                caller.msg(errmsg)        

        '''
        had a switch, so just set the value
        '''

        if "verbose" in self.switches:
            caller.db.rollset = 1
            caller.msg("Set roll view type to verbose.")
            return
        elif "basic" in self.switches:
            caller.db.rollset = 2
            caller.msg("Set roll view type to basic.")
            return
        else:
            caller.msg("Not a valid choice. Choose verbose or basic.")
            return
        