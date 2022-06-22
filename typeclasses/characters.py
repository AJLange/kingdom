"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# mygame/typeclasses/characters.py

from evennia import DefaultCharacter


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
        self.db.aur = 4


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
        # note this doesn't work right now, not until chargen machine allows adding all stats. 
        return self.db.pow, self.db.dex, self.db.ten, self.db.cun, self.db.edu, self.db.chr, self.db.aur, self.db.cun, self.db.edu, self.db.chr, self.db.aur



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



