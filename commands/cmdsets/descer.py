"""
Better multidescer to match the old multidescer.

"""


from evennia.contrib import multidescer 
from evennia.objects.models import ObjectDB
from evennia import default_cmds
from evennia.commands.default.muxcommand import MuxCommand
from server.utils import sub_old_ansi

#permissions on desc are strange. 
#todo, allow PCs to desc themselves, but not rooms.

class CmdDesc(MuxCommand):
    """
    describe an object or the current room.

    Usage:
      desc [<obj> =] <description>

    Sets the "desc" attribute on an object. If an object is not given,
    describe the current room.
    """

    key = "desc"
    aliases = "describe", "@desc"
    locks = "cmd:perm(desc) or perm(Builder)"
    help_category = "Building"


    def func(self):
        """Define command"""

        caller = self.caller
        if not self.args:
            caller.msg("Usage: desc [<obj> =] <description>")
            return


        if "=" in self.args:
            # We have an =
            obj = caller.search(self.lhs)
            if not obj:
                return
            desc = self.rhs or ""
        else:
            obj = caller.location or self.msg("|rYou can't describe oblivion.|n")
            if not obj:
                return
            desc = self.args
            desc = sub_old_ansi(desc)
        if obj.access(self.caller, "control") or obj.access(self.caller, "edit"):
            obj.db.desc = sub_old_ansi(desc)
            caller.msg("The new description was set on %s." % obj.get_display_name(caller))
        else:
            caller.msg("You don't have permission to edit the description of %s." % obj.key)


class CmdMultiDesc(MuxCommand):
    """
    +multidesc = <text of desc>
    +mdesc = <text of desc>
    +multidesc/store <name>
    +multidesc/wear <name>
    +multidesc/view <name>
    +multidesc/list
    
    Use the multidescer to describe yourself. 
    Multidesc, by itself, lists your current descs, or use +mutidesc/list
    for the same functionality.

    +multidesc/store stores your current desc under the name you
    have provided.

    +multidesc/wear will put on a desc you've already stored.

    +multidesc/view shows the desc before you wear it.

    +mdesc is an alias for +multidesc and does the same thing.

    this doesn't work yet I'm just typing out this stuff.

    """

    key = "multidesc"
    aliases = "+multidesc, mdesc, +mdesc"
    switch_options = ("list","store","wear","view")
    help_category = "Building"

    def func(self):
        """Define command"""

        caller = self.caller
        if not self.args and "edit" not in self.switches:
            caller.msg("Usage: desc [<obj> =] <description>")
            return

        if "list" in self.switches:
            
            return

        if "store" in self.switches:
            
            return

        if "wear" in self.switches:
            
            return

        if "view" in self.switches:
            
            return

        if "=" in self.args:
            # We have an =
            obj = caller.search(self.lhs)
            if not obj:
                return
            desc = self.rhs or ""
        else:
            obj = caller.location or self.msg("|rYou can't describe oblivion.|n")
            if not obj:
                return
            desc = self.args
            desc = sub_old_ansi(desc)
        if obj.access(self.caller, "control") or obj.access(self.caller, "edit"):
            obj.db.desc = desc
            caller.msg("The description was set on %s." % obj.get_display_name(caller))
        else:
            caller.msg("You don't have permission to edit the description of %s." % obj.key)
