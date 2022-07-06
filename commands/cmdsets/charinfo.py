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

    To get basic IC profile information about a character.

    Useful for an OOC overview and for potential 
    appers. Information here is a combination of 
    what is known publically as well as what is 
    more general about a character's personality
    and backstory and is more individual to the
    character.

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
        



class CmdOOCFinger(MuxCommand):
    """
    
    +oocfinger <character>

    +oocfinger/discord <Your Discord here>
    +oocfinger/email <Your Email here>
    
    To get basic OOC information which relates to 
    the player of the character. You can find
    personal RP hooks and other preferences
    set here, as well as any OOC contact information
    the player feels comfortable to provide.

    Set with switches such as +oocfinger/altchars
    to add the fields provided to your own OOC finger.
    Fields included:

    Email, Alias, Discord, Altchars, RPTimes,
    Timezone, Voice, Info 

    Info is for free response where you can set RP 
    preferences and hooks or anything you like.
    Timezone should update automatically.
    
    """
    key = "+oocfinger"
    aliases = ["oocfinger","ofinger", "+ofigner", "ofigner", "+oocfigner"]
    lock = "cmd:all()"
    help_category = "General"

    def func(self):
        "This performs the actual command"
        caller = self.caller

    # setting attributes switches
    # first pass
        
        if "email" in self.switches:
            if self.args:
                caller.db.prefemail = self.args
                self.msg("Email set to: %s" % self.args)
            else:
                caller.attributes.remove("prefemail")
                self.msg("Email address cleared.")
            return
        if "discord" in self.switches:
            if self.args:
                caller.db.discord = self.args
                self.msg("Discord set to: %s" % self.args)
            else:
                caller.attributes.remove("discord")
                self.msg("Discord cleared.")
            return
        if "altchars" in self.switches:
            if self.args:
                caller.db.altchars = self.args
                self.msg("AltChars set to: %s" % self.args)
            else:
                caller.attributes.remove("altchars")
                self.msg("Alts cleared.")
            return
        if "rptimes" in self.switches:
            if self.args:
                caller.db.rptimes = self.args
                self.msg("RP Times set to: %s" % self.args)
            else:
                caller.attributes.remove("rptimes")
                self.msg("RP Times cleared.")
            return
        if "voice" in self.switches:
            if self.args:
                caller.db.voice = self.args
                self.msg("Voice set to: %s" % self.args)
            else:
                caller.attributes.remove("voice")
                self.msg("Voice cleared.")
            return
        if "info" in self.switches:
            if self.args:
                caller.db.info = self.args
                self.msg("Info set to: %s" % self.args)
            else:
                caller.attributes.remove("info")
                self.msg("Info cleared.")
            return


        if not self.args:
            player = caller
        else:     
        # find a player in the db who matches this string
            player = caller.search(self.args)

        if not player:
            return
        char = player
        if not char:
            caller.msg("Character not found.")
            return
        try:
            # build the string for ooc finger

            oocfingermsg = f"Name: {char.name} |/" 
            f"Email:  {char.prefemail} |/ Alias: {char.alias} |/"
            f"Discord: {char.discord} |/ Altchars: {char.alts} |/" 
            f"Timezone: {char.timezone} |/ Voice: {char.voice} |/"
            f" Info: |/ {char.info}"
            caller.msg(oocfingermsg)
        except ValueError:
            caller.msg("Some error occured.")
            return
        

