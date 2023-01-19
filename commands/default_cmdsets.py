"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""



from evennia import default_cmds

from commands.cmdsets.chargen import CmdStartChargen
from commands.cmdsets.pose import CmdThink, CmdPose, CmdMegaSay, CmdEmit, CmdOOCSay
from commands.cmdsets.charinfo import CmdFinger, CmdSheet, CmdCookieCounter, CmdCookie
from commands.cmdsets.charinfo import CmdOOCFinger
from commands.cmdsets.charinfo import CmdEFinger
from commands.cmdsets.movement import CmdHome, CmdDitch, CmdSummon, CmdJoin, CmdFollow, CmdWarp, CmdPortal
from evennia import CmdSet
from commands import command
from commands.default.account import CmdOOC, CmdOOCLook, CmdWho
from commands.cmdsets.combat import CmdRoll, CmdGMRoll, CmdFlip, CmdRollSet, CmdRollSkill, CmdTaunt, CmdPersuade, CmdIntimidate

from commands.cmdsets.building import CmdLinkTeleport, CmdMakeCity
from evennia.contrib.dice import CmdDice
from evennia.contrib import multidescer
from commands.cmdsets.descer import CmdDesc
from commands.cmdsets.utility import CmdWho, CmdICTime
from commands.cmdsets.movement import CmdEnterCity, CmdLeaveCity
#from commands.cmdsets.bboards import CmdBBCreate, CmdBBNew, CmdBBReadOrPost, CmdBBSub, CmdBBUnsub, CmdGetUnreadPosts

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.

        # use @typeclass/force self to reset yourself after adding new commands.
        #
        self.add(CmdSheet())
        self.add(CmdThink())
        self.add(CmdDice())
        self.add(CmdPose())
        self.add(CmdMegaSay())
        self.add(CmdEmit())
        self.add(CmdOOCSay())
        self.add(CmdFinger())
        self.add(CmdOOCFinger())
        self.add(CmdEFinger())

        self.add(CmdHome())
        self.add(CmdSummon())
        self.add(CmdJoin())
        self.add(CmdFollow())
        self.add(CmdDitch())
        self.add(CmdDesc())
        self.add(CmdEnterCity())
        self.add(CmdLeaveCity())

        self.add(CmdPortal())
        self.add(CmdICTime())

        #commands related to dice 

        self.add(CmdFlip())
        self.add(CmdGMRoll())
        self.add(CmdRoll())
        self.add(CmdRollSet())
        self.add(CmdRollSkill())
        self.add(CmdIntimidate())
        self.add(CmdTaunt())
        self.add(CmdPersuade())



        #cookie commands will be moved to account level at a later time
        self.add(CmdCookie())
        self.add(CmdCookieCounter())

        #self.add(multidescer.CmdMultiDesc()) 
        #do not use this multidescer, it over-writes descing rooms and makes me cry. totally redo it.

        # in the future, any command below this line will be staff only.
        self.add(CmdWarp())       
        self.add(CmdPortal())
        self.add(CmdLinkTeleport())
        self.add(CmdMakeCity())
        self.add(CmdStartChargen())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #

        self.add(CmdWho())
        self.add(CmdOOCLook())
        self.add(CmdOOC())

        '''
        bboard commands do not work yet.
        self.add(CmdBBCreate())
        self.add(CmdBBUnsub())
        self.add(CmdBBSub())
        self.add(CmdBBReadOrPost())
        self.add(CmdBBNew())
        '''



class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #



class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As an example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #



class GMCmdSet(default_cmds.CharacterCmdSet):
    """
    These are commands that will belong to GMs and
    be temporarily set on GMs.
    """

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class WizardCmdSet(default_cmds.CharacterCmdSet):
    """
    These are commands that will belong to staffers only, being 
    set by wizards.

    Empty for now during the testing phase. Everything is on
    character. Later on this will be full of stuff from
    above.
    """

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
