"""
Commands related to character creation.
For now lock these commands only to staff
and only in certain rooms flagged for chargen.

Later may add a monster-maker or something for
player GMs to use.
"""


from evennia import CmdSet
from evennia import Command
from evennia.commands.default.building import CmdSetAttribute

'''
None of the numerical stuff works yet, only takes the single argument. 
Just stubbing it out.

'''


class CmdSetStat(Command):
    """
    Sets the stats on a character. 
    Staff creating characters only.

    Usage:
      +setstat power <1-10>
      +setstat <namestat> <1-10> 


    Stats in this system are 
    Power, Dex, Tenacity
    Cunning, Edu, Charisma, Aura

    """
    
    key = "+setstat"
    help_category = "staffonly"

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

class CmdSetSkills(Command):
    """
    Sets the skills on a character. 
    Staff creating characters only.

    Usage:
      +setstat Infiltration <1-5>
      +setstat <nameskill> <1-5> 


    Valid skills in this version are
    Perception
    Athletics
    Force
    Mechanic
    Medicine
    Hacking
    Stealth
    Infiltration
    Convince
    Presence
    Mojo


    """
    
    key = "+setskill"
    help_category = "staffonly"

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



class CmdSetProfileAttr(Command):
    """
    Sets the profile info of a character.
    Staff creating characters only.

     This command sets the +finger attributes and a few other 
     static attributes. The full list is as follows: Type, 
     Game, Function, Quote, Profile, Sex


    Usage:
      +setprofile attribute=value

    """
    
    key = "+setprofile"
    help_category = "staffonly"

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
        self.caller.db.profile = text
        self.caller.msg("Profile was set to: %i" % text)



class CmdSetSpecialty(Command):
    """
    Sets the profile info of a character.
    This is for setting the specialties of characters, 
    formerly known as skills. Just a fun thing to do. Should accept
    a value or list of values spaced out by commas.

    Usage:
      +setspecialty <specialty>
      +setspecialty <spec>, <another spec>

    """
    
    key = "+setspecialty"
    help_category = "staffonly"

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
        self.caller.msg("Added a specialty at: %i" % text)

# to do above, make it a proper list you can add to

class CmdSetTypes(Command):
    """
    Setting or adding attack types to characters.

    Usage:
      +settypes <type>
      +settypes <type>, <type>

    """
    
    key = "+settype"
    help_category = "staffonly"

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
        self.caller.msg("Added a specialty at: %i" % text)






class ChargenCmdset(CmdSet):
    """
    This cmdset is used in character generation areas.
    """
    key = "Chargen"
    def at_cmdset_creation(self):
        "This is called at initialization"
        self.add(CmdSetStat())
        self.add(CmdSetSkills())
        self.add(CmdSetProfileAttr())
        self.add(CmdSetSpecialty())