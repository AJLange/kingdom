"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# mygame/typeclasses/characters.py

from evennia import DefaultCharacter
from evennia.utils import ansi
import inflect

_INFLECT = inflect.engine()

class Character(DefaultCharacter):
    """
    [...]
    """
    def at_object_creation(self):
        """
        Called only at initial creation. 
        
        Intended use is that stats and skills are set as a 
        list and come in as a list from the chargen machine.
        """
        self.db.pow = 1
        self.db.dex = 1
        self.db.ten = 1
        self.db.cun = 1
        self.db.edu = 1
        self.db.chr = 1
        self.db.aur = 1
        self.db.size = "Medium"
        self.db.speed = "Medium"
        self.db.strength = "Normal"
        self.db.type = "Human"
        self.db.cookiecount = 0
        self.db.stagequota = 10
        self.db.roomquota = 10
        self.db.craftquota = 10


    def get_abilities(self):
        """
        Simple access method to return ability
        scores as a tuple. 
        """
        return self.db.pow, self.db.dex, self.db.ten, self.db.cun, self.db.edu, self.db.chr, self.db.aur

    def get_skills(self):
        """
        Simple access method to return skills
    
        """
        return self.db.discern, self.db.aim, self.db.athletics, self.db.force, self.db.mechanics, self.db.medicine, self.db.computer, self.db.stealth, self.db.heist, self.db.convince, self.db.presence, self.db.arcana


    def get_finger(self):
        """
        haha, finger
        """
        return self.db.gender, self.db.type, self.db.quote, self.db.profile, self.db.game, self.db.function, self.db.specialties

    def get_ocfinger(self):
        return self.db.alias, self.db.prefemail, self.db.discord, self.db.rptimes, self.db.voice, self.db.altchars, self.db.info

    def get_statobjs(self):
        return self.db.type, self.db.size, self.db.capabilities, self.db.speed, self.db.weakness, self.db.resistance, self.db.elements, self.db.strength

    def get_numbered_name(self, count, looker, **kwargs):
                """
                simply overloading this method to squash pluralization of character objects
                """
                key = kwargs.get("key", self.key)
                key = ansi.ANSIString(key)  
                plural = key
                singular = key
                
                return singular, plural

    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    pass