'''
Not high priority, but to be converted and added as a stretch feature

class CmdRPHooks(MuxCommand):
    """
    Sets or searches RP hook tags
    Usage:
        +rphooks <character>
        +rphooks/search <tag>
        +rphooks/add <searchable title>[=<optional description>]
        +rphooks/rm <searchable title>
    """

    key = "+rphooks"
    help_category = "Social"
    aliases = ["rphooks"]

    def list_valid_tags(self):
        """Lists the existing tags for rp hooks"""
        tags = Tag.objects.filter(db_category="rp hooks").order_by("db_key")
        self.msg("Categories: %s" % "; ".join(tag.db_key for tag in tags))
        return

    def func(self):
        """Executes the RPHooks command"""
        if not self.switches:
            if not self.args:
                targ = self.caller
            else:
                targ = self.caller.search(self.args)
                if not targ:
                    self.list_valid_tags()
                    return
            hooks = targ.tags.get(category="rp hooks") or []
            hooks = make_iter(hooks)
            hook_descs = targ.db.hook_descs or {}
            table = EvTable("Hook", "Desc", width=78, border="cells")
            for hook in hooks:
                table.add_row(hook, hook_descs.get(hook, ""))
            table.reformat_column(0, width=20)
            table.reformat_column(1, width=58)
            self.msg(table)
            if not hooks:
                self.list_valid_tags()
            return
        if "add" in self.switches:
            title = self.lhs.lower()
            if len(title) > 25:
                self.msg("Title must be under 25 characters.")
                return
            # test characters in title
            if not self.validate_name(title):
                return
            data = self.rhs
            hook_descs = self.caller.db.hook_descs or {}
            self.caller.tags.add(title, category="rp hooks")
            if data:
                hook_descs[title] = data
                self.caller.db.hook_descs = hook_descs
            data_str = (": %s" % data) if data else ""
            self.msg("Added rphook tag: %s%s." % (title, data_str))
            return
        if "search" in self.switches:
            table = EvTable("Name", "RPHook", "Details", width=78, border="cells")
            if not self.args:
                self.list_valid_tags()
                return
            tags = Tag.objects.filter(
                db_key__icontains=self.args, db_category="rp hooks"
            )
            for tag in tags:
                for pc in tag.accountdb_set.all():
                    hook_desc = pc.db.hook_descs or {}
                    desc = hook_desc.get(tag.db_key, "")
                    table.add_row(pc, tag.db_key, desc)
            table.reformat_column(0, width=10)
            table.reformat_column(1, width=20)
            table.reformat_column(2, width=48)
            self.msg(table)
            return
        if "rm" in self.switches or "remove" in self.switches:
            args = self.args.lower()
            hook_descs = self.caller.db.hook_descs or {}
            if args in hook_descs:
                del hook_descs[args]
                if not hook_descs:
                    self.caller.attributes.remove("hook_descs")
                else:
                    self.caller.db.hook_descs = hook_descs
            tagnames = self.caller.tags.get(category="rp hooks") or []
            if args not in tagnames:
                self.msg("No rphook by that category name.")
                return
            self.caller.tags.remove(args, category="rp hooks")
            self.msg("Removed.")
            return
        self.msg("Invalid switch.")

    def validate_name(self, name):
        """Ensures that RPHooks doesn't have a name with special characters that would break it"""
        import re

        if not re.findall("^[\w',]+$", name):
            self.msg("That category name contains invalid characters.")
            return False
        return True

'''

class CmdSoundtrack(BaseCommand):
    '''
    To be added
    '''
    def func(self):
        "This performs the actual command"
        self.caller.msg("Not yet added.")
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
            discern, flow, force, mechanics, medicine, computer, stealth, heist, convince, presence, arcana = self.caller.get_skills()
            line1 = "Name: "
            line2 = "Racetype: Power Types:" 
            line3 = "Current Mode:"            
            line4= "POW: %s, DEX: %s, TEN: %s, CUN: %s, EDU: %s, CHR: %s, AUR: %s"  % (pow, dex, ten, cun, edu, chr, aur)
            line5 = "Discern: %s, Flow: %s, Force: %s, Mechanics: %s, Medicine: %s, Computer: %s, Stealth: %s , Heist: %s , Convince: %s, Presence: %s, Arcana: %s"  % (perception, athletics, force, mechanics, medicine, computer, stealth, larceny, convince, presence, arcana)
            line6 = "Capabilities: "
            line7 =  "Size, Speed"
            line8 = "Elements: Weakness/Resistance:"
            # not sure yet about attack lists, if that will be a thing or not
            sheetmsg = (line1 + "\n" + line2 + "\n" + line3 + "\n" + line4  + "\n" + line5 + "\n" + line6 + "\n" + line7 + "\n" + line8)
            self.caller.msg(sheetmsg)

class CmdCookie(MuxCommand):

    """
    Give a mouse a cookie.
    
    Usage:
      +cookie <player>
    This gives a little cookie to a player that you did RP with.
    The cookie is a vote or 'thank you' for roleplay.
    +vote does the same thing as cookie.
    
    Check cookie board leaders with +100check or +monsters.
    """

    key = "cookie"
    aliases = ["+cookie"]
    locks = "cmd:all()"

    def func(self):
        "This performs the actual command"
        if not self.args:
            self.caller.msg("Give cookie to who?")
            return

class CmdCookieCounter(MuxCommand):

    """
   
    Usage:
        +tally
    See how many cookies you have, and how many cookies
    you have to give out for the rest of the week. 

    """

    key = "tally"
    aliases = ["+tally"]
    locks = "cmd:all()"

    def func(self):
        self.caller.msg("Wow here's how many cookies you have!")



class CmdCookiemonsters(MuxCommand):

    """
    Give a mouse a cookie.
    
    Usage:
      +100check or +monsters

      Shows a leaderboard of PCs with 100 cookies or more.
    """
    key = "100check"
    aliases = ["+100check", "monsters", "+monsters"]
    locks = "cmd:all()"

    def func(self):
        self.caller.msg("Wow here's all the people with 100 cookies!")


