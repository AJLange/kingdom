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

class CmdFinger(default_cmds.MuxCommand):
    """
        +finger
        Usage:
          +finger <character>
        Displays finger'd character's information
        """

    key = '+finger'
    aliases = ["finger", "oocfinger", "+oocfinger"]
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            # TODO: better messaging
            self.caller.msg("Need a person to finger!")
            return

        # We've tried changing the evennia-master code in evennia/objects/object.py to allow for non-exact string
        # matching with global_search=True, but this seems to cause "examine <db_id>" to fail
        # TODO: figure out a way to have partial string matching AND db_id referencing. Might be able to do this with more playing around with the if-else logic in objects.py
        target = self.caller.search(self.args, global_search=True)

        # TODO: actually figure out error handling. Need to be able to differentiate between "ambiguous search" error and "not a character" error
        try:
            char = target.get_abilities()
            charInfoTable = evtable.EvTable(border_left_char="|", border_right_char="|", border_top_char="-",
                                            border_bottom_char=" ", width=78)
            charInfoTable.add_column()
            charInfoTable.add_column()
            charInfoTable.add_row("Sex: {0}".format(char["sex"]), "Group: {0}".format(char["group"]))
            charInfoTable.add_row("Race: {0}".format(char["race"]), "Domain: {0}".format(char["domain"]))
            charInfoTable.add_row("Origin: {0}".format(char["origin"]), "Element: {0}".format(char["element"]))

            charDescTable = evtable.EvTable(border="table", border_left_char="|", border_right_char="|",
                                            border_top_char="-",
                                            border_bottom_char="_", width=78)
            charDescTable.add_column()
            charDescTable.add_row('"{0}"'.format(char["quote"]))
            charDescTable.add_row("")
            charDescTable.add_row("{0}".format(char["profile"]))

            fingerMsg = ""
            fingerMsg += "/\\" + 74 * "_" + "/\\" + "\n"

            # TODO: we want if-else logic to add an alias if they have it, and just spit out their name if they don't
            nameBorder = "\\/" + (37 - floor(len(char["name"] + " - " + char["occupation"]) / 2.0)) * " "
            nameBorder += char["name"] + " - " + char["occupation"]
            nameBorder += (76 - len(nameBorder)) * " " + "\\/"
            fingerMsg += nameBorder + "\n"

            charInfoString = charInfoTable.__str__()
            fingerMsg += charInfoString[:charInfoString.rfind('\n')] + "\n"  # delete last newline (i.e. bottom border)
            fingerMsg += charDescTable.__str__() + "\n"
            fingerMsg += "/\\" + 74 * "_" + "/\\" + "\n"
            fingerMsg += "\\/" + 74 * " " + "\\/" + "\n"

            self.caller.msg(fingerMsg)
        except:
            self.caller.msg("Target is either not a character or there are multiple matches")




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
        




class CmdSheet(default_cmds.MuxCommand):
        """
        List attributes
        Usage:
          sheet, score
        Displays a list of your current ability values.
        """
        key = "sheet"
        aliases = ["score"]
        lock = "cmd:all()"
        help_category = "General"

        def func(self):
            "implements the actual functionality"
            # TODO: We did this before we knew about the evtable function. This needs to be refactored.
            char = self.caller.get_abilities()
            # name, sex, race, occupation, group, domain, element, origin, quote, profile, lf, maxlf, ap, maxap, ex, maxex, \
            # power, knowledge, parry, barrier, speed = self.caller.get_abilities()
            sheetMsg = ""

            sheetMsg += "/\\" + 74 * "_" + "/\\" + "\n"
            nameBorder = "\\/" + (37 - floor(len(char["name"] + " - " + char["occupation"])/2.0)) * " "
            nameBorder += char["name"] + " - " + char["occupation"]
            nameBorder += (76 - len(nameBorder))*" " + "\\/"
            sheetMsg += nameBorder + "\n"
            sheetMsg += "--" + 74 * "-" + "--" + "\n"

            # first row
            firstRow = "| LF"
            firstRow += (22 - (len(str(char["lf"])) + len(str(char["maxlf"])) + 1 + len(firstRow))) * " "
            firstRow += "{0}/{1}".format(char["lf"], char["maxlf"])
            firstRow = self.padToSecondLabel(firstRow)
            firstRow += "Power"
            firstRow = self.padToLastValue(firstRow)
            firstRow += "{0}".format(char["power"])
            firstRow = self.padToEnd(firstRow)
            firstRow += "\n"
            sheetMsg += firstRow

            # second row
            secondRow = "| ["
            secondRow += (21 - len(secondRow)) * " "
            secondRow += "]"
            secondRow = self.padToSecondLabel(secondRow)
            secondRow += "Knowledge"
            secondRow = self.padToLastValue(secondRow)
            secondRow += "{0}".format(char["knowledge"])
            secondRow = self.padToEnd(secondRow)
            secondRow += "\n"
            sheetMsg += secondRow

            # third row
            thirdRow = "| AP"
            thirdRow += (22 - (len(str(char["ap"])) + len(str(char["maxap"])) + 1 + len(thirdRow))) * " "
            thirdRow += "{0}/{1}".format(char["ap"], char["maxap"])
            thirdRow = self.padToSecondLabel(thirdRow)
            thirdRow += "Parry"
            thirdRow = self.padToLastValue(thirdRow)
            thirdRow += "{0}".format(char["parry"])
            thirdRow = self.padToEnd(thirdRow)
            thirdRow += "\n"
            sheetMsg += thirdRow

            # fourth row
            fourthRow = "| ["
            fourthRow += (21 - len(fourthRow)) * " "
            fourthRow += "]"
            fourthRow = self.padToSecondLabel(fourthRow)
            fourthRow += "Barrier"
            fourthRow = self.padToLastValue(fourthRow)
            fourthRow += "{0}".format(char["barrier"])
            fourthRow = self.padToEnd(fourthRow)
            fourthRow += "\n"
            sheetMsg += fourthRow

            # fifth row
            fifthRow = "| EX"
            fifthRow += (20 - (len(str(char["ex"])) + len(str(char["maxex"])) + 1 + len(fifthRow))) * " "
            fifthRow += "{0}%/{1}%".format(char["ex"], char["maxex"])
            fifthRow = self.padToSecondLabel(fifthRow)
            fifthRow += "Speed"
            fifthRow = self.padToLastValue(fifthRow)
            fifthRow += "{0}".format(char["speed"])
            fifthRow = self.padToEnd(fifthRow)
            fifthRow += "\n"
            sheetMsg += fifthRow

            # sixth row
            sixthRow = "| ["
            sixthRow += (21 - len(sixthRow)) * " "
            sixthRow += "]"
            sixthRow = self.padToEnd(sixthRow)
            sixthRow += "\n"
            sheetMsg += sixthRow

            # ARTTSSSSS
            sheetMsg += "|===================================ARTS=====================================|\n"


            # Bottom border
            sheetMsg += "/\\" + 74 * "_" + "/\\" + "\n"
            sheetMsg += "\\/" + 74 * " " + "\\/" + "\n"

            self.caller.msg(sheetMsg)


        def padToSecondLabel(self, inString):
            outString = inString + (38 - len(inString)) * " "
            return outString


        def padToLastValue(self, inString):
            outString = inString + (63 - len(inString)) * " "
            return outString


        def padToEnd(self, inString):
            """Pad out to the end of the sheet row"""
            outString = inString + (77 - len(inString))*" "
            outString += "|"
            return outString

        # def sheetRow(self, firstLabel, firstValue, secondLabel, secondValue):
        #     """Format a row of the sheet, providing the sheet the two values that you want to print"""
        #
        #     # 80 characters total per row
        #     rowString = "|"
        #     rowString += 10 * " "
        #     rowString += firstLabel + ": "
        #     rowString += firstValue
        #     rowString += (50-size(rowString)) * " " # pad out to second column
        #
        #     # if we want a second value (i.e. if there are an even number of values in the sheet)
        #     if secondColumn:
        #         rowString += secondLabel+": "
        #         rowString += secondValue
        #
        #     # remember to leave room for the right border
        #     rowString += 79 - size(rowString) * " "
        #     rowString += "|"
        #
        #     return rowString

class CmdSetDesc(default_cmds.MuxCommand):
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
