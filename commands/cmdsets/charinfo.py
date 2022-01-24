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
        


