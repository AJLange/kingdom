'''
Some random global commands
'''


from evennia import CmdSet
from six import string_types
from commands.command import BaseCommand
from evennia.commands.default.muxcommand import MuxCommand
from server.utils import sub_old_ansi

from commands.cmdsets import places
from evennia.server.sessionhandler import SESSIONS

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
these are who and staff list commands from arx, currently not working
due to dependencies, but wil be fixed to work at a later time.


class CmdWho(MuxCommand):
    """
    who
    Usage:
      who [<filter>]
      doing [<filter>]
      who/sparse [<filter>]
      doing/sparse [<filter>]
      who/active
      who/watch
      who/org <organization>
    Shows who is currently online. Doing is an alias that limits info
    also for those with all permissions. Players who are currently
    looking for scenes show up with the (LRP) flag, which can be
    toggled with the @settings command. If a filter is supplied, it
    will match names that start with it.
    """

    key = "who"
    aliases = ["doing", "+who"]
    locks = "cmd:all()"

    @staticmethod
    def format_pname(player, lname=False, sparse=False):
        """
        Returns name of player with flags
        """
        base = player.name.capitalize()
        if lname and not sparse:
            char = player.char_ob
            if char:
                base = char.item_data.longname or base
        if player.db.afk:
            base += " {w(AFK){n"
        if player.db.lookingforrp:
            base += " {w(LRP){n"
        if player.is_staff:
            base += " {c(Staff){n"
        return base

    def check_filters(self, pname, base, fealty=""):
        """
        If we have no filters or the name starts with the
        filter or matches a flag, we return True. Otherwise
        we return False.
        """
        if "org" in self.switches:
            return True
        if not self.args:
            return True
        if self.args.lower() == "afk":
            return "(AFK)" in pname
        if self.args.lower() == "lrp":
            return "(LRP)" in pname
        if self.args.lower() == "staff":
            return "(Staff)" in pname
        if self.args.lower() == str(fealty).lower():
            return True
        return base.lower().startswith(self.args.lower())

    @staticmethod
    def get_idlestr(idle_time):
        """Returns a string that vaguely says how idle someone is"""
        if idle_time is None:
            return "N/A"
        if idle_time < 1200:
            return "No"
        if idle_time < 3600:
            return "Idle-"
        if idle_time < 86400:
            return "Idle"
        return "Idle+"

    def func(self):
        """
        Get all connected players by polling session.
        """
        player = self.caller
        session_list = [
            ob
            for ob in SESSIONS.get_sessions()
            if ob.account and ob.account.show_online(player)
        ]
        session_list = sorted(session_list, key=lambda o: o.account.key.lower())
        sparse = "sparse" in self.switches
        watch_list = player.db.watching or []
        if self.cmdstring == "doing":
            show_session_data = False
        else:
            show_session_data = player.check_permstring(
                "Immortals"
            ) or player.check_permstring("Wizards")
        total_players = len(set(ob.account for ob in session_list))
        number_displayed = 0
        already_counted = []
        public_members = []
        if "org" in self.switches:
            from world.dominion.models import Organization

            try:
                org = Organization.objects.get(name__iexact=self.args)
                if org.secret:
                    raise Organization.DoesNotExist
            except Organization.DoesNotExist:
                self.msg("Organization not found.")
                return
            public_members = [
                ob.player.player
                for ob in org.members.filter(deguilded=False, secret=False)
            ]
        if show_session_data:
            table = prettytable.PrettyTable(
                ["{wPlayer Name", "{wOn for", "{wIdle", "{wRoom", "{wClient", "{wHost"]
            )
            for session in session_list:
                pc = session.get_account()
                if pc in already_counted:
                    continue
                if not session.logged_in:
                    already_counted.append(pc)
                    continue
                delta_cmd = pc.idle_time
                if "active" in self.switches and delta_cmd > 1200:
                    already_counted.append(pc)
                    continue
                if "org" in self.switches and pc not in public_members:
                    continue
                delta_conn = time.time() - session.conn_time
                plr_pobject = session.get_puppet()
                plr_pobject = plr_pobject or pc
                base = str(session.get_account())
                pname = self.format_pname(session.get_account())
                char = pc.char_ob
                if "watch" in self.switches and char not in watch_list:
                    already_counted.append(pc)
                    continue
                if not char or not char.item_data.fealty:
                    fealty = "---"
                else:
                    fealty = char.item_data.fealty
                if not self.check_filters(pname, base, fealty):
                    already_counted.append(pc)
                    continue
                pname = crop(pname, width=18)
                if (
                    session.protocol_key == "websocket"
                    or "ajax" in session.protocol_key
                ):
                    client_name = "Webclient"
                else:
                    # Get a sane client name to display.
                    client_name = session.protocol_flags.get("CLIENTNAME")
                    if not client_name:
                        client_name = session.protocol_flags.get("TERM")
                    if client_name and client_name.upper().endswith("-256COLOR"):
                        client_name = client_name[:-9]

                if client_name is None:
                    client_name = "Unknown"

                client_name = client_name.capitalize()

                table.add_row(
                    [
                        pname,
                        time_format(delta_conn)[:6],
                        time_format(delta_cmd, 1),
                        hasattr(plr_pobject, "location")
                        and plr_pobject.location
                        and plr_pobject.location.dbref
                        or "None",
                        client_name[:9],
                        isinstance(session.address, tuple)
                        and session.address[0]
                        or session.address,
                    ]
                )
                already_counted.append(pc)
                number_displayed += 1
        else:
            if not sparse:
                table = prettytable.PrettyTable(["{wPlayer name", "{wFealty", "{wIdle"])
            else:
                table = prettytable.PrettyTable(["{wPlayer name", "{wIdle"])

            for session in session_list:
                pc = session.get_account()
                if pc in already_counted:
                    continue
                if not session.logged_in:
                    already_counted.append(pc)
                    continue
                if "org" in self.switches and pc not in public_members:
                    continue
                delta_cmd = pc.idle_time
                if "active" in self.switches and delta_cmd > 1200:
                    already_counted.append(pc)
                    continue
                if not pc.db.hide_from_watch:
                    base = str(pc)
                    pname = self.format_pname(pc, lname=True, sparse=sparse)
                    char = pc.char_ob
                    if "watch" in self.switches and char not in watch_list:
                        already_counted.append(pc)
                        continue
                    if not char or not char.item_data.fealty:
                        fealty = "---"
                    else:
                        fealty = str(char.item_data.fealty)
                    if not self.check_filters(pname, base, fealty):
                        already_counted.append(pc)
                        continue
                    idlestr = self.get_idlestr(delta_cmd)
                    if sparse:
                        width = 30
                    else:
                        width = 55
                    pname = crop(pname, width=width)
                    if not sparse:
                        table.add_row([pname, fealty, idlestr])
                    else:
                        table.add_row([pname, idlestr])
                    already_counted.append(pc)
                    number_displayed += 1
                else:
                    already_counted.append(pc)
        is_one = number_displayed == 1
        if number_displayed == total_players:
            string = "{wPlayers:{n\n%s\n%s unique account%s logged in." % (
                table,
                "One" if is_one else number_displayed,
                "" if is_one else "s",
            )
        else:
            string = (
                "{wPlayers:{n\n%s\nShowing %s out of %s unique account%s logged in."
                % (
                    table,
                    "1" if is_one else number_displayed,
                    total_players,
                    "" if total_players == 1 else "s",
                )
            )
        self.msg(string)



class CmdListStaff(MuxCommand):
    """
    +staff
    Usage:
        +staff
        +staff/all
    
    +staff lists staff currently online.
    +staff/all lists all staff and their status.
    """

    key = "+staff"

    locks = "cmd:all()"
    help_category = "Admin"

    def func(self):
        """Implements command"""
        caller = self.caller
        staff = AccountDB.objects.filter(db_is_connected=True, is_staff=True)
        table = evtable.EvTable("{wName{n", "{wRole{n", "{wIdle{n", width=78)
        for ob in staff:
            from .overrides import CmdWho

            if ob.tags.get("hidden_staff") or ob.db.hide_from_watch:
                continue
            timestr = CmdWho.get_idlestr(ob.idle_time)
            obname = CmdWho.format_pname(ob)
            table.add_row(obname, ob.db.staff_role or "", timestr)
        caller.msg("{wOnline staff:{n\n%s" % table)

class CmdXWho(MuxCommand):
    """
    xwho
    Usage:
        +staff
    Lists staff that are currently online.
    """

   

'''