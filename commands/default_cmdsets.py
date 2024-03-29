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
from evennia import CmdSet

from commands.cmdsets.chargen import CmdStartChargen
from commands.cmdsets.pose import CmdThink, CmdPose, CmdMegaSay, CmdEmit, CmdOOCSay, CmdAside
from commands.cmdsets.charinfo import CmdFinger, CmdSheet, CmdCookieCounter, CmdCookie, CmdOOCFinger, CmdEFinger
from commands.cmdsets.scenes import CmdPot
from commands.cmdsets.mail import CmdMail, CmdMailCharacter
from commands.cmdsets.movement import CmdHome, CmdDitch, CmdSummon, CmdJoin, CmdFollow, CmdWarp, CmdPortal

from commands import command
from commands.default.account import CmdOOC, CmdOOCLook, CmdWho, CmdCharCreate, CmdCharDelete
from commands.cmdsets.combat import CmdRoll, CmdGMRoll, CmdFlip, CmdRollSet, CmdRollSkill, CmdTaunt, CmdPersuade, CmdIntimidate
from commands.cmdsets.roster import CmdShowGroups, CmdSetGroups
from commands.cmdsets.building import CmdLinkTeleport, CmdMakeCity, CmdProtector, CmdSetProtector, CmdClearProtector, CmdCheckQuota, CmdMakePrivateRoom, CmdDestroyPrivateRoom
from commands.cmdsets.building import CmdLockRoom, CmdUnLockRoom, CmdDescInterior
from commands.cmdsets.items import CmdCraft, CmdDescCraft, CmdSetQuota, CmdJunkCraft
from commands.cmdsets.jobs import CmdRequest, CmdCheckJobs
from evennia.contrib.dice import CmdDice
from evennia.contrib import multidescer
from commands.cmdsets.descer import CmdDesc, CmdMultiDesc
from commands.cmdsets.utility import CmdWho, CmdICTime, CmdWarning, CmdHighlight
from commands.cmdsets.movement import CmdEnterCity, CmdLeaveCity
from commands.default.unloggedin import CmdUnconnectedCreate
from commands.default.comms import CmdGrapevine2Chan, CmdIRC2Chan, CmdIRCStatus, CmdRSS2Chan
from commands.default.comms import CmdChannelCreate, CmdCdestroy, CmdCBoot
from commands.cmdsets.bboards import CmdBBCreate, CmdBBRead, CmdBBPost

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
        self.add(CmdAside())
        self.add(CmdOOCSay())
        self.add(CmdFinger())
        self.add(CmdOOCFinger())
        self.add(CmdEFinger())

        #moving around
        self.add(CmdHome())
        self.add(CmdSummon())
        self.add(CmdJoin())
        self.add(CmdFollow())
        self.add(CmdDitch())
        self.add(CmdDesc())
        self.add(CmdEnterCity())
        #self.add(CmdLeaveCity())
        self.add(CmdPortal())

        self.add(CmdMultiDesc())
        self.add(CmdICTime())
        self.add(CmdWarning())

        self.add(CmdProtector())


        self.add(CmdSetGroups())
        self.add(CmdShowGroups())

        #commands related to dice 

        self.add(CmdFlip())
        self.add(CmdGMRoll())
        self.add(CmdRoll())
        self.add(CmdRollSet())
        self.add(CmdRollSkill())
        self.add(CmdIntimidate())
        self.add(CmdTaunt())
        self.add(CmdPersuade())

        self.add(CmdWarp())       
        self.add(CmdPortal())

        #cookie commands will be moved to account level at a later time
        self.add(CmdCookie())
        self.add(CmdCookieCounter())

        self.add(CmdMailCharacter())
        self.add(CmdHighlight())
        #self.add(CmdPot())


        #request and file system
        self.add(CmdRequest())

        #boards
        self.add(CmdBBRead())
        self.add(CmdBBPost())

        #building and crafting
        self.add(CmdCheckQuota())
        self.add(CmdMakePrivateRoom())
        self.add(CmdDestroyPrivateRoom())
        self.add(CmdLockRoom())
        self.add(CmdUnLockRoom())
        self.add(CmdDescInterior())
        self.add(CmdCraft())
        self.add(CmdDescCraft())
        self.add(CmdJunkCraft())

        # any command below this line is only available to staff.

        self.add(CmdLinkTeleport())
        self.add(CmdMakeCity())
        self.add(CmdStartChargen())
        self.add(CmdSetProtector())
        self.add(CmdClearProtector())
        self.add(CmdSetQuota())
        self.add(CmdBBCreate)



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
        self.add(CmdMail())

        self.add(CmdGrapevine2Chan())
        self.add(CmdIRC2Chan())
        self.add(CmdIRCStatus())        
        self.add(CmdRSS2Chan())

        self.add(CmdChannelCreate())
        self.add(CmdCBoot())
        self.add(CmdCdestroy())


        #self.remove(default_cmds.CmdIRC2Chan())
        #self.remove(default_cmds.CmdIrcStatus())
        #self.remove(default_cmds.CmdRSS2Chan())
        #self.remove(default_cmds.CmdGrapevine2Chan())

        self.remove(default_cmds.CmdCharCreate())
        self.remove(default_cmds.CmdCharDelete())
        

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
        
        self.add(CmdUnconnectedCreate())




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
