"""
Commands related to character creation.
For now lock these commands only to staff
and only in certain rooms flagged for chargen.

Later may add a monster-maker or something for
player GMs to use.
"""


from evennia import CmdSet
from evennia import Command
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.rooms import ChargenRoom
from evennia import create_object


'''
None of the numerical stuff works yet, only takes the single argument. 
Just stubbing it out.

What characters must have:

Fixed set by staff:
Name
Function
Quote
Profile 
Primary Weapon
Gender/Sex
Game (if applicable)
Type (FC or OC)
Power Source (eg Race)
Specialties (the cute list of skills)

OOCfinger info (can be set by player):
Email
Contact/Discord
Alias
Alts
Timezone/Location
Voice Actor
Theme/Music
Info
RP Hooks

Combat and systems:
(set per armor form)
Stats
Skills
Abilities/Capabilities (collapsing this back into one thing)
AttackTypes
Armor forms
Weakness
Resist
Height/Size 
Speed

Faction related info (to be added later)

Flags which are flexible per scene:
HP


'''

class CmdStartChargen(MuxCommand):
    """
    
    +chargen
    +chargen/finish

    This command will temporarily give you access to the rest
    of the chargen commands. It can only be done in a chargen
    enabled room.  For now, this command is only available
    to staffers in staff only areas.

    """
    
    key = "+chargen"
    help_category = "staffonly"

    def func(self):
        caller = self.caller
        location = caller.location
        chargeninit = "You have begun character creation. You now have access to character setup commands. When you are done making a character, +chargen/finish."
        
        if isinstance(location, ChargenRoom):
            '''
            deleting command doesn't work but adding it does? idk.
            commenting this out until i understand this better.

            if "finish" in self.switches or "done" in self.switches:
                caller.msg("You finish generating a character.")
                #remove the chargen command set
                self.cmdset.delete(ChargenCmdset)
                
            else:
                '''
            caller.msg(chargeninit)
                # add the chargen command set
            self.cmdset.add(ChargenCmdset)
            
        else:
            caller.msg("You cannot do chargen here.")
            return
        


class CmdCreatePC(Command):
    """
    Create a new PC

    Usage:
        +createPC <name>

    Creates a new, named PC. 
    """
    key = "+createpc"
    aliases = ["+createPC"]
    locks = "call:not perm(nonpcs)"
    help_category = "staffonly"
    
    def func(self):
        "creates the object and names it"
        caller = self.caller
        if not self.args:
            caller.msg("Usage: +createPC <name>")
            return

        # make name always start with capital letter
        name = self.args.strip().capitalize()
        # create in caller's location
        npc = create_object("characters.Character",
                      key=name,
                      location=caller.location,
                      locks="edit:id(%i) and perm(Builders);call:false()" % caller.id)
        # announce
        message = "%s created the PC '%s'."
        caller.msg(message % ("You", name))
        caller.location.msg_contents(message % (caller.key, name),
                                                exclude=caller)


class CmdSetStat(MuxCommand):
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
        self.caller.db.pow = power
        self.caller.msg("Your Power was set to %i." % power)

class CmdSetSkills(MuxCommand):
    """
    Sets the skills on a character. 
    Staff creating characters only.

    Usage:
      +setskill Perception <1-5>
      +setskill <nameskill> <1-5> 


    Valid skills in this version are
    Perception
    Athletics
    Force
    Mechanic
    Medicine
    Computer
    Stealth
    Larceny
    Convince
    Presence
    Arcana


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



class CmdSetProfileAttr(MuxCommand):
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
        self.add(CmdSetSpecialty())
        self.add(CmdSetSkills())
        self.add(CmdSetProfileAttr())
