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
What characters must have:

Fixed set by staff:
Name
Function
Quote
Profile 
Gender/Sex
Game (if applicable)
Type (FC or OC)
Power Source (eg Race)
Specialties (the cute list of skills)

Primary Weapon

Combat and systems:

Set Per armor form.

Stats
Skills
Abilities 
AttackTypes
Weakness
Resist
Height 
Speed

Faction related info (to be added later)

Flags which are flexible per scene:
HP

OOCfinger info:
Can be set by player so not in this file
Email
Discord
Alias
Alts
Timezone
Voice
Info

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
      +setstat/power <1-10>
      +setstat <namestat> <1-10> 


    Stats in this system are 
    Power, Dexterity, Tenacity
    Cunning, Education, Charisma, Aura

    """
    
    key = "+setstat"
    help_category = "staffonly"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        errmsg = "You must supply a number between 1 and 10."
        if not self.switches:
            caller.msg("Set which stat?")
            return
        if not self.args:
            caller.msg(errmsg)
            return
        try:
            stat = int(self.args)
        except ValueError:
            caller.msg(errmsg)
            return
        if not (1 <= stat <= 10):
            caller.msg(errmsg)
            return
        # at this point the argument is tested as valid. Let's set it.
        if "power" in self.switches:
            caller.db.pow = stat
        if "dexterity" in self.switches:
            caller.db.dex = stat
        if "tenacity" in self.switches:
            caller.db.ten = stat
        if "cunning" in self.switches:
            caller.db.cun = stat
        if "education" in self.switches:
            caller.db.edu = stat
        if "charisma" in self.switches:
            caller.db.chr = stat
        if "aura" in self.switches:
            caller.db.aur = stat

        caller.msg(f"Your {self.switches} was set to %i." % stat)

class CmdSetSkills(MuxCommand):
    """
    Sets the skills on a character. 
    Staff creating characters only.

    Usage:
      +setskill/Discern <1-5>
      +setskill/<nameskill> <1-5> 


    Valid skills in this version are
    Discern
    Flow
    Force
    Mechanics
    Medicine
    Computer
    Stealth
    Heist
    Convince
    Presence
    Arcana


    """
    
    key = "+setskill"
    help_category = "staffonly"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        errmsg = "You must supply a number between 1 and 10."
        if not self.switches:
            caller.msg("Set which skill?")
            return
        if not self.args:
            caller.msg(errmsg)
            return
        try:
            stat = int(self.args)
        except ValueError:
            caller.msg(errmsg)
            return
        if not (1 <= stat <= 10):
            caller.msg(errmsg)
            return
        # at this point the argument is tested as valid. Let's set it.
        if "discern" in self.switches:
            caller.db.discern = stat
        if "flow" in self.switches:
            caller.db.flow = stat
        if "force" in self.switches:
            caller.db.force = stat
        if "mechanics" in self.switches:
            caller.db.mechanics = stat
        if "medicine" in self.switches:
            caller.db.medicine = stat
        if "computer" in self.switches:
            caller.db.computer = stat
        if "stealth" in self.switches:
            caller.db.stealth = stat
        if "heist" in self.switches:
            caller.db.heist = stat
        if "convince" in self.switches:
            caller.db.convince = stat
        if "presence" in self.switches:
            caller.db.presence = stat
        if "arcana" in self.switches:
            caller.db.arcana = stat
        caller.msg(f"Your {self.switches} was set to %i." % stat)



class CmdSetProfileAttr(MuxCommand):
    """
    Sets the profile info of a character.
    Staff creating characters only.

     This command sets the +finger attributes and a few other 
     static attributes. The full list is as follows: Type, 
     Game, Function, Quote, Profile, Gender, Specialties
     (formerly skills)

    For now just put all the skills in one list.

    Usage:
      +setprofile/<attribute> <value>

    """
    
    key = "+setprofile"
    help_category = "staffonly"

    def func(self):
        "This performs the actual command"
        errmsg = "Not a valid attribute."
        if "gender" in self.switches:
            if self.args:
                caller.db.gender = self.args
            return
        if "type" in self.switches:
            if self.args:
                caller.db.type = self.args
            return
        if "quote" in self.switches:
            if self.args:
                caller.db.quote = self.args
            return
        if "profile" in self.switches:
            if self.args:
                caller.db.profile = self.args
            return
        if "game" in self.switches:
            if self.args:
                caller.db.game = self.args
            return
        if "function" in self.switches:
            if self.args:
                caller.db.function = self.args
            return
        if "specialties" in self.switches:
            if self.args:
                caller.db.specialties = self.args
            return 
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            self.caller.msg(errmsg)
            return

        self.caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)


class CmdSetAttribute(MuxCommand):
    """
    Sets the assorted info on a character which is 
    different per armor form.

     The full list is as follows:  
     Weakness, Resistance, Height, Speed

    For now just put all the skills in one list.

    Usage:
      +setattribute/<attribute> <value>

    """
    
    key = "+setattribute"
    help_category = "staffonly"

    def func(self):
        "This performs the actual command"
        errmsg = "Not a valid attribute."
        if "weakness" in self.switches:
            if self.args:
                caller.db.weakness = self.args
            return
        if "resistance" in self.switches:
            if self.args:
                caller.db.resistance = self.args
            return
        if "height" in self.switches:
            if self.args:
                caller.db.height = self.args
            return
        if "speed" in self.switches:
            if self.args:
                caller.db.speed = self.args
            return
        
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            self.caller.msg(errmsg)
            return

        self.caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)


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
