"""
Better multidescer to match the old multidescer.

"""


from evennia import CmdSet
from evennia.contrib import multidescer 
from evennia.objects.models import ObjectDB
from evennia import CmdSet
from evennia import default_cmds


class CmdDesc(default_cmds.CharacterCmdSet):
    """
    describe an object or the current room.

    Usage:
      desc [<obj> =] <description>

    Switches:
      edit - Open up a line editor for more advanced editing.

    Sets the "desc" attribute on an object. If an object is not given,
    describe the current room.
    """

    key = "desc"
    aliases = "describe"
    switch_options = ("edit",)
    locks = "cmd:perm(desc) or perm(Builder)"
    help_category = "Building"

    def edit_handler(self):
        if self.rhs:
            self.msg("|rYou may specify a value, or use the edit switch, " "but not both.|n")
            return
        if self.args:
            obj = self.caller.search(self.args)
        else:
            obj = self.caller.location or self.msg("|rYou can't describe oblivion.|n")
        if not obj:
            return

        if not (obj.access(self.caller, "control") or obj.access(self.caller, "edit")):
            self.caller.msg("You don't have permission to edit the description of %s." % obj.key)

        self.caller.db.evmenu_target = obj
        # launch the editor
        EvEditor(
            self.caller,
            loadfunc=_desc_load,
            savefunc=_desc_save,
            quitfunc=_desc_quit,
            key="desc",
            persistent=True,
        )
        return

    def func(self):
        """Define command"""

        caller = self.caller
        if not self.args and "edit" not in self.switches:
            caller.msg("Usage: desc [<obj> =] <description>")
            return

        if "edit" in self.switches:
            self.edit_handler()
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
        if obj.access(self.caller, "control") or obj.access(self.caller, "edit"):
            obj.db.desc = desc
            caller.msg("The description was set on %s." % obj.get_display_name(caller))
        else:
            caller.msg("You don't have permission to edit the description of %s." % obj.key)
