"""
commands related to groups and rosters
"""



from evennia import CmdSet
from evennia import Command

class CmdSetGroups(Command):
    """
    Adding a character to a particular group

    This is just stubbed out.

    Usage:
      +addgroup <person>=<group>

    """
    
    key = "+addgroup"
    help_category = "roster"

    def func(self):
        "This performs the actual command"
        errmsg = "What text?"
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            text = self.args
        except ValueError:
            self.caller.msg(errmsg)
            return
        self.caller.db.quote = text
        self.caller.msg("Add the character to the group: %i" % text)

# to do above, make it a proper list you can add to


class CmdSetXWho(Command):

    """
    Full Who By Group
    Stubbed out only.

    Usage:
      xwho

    """
    
    key = "xwho"
    help_category = "roster"

    def func(self):
        
        self.caller.msg("Get Character List by Group")




class CmdSetWho(Command):

    """
    Full Who formatted nicely.
    Stubbed out only.

    Usage:
      who

    """
    
    key = "who"
    help_category = "roster"

    def func(self):
        
        self.caller.msg("Get Character List by Group")


"""


Syntax: who, +who                                                             
        who<Name, Letters>                                                    
        who <Faction>                                                         


        The 'who' command lists everyone online, their alias, the abbreviaton 
of the faction they're a part of, idle time, connect time, and function.      
        The who<Letters> will display only those online with the letters      
given; such as 'whot' would display everyone whose name starts with T.        
        The who <Faction> command will list only those on within that faction.
(Ex. who R, who W)                                                



"""


class CmdWho(default_cmds.MuxCommand):
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
