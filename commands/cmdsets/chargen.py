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

Reminder: be sure to lock changing most attributes to admin only.

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

    To do chargen in order:
    +chargen
    +createpc <name>
    +workchar <name>
    +setstat/<namestat> <1-10> (for all 7 stats)
    +setskill/<nameskill> <1-5> (for all 12 skills)
    +setprofile/<attribute> <value> (for all 7 text attributes)
    +settypes <type>, <type> (for all elemental types)
    +setpower <name> (for the character's 'racetype' aka power set sources)
    +chargen/finish

    Armor modes, and characters with multiple power sets, are not working
    in the pre-alpha build.

    """
    
    key = "+chargen"
    help_category = "Chargen"

    def func(self):
        caller = self.caller
        location = caller.location
        chargeninit = "You have begun character creation. You now have access to character setup commands. When you are done making a character, +chargen/finish. For the list of commands, see +help +chargen."
        
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
    aliases = ["createPC"]
    locks = "call:not perm(nonpcs)"
    help_category = "Chargen"
    
    def func(self):
        "creates the object and names it"
        caller = self.caller
        if not self.args:
            caller.msg("Usage: +createPC <name>")
            return

        # set name as set
        name = self.args
        # create in caller's location
        character = create_object("characters.Character",
                      key=name,
                      location=caller.location,
                      locks="edit:id(%i) and perm(Builders);call:false()" % caller.id)
        # announce
        message = "%s created the PC '%s'."
        caller.msg(message % ("You", name))
        caller.location.msg_contents(message % (caller.key, name),
                                                exclude=caller)
        return 


class CmdWorkChar(Command):
    """
    Work on a Character. This sets the character that you 
    are working on. To be used after creating the PC using +createpc.

    Usage:
        +workchar <name>

    Sets the character to work on. Only works in the chargen room.
    Is persisent on server reset, just in case you get interrupted.

    """
    key = "+workchar"
    aliases = ["workchar"]
    locks = "call:not perm(nonpcs)"
    help_category = "Chargen"
    
    def func(self):
        "creates the object and names it"
        caller = self.caller
        if not self.args:
            caller.msg("Usage: +workchar <name>")
            return

        # set name as set
        name = self.args
        # create in caller's location
        character = self.caller.search(name)
        if not character:
            caller.msg("Sorry, couldn't find that PC.")
            return
        
        # announce
        caller.db.workingchar = character
        
        message = "%s now working on the PC '%s'."
        caller.msg(message % ("You're", name))
        caller.location.msg_contents(message % (caller.key, name),
                                                exclude=caller)
        return 


class CmdSetStat(MuxCommand):
    """
    Sets the stats on a character. 
    Staff creating characters only.

    Usage:
      +setstat/power <1-10>
      +setstat/<namestat> <1-10> 


    Stats in this system are 
    Power, Dexterity, Tenacity
    Cunning, Education, Charisma, Aura

    """
    
    key = "+setstat"
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
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
            character.db.pow = stat
        if "dexterity" in self.switches:
            character.db.dex = stat
        if "tenacity" in self.switches:
            character.db.ten = stat
        if "cunning" in self.switches:
            character.db.cun = stat
        if "education" in self.switches:
            character.db.edu = stat
        if "charisma" in self.switches:
            character.db.chr = stat
        if "aura" in self.switches:
            character.db.aur = stat

        caller.msg(f"The PC's {self.switches} was set to %i." % stat)

class CmdSetSkills(MuxCommand):
    """
    Sets the skills on a character. 
    Staff creating characters only.

    Usage:
      +setskill/Discern <1-5>
      +setskill/<nameskill> <1-5> 


    Valid skills in this version are
    Discern
    Athletics
    Aim
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
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
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
            character.db.discern = stat
        if "aim" in self.switches:
            character.db.aim = stat
        if "athletics" in self.switches:
            character.db.althetics = stat
        if "force" in self.switches:
            character.db.force = stat
        if "mechanics" in self.switches:
            character.db.mechanics = stat
        if "medicine" in self.switches:
            character.db.medicine = stat
        if "computer" in self.switches:
            character.db.computer = stat
        if "stealth" in self.switches:
            character.db.stealth = stat
        if "heist" in self.switches:
            character.db.heist = stat
        if "convince" in self.switches:
            character.db.convince = stat
        if "presence" in self.switches:
            character.db.presence = stat
        if "arcana" in self.switches:
            character.db.arcana = stat
        caller.msg(f"The PC's {self.switches} was set to %i." % stat)



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
    help_category = "Chargen"

    '''
    This works, but it's pretty sloppy and could really use a refactor.
    '''

    def func(self):
        "This performs the actual command"
        errmsg = "Set value to what?"
        caller = self.caller
        character = caller.db.workingchar 
        if "gender" in self.switches or "Gender" in self.switches:
            if self.args:
                text = self.args
                character.db.gender = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return
        if "type" in self.switches or "Type" in self.switches:
            if self.args:
                text = self.args
                character.db.type = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return
        if "quote" in self.switches or "Quote" in self.switches:
            if self.args:
                text = self.args
                character.db.quote = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return
        if "profile" in self.switches or "Profile" in self.switches:
            if self.args:
                text = self.args
                character.db.profile = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return
        if "game" in self.switches or "Game" in self.switches:
            if self.args:
                text = self.args
                character.db.game = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return
        if "function" in self.switches or "Function" in self.switches:
            if self.args:
                text = self.args
                character.db.function = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return
        if "specialties" in self.switches or "Specialties" in self.switches:
            if self.args:
                text = self.args
                character.db.specialties = self.args
                caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)
            else:
                caller.msg(errmsg)
            return 
        if not self.args:
            self.caller.msg("Not a valid attribute.")
            return
        else:
            self.caller.msg("Not a valid attribute.")
            return

'''
        try:
            text = self.args
        except ValueError:
            self.caller.msg("Not a valid attribute.")
            return
'''
        


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
    help_category = "Chargen"
    

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
        errmsg = "Not a valid attribute."
        if "weakness" in self.switches:
            if self.args:
                character.db.weakness = self.args
            return
        if "resistance" in self.switches:
            if self.args:
                character.db.resistance = self.args
            return
        if "height" in self.switches:
            if self.args:
                character.db.height = self.args
            return
        if "speed" in self.switches:
            if self.args:
                character.db.speed = self.args
        if "strength" in self.switches:
            if self.args:
                character.db.strength = self.args
            return
        
        if not self.args:
            caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            caller.msg(errmsg)
            return

        caller.msg(f"Profile Attribute {self.switches} was set to: %s" % text)


'''

Not working for now. Just copy+paste an entire list.

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
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        errmsg = "What text?"
        self.caller.db.quote = text
        self.caller.msg("Added a specialty at: %s" % text)
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            self.caller.msg(errmsg)
            return
        
'''

# to do above, make it a proper list you can add to

class CmdSetTypes(Command):
    """
    Setting or adding attack types to characters.

    Usage:
      +settypes <type>
      +settypes <type>, <type>

    """
    
    key = "+settype"
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
        errmsg = "What text?"
        if not self.args:
            caller.msg(errmsg)
            character.db.attacktype = text
            caller.msg("Added an attack type at: %s" % text)
            return
        try:
            text = self.args
        except ValueError:
            caller.msg(errmsg)
            return
        

class CmdSetWeapons(MuxCommand):
    """
    Setting or adding attack types to characters.

    Usage:
      +setweapon <type>
      +setweapon/primary <type>
      +setweapon/secondary <type>

    not figured out how I intend to do this, but
    stubbing it out.

    Ability to set primary and secondary weapon also lives here.

    """
    
    key = "+setweapon"
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
        errmsg = "What text?"
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            caller.msg(errmsg)
            return
        character.db.quote = text
        caller.msg("Added this weapon: %s" % text)

class CmdSetArmors(Command):
    """
    Setting or adding armors to characters.

    Usage:
      +setarmor <name>

    This command currently doesn't do anything, 
    but is a good test for if other chargen
    commands are available to the user.

    When you execute it, you'll get a confirmation
    that you added an armor but nothing else happens yet.
    """
    
    key = "+setarmor"
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
        errmsg = "What text?"
        if not self.args:
            caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            caller.msg(errmsg)
            return
        character.db.quote = text
        caller.msg("Added an armor named: %s" % text)

class CmdSetPowers(Command):
    """
    Setting or adding armors to characters.

    Usage:
      +setpower <name>

    This sets the power source on characters.
    Power sources are tied to certain abilities.

    This command works, but is temporary. You can also use
    +setprofile/type <power>


    """
    
    key = "+setpower"
    help_category = "Chargen"

    def func(self):
        "This performs the actual command"
        caller = self.caller
        character = caller.db.workingchar 
        errmsg = "What text?"
        if not self.args:
            caller.msg(errmsg)
            return
        try:
            text = self.args
            character.db.type = text
            caller.msg("Added the power: %i" % text)
        except ValueError:
            caller.msg(errmsg)
            return
        


class ChargenCmdset(CmdSet):
    """
    This cmdset is used in character generation areas.
    """
    key = "Chargen"
    def at_cmdset_creation(self):
        "This is called at initialization"
        self.add(CmdCreatePC())
        self.add(CmdSetStat())
        self.add(CmdWorkChar())
        #self.add(CmdSetSpecialty())
        self.add(CmdSetSkills())
        self.add(CmdSetTypes())
        self.add(CmdSetWeapons())
        self.add(CmdSetArmors())
        self.add(CmdSetProfileAttr())
        self.add(CmdSetPowers())
