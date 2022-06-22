'''
Some random global commands
'''


from evennia import CmdSet
from six import string_types
from commands.command import BaseCommand
from evennia.commands.default.muxcommand import MuxCommand
from server.utils import sub_old_ansi
from evennia.accounts.models import AccountDB
from commands.cmdsets import places
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import evtable, utils
import time


def prune_sessions(session_list):
    # This function modifies the display of "who" and "+pot" so that, if the same player is connected from multiple
    # devices, their character name is only displayed once to avoid confusion. Admin still see all connected sessions.
    session_accounts = [session.account.key for session in session_list]  # get a list of just the names

    unique_accounts = set(session_accounts)
    positions = []

    for acct in unique_accounts:
        # finds positions of account name matches in the session_accounts list
        account_positions = [i for i, x in enumerate(session_accounts) if x == acct]

        # add the position of the account entry we want to the positions list
        if len(account_positions) != 1:
            positions.append(account_positions[-1])
        else:
            positions.append(account_positions[0])

    positions.sort()  # since set() unorders the initial list and we want to keep a specific printed order
    pruned_sessions = []

    for pos in positions:
        pruned_sessions.append(session_list[pos])

    return pruned_sessions

#who from SCS. for now, this also is aliased to 'where', but that will change later.


class CmdWho(MuxCommand):
    """
    list who is currently online
    Usage:
      who
      doing
      where
    Shows who is currently online. Doing is an alias that limits info
    also for those with all permissions. Modified to allow players to see
    the locations of other players and add a "where" alias.
    """

    key = "who"
    aliases = ["doing", "where"]
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    # Here we have modified "who" to display the locations of players to other players
    # and to add "where" as an alias.
    def func(self):
        """
        Get all connected accounts by polling session.
        """

        account = self.account
        all_sessions = SESSIONS.get_sessions()

        all_sessions = sorted(all_sessions, key=lambda o: o.account.key) # sort sessions by account name
        pruned_sessions = prune_sessions(all_sessions)

        # check if users are admins and should be able to see all users' session data
        if self.cmdstring == "doing":
            show_session_data = False
        else:
           show_session_data = account.check_permstring("Developer") or account.check_permstring(
               "Admins"
           )

        naccounts = SESSIONS.account_count()
        if show_session_data:
            # privileged info
            table = self.styled_table(
                "|wAccount Name",
                "|wOn for",
                "|wIdle",
                "|wPuppeting",
                "|wRoom",
                "|wCmds",
                "|wProtocol",
                "|wHost",
            )
            for session in all_sessions:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                session_account = session.get_account()
                puppet = session.get_puppet()
                location = puppet.location.key if puppet and puppet.location else "None"
                table.add_row(
                    utils.crop(session_account.get_display_name(account), width=25),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(puppet.get_display_name(account) if puppet else "None", width=25),
                    utils.crop(location, width=35),
                    session.cmd_total,
                    session.protocol_key,
                    isinstance(session.address, tuple) and session.address[0] or session.address,
                )
        else:
            # unprivileged
            table = self.styled_table("|wAccount name", "|wOn for", "|wIdle", "|wRoom")
            for session in pruned_sessions:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                session_account = session.get_account()
                puppet = session.get_puppet()
                location = puppet.location.key if puppet and puppet.location else "None"
                table.add_row(
                    utils.crop(session_account.get_display_name(account), width=25),
                    utils.time_format(delta_conn, 0),
                    utils.time_format(delta_cmd, 1),
                    utils.crop(location, width=35),
                )
        is_one = naccounts == 1
        self.msg(
            "|wAccounts:|n\n%s\n%s unique account%s logged in."
            % (table, "One" if is_one else naccounts, "" if is_one else "s")
        )


class CmdWall(MuxCommand):
    """
    @wall
    Usage:
      @wall <message>
    Shouts a message to all connected players.
    This command should be used to send OOC broadcasts,
    while @gemit is used for IC global messages.
    """

    key = "@wall"
    locks = "cmd:perm(wall) or perm(Wizards)"
    help_category = "Admin"

    def func(self):
        """Implements command"""
        if not self.args:
            self.msg("Usage: @wall <message>")
            return
        message = '%s shouts "%s"' % (self.caller.name, self.args)
        self.msg("Announcing to all connected players ...")
        SESSIONS.announce_all(message)

#this is force from arx, but removing the part where it informs a staff channel about it.
#should be an admin only command. But future puppeting may need this permission.

class CmdForce(MuxCommand):
    """
    @force
    Usage:
      @force <character>=<command>
      @force/char <player>=command
    Forces a given character to execute a command. Without the char switch,
    this will search for character objects in your room, which may be npcs
    that have no player object. With the /char switch, this searches for
    the character of a given player name, who may be anywhere.
    """

    key = "@force"
    locks = "cmd:perm(force) or perm(Wizards)"
    help_category = "GMing"

    def func(self):
        """Implements command"""
        caller = self.caller
        if not self.lhs or not self.rhs:
            self.msg("Usage: @force <character>=<command>")
            return
        if "char" in self.switches:
            player = self.caller.player.search(self.lhs)
            if not player:
                return
            char = player.char_ob
        else:
            char = caller.search(self.lhs)
        if not char:
            caller.msg("No character found.")
            return
        if not char.access(caller, "edit"):
            caller.msg("You don't have 'edit' permission for %s." % char)
            return
        char.execute_cmd(self.rhs)
        caller.msg("Forced %s to execute the command '%s'." % (char, self.rhs))

'''
this is staff list command from arx
todo: fix to list all staff 
'''


class CmdListStaff(MuxCommand):
    """
    +staff
    Usage:
        +staff
        +staff/all
        +staff/list
    
    +staff lists staff currently online.
    +staff/all or +staff/list lists all staff and their status.
    """

    key = "+staff"

    locks = "cmd:all()"
    help_category = "Admin"

    def func(self):
        """Implements command"""
        caller = self.caller
        staff = AccountDB.objects.filter(db_is_connected=True, is_staff=True)
        table = evtable.EvTable("{wName{n", "{wRole{n", "{wIdle{n", width=78)
        
        if "all" or "list" in self.switches:
            for ob in staff:
                if ob.tags.get("hidden_staff") or ob.db.hide_from_watch:
                    continue
                timestr = CmdWho.get_idlestr(ob.idle_time)
                obname = CmdWho.format_pname(ob)
                table.add_row(obname, ob.db.staff_role or "", timestr)
            caller.msg("{wStaff:{n\n%s" % table)
        else:
            for ob in staff:
                if ob.tags.get("hidden_staff") or ob.db.hide_from_watch:
                    continue
                timestr = CmdWho.get_idlestr(ob.idle_time)
                obname = CmdWho.format_pname(ob)
                table.add_row(obname, ob.db.staff_role or "", timestr)
            caller.msg("{wOnline staff:{n\n%s" % table)

'''
class CmdXWho(MuxCommand):
    """
    xwho
    Usage:
        xwho
    Factional Who.
    Implimentation on hold until we know what groups are, just making a note of it.
    """

'''