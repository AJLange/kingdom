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
        list and come in as a list. The old 'skills' value
        may still be used for something else later.

        quote and profile coming in at chargen. More stats
        as they come up.




        """
        '''
        to do, this comes in from the chargen machine, not static.
        eg , stats, skills, quote, profile should be added from char machine.
        set persistent attributes
        '''
        self.db.pow = 3
        self.db.dex = 2
        self.db.ten = 2
        self.db.cun = 3
        self.db.edu = 2
        self.db.chr = 4
        self.db.aur = 1
        self.quote = "This is a test quote."
        self.profile = "This is a test profile."


    def get_abilities(self):
        """
        Simple access method to return ability
        scores as a tuple. This for now is all stats we're using!
        """
        return self.db.pow, self.db.dex, self.db.ten, self.db.cun, self.db.edu, self.db.chr, self.db.aur
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



