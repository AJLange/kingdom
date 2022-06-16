"""
Commands related to getting information about characters.

Finger, OOCFinger, Efinger (aka IC finger)

To add: FClist related commands
Commands related to FC sorting

Other fun info options as needed
"""


from evennia import CmdSet
from commands.command import BaseCommand
from evennia.commands.default.muxcommand import MuxCommand
from server.utils import sub_old_ansi
from math import floor




class CmdFinger(BaseCommand):
    """

    +finger <character>

    To get basic information about a character.
    Useful for an OOC overview and for potential 
    appers.
    """
    key = "+finger"
    aliases = ["finger", "+figner", "figner", "profile", "+profile"]
    lock = "cmd:all()"
    help_category = "General"

    def func(self):
        "This performs the actual command"
        if not self.args:
            self.caller.msg("Finger who?")
            return

        # find a player in the db who matches this string
        player = self.caller.search(self.args)
        if not player:
            return
        char = player
        if not char:
            self.caller.msg("Character not found.")
            return
        try:
            self.caller.msg(f"{char.name} |/ Finger information lives here.")
        except ValueError:
            self.caller.msg("Not a valid character.")
            return
        


class CmdEFinger(BaseCommand):
    """

    +efinger <character>
    +info <character>

    To get basic IC information about a character.
    Usually set to what is publically known or can be
    looked up about a character from an IC standpoint,
    including their reputation and known abilities.
    
    """
    key = "+efinger"
    aliases = ["efinger", "+efigner", "efigner", "info", "+info"]
    lock = "cmd:all()"
    help_category = "General"

    def func(self):
        "This performs the actual command"
        if not self.args:
            self.caller.msg("Finger who?")
            return

        # find a player in the db who matches this string
        player = self.caller.search(self.args)
        if not player:
            return
        char = player
        if not char:
            self.caller.msg("Character not found.")
            return
        try:
            self.caller.msg(f"{char.name} Eventually Efinger information would go here.")
        except ValueError:
            self.caller.msg("Some error occured.")
            return
        



class CmdOOCFinger(BaseCommand):
    """
    
    +oocfinger <character>
    
    To get basic OOC information which relates to 
    the player of the character. You can find
    personal RP hooks and other preferences
    set here, as well as any OOC contact information
    the player feels comfortable to provide.
    
    """
    key = "+oocfinger"
    aliases = ["oocfinger","ofinger", "+ofigner", "ofigner", "+oocfigner"]
    lock = "cmd:all()"
    help_category = "General"

    def func(self):
        "This performs the actual command"
        if not self.args:
            self.caller.msg("Finger who?")
            return

        # find a player in the db who matches this string
        player = self.caller.search(self.args)
        if not player:
            return
        char = player
        if not char:
            self.caller.msg("Character not found.")
            return
        try:
            self.caller.msg(f"Name: {char.name} |/ OOCFinger information lives here.")
        except ValueError:
            self.caller.msg("Some error occured.")
            return
        


class CmdSheet(BaseCommand):
        """
        List my stats

        Usage:
        +stats

        Displays a list of your current stats.
        """
        key = "+stats"
        aliases = ["stats", "sheet", "+sheet"]
        lock = "cmd:all()"
        help_category = "General"

        def func(self):
            """implements the actual functionality"""

            pow, dex, ten, cun, edu, chr, aur = self.caller.get_abilities()
            # right now this just pulls numbers/stats, to be fixed once skills are set in stone.
            perception, athletics, force, mechanics, medicine, computer, stealth, larceny, convince, presence, arcana = self.caller.get_skills()
            line1 = "Name: "
            line2 = "Racetype: Power Types:" 
            line3 = "Current Mode:"            
            line4= "POW: %s, DEX: %s, TEN: %s, CUN: %s, EDU: %s, CHR: %s, AUR: %s"  % (pow, dex, ten, cun, edu, chr, aur)
            line5 = "Perception: %s, Athletics: %s, Force: %s, Mechanics: %s, Medicine: %s, Computer: %s, Stealth: %s , Larceny: %s , Convince: %s, Presence: %s, Arcana: %s"  % (perception, athletics, force, mechanics, medicine, computer, stealth, larceny, convince, presence, arcana)
            line6 = "Capabilities: "
            line7 =  "Size, Speed"
            line8 = "Elements: Weakness/Resistance:"
            # not sure yet about attack lists, if that will be a thing or not
            sheetmsg = (line1 + "\n" + line2 + "\n" + line3 + "\n" + line4  + "\n" + line5 + "\n" + line6 + "\n" + line7 + "\n" + line8)
            self.caller.msg(sheetmsg)



class CmdSetDesc(MuxCommand):
    """
    describe yourself
    Usage:
      setdesc <description>
    Add a description to yourself. This
    will be visible to people when they
    look at you.
    """

    key = "setdesc"
    aliases = ["@desc"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    # Here I overwrite "setdesc" from the Evennia master so it has an alias, "@desc."
    def func(self):
        """add the description"""

        if not self.args:
            self.caller.msg("You must add a description.")
            return

        message = self.args
        message = sub_old_ansi(message)
        self.caller.db.desc = message
        self.caller.msg("You set your description.")
