"""
Pose-related and Pose Order Tracking commands will live here

"""

from evennia import CmdSet
from commands.command import BaseCommand
from evennia.commands.default.muxcommand import MuxCommand, MuxAccountCommand
from server.utils import sub_old_ansi
from evennia.commands.default.general import CmdSay
from evennia.commands.default.account import CmdOOC


class CmdThink(BaseCommand):
    """
    This is just for thinking out loud.
    """
    key = "think"
    lock = "cmd:all()"
    help_category = "General"

    def func(self):
        "This performs the actual command"
        errmsg = "You can't think of anything."
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            message = self.args
            message = sub_old_ansi(message)
            self.caller.msg(f"You think:{str(message)}")
        except ValueError:
            self.caller.msg(errmsg)
            return
        


'''
These are Arx's emit and pose commands with some modification to start.
I'm commenting out irrelevant stuff to test basics.

Emit is basic and uncapped and unlocked and will require more locks
at a later time to do things like nospoof. Just making it work for
right now.

'''

class CmdOOCSay(MuxCommand):
    """
    ooc

    Usage:
      ooc <message>

    Send an OOC message to your current location. For IC messages,
    use 'say' instead.
    """

    key = "ooc"
    locks = "cmd:all()"
    help_category = "Comms"

    def func(self):
        """Run the OOCsay command"""

        caller = self.caller
        speech = self.raw.lstrip()

        if not speech:
            caller.msg(
                "No message specified. If you wish to stop being IC, use @ooc instead."
            )
            return

        oocpose = False
        nospace = False
        if speech.startswith(";") or speech.startswith(":"):
            oocpose = True
            if speech.startswith(";"):
                nospace = True
            speech = speech[1:]

        # calling the speech hook on the location
        speech = caller.location.at_say(speech)
        options = {"ooc_note": True, "log_msg": True}

        # Feedback for the object doing the talking.
        if not oocpose:
            caller.msg("(OOC) You say: %s" % speech)

            # Build the string to emit to neighbors.
            emit_string = "(OOC) %s says: %s" % (caller.name, speech)
            caller.location.msg_contents(
                emit_string, from_obj=caller, exclude=caller, options=options
            )
        else:
            if nospace:
                emit_string = "(OOC) %s %s" % (caller.name, speech)
            else:
                emit_string = "(OOC) %s %s" % (caller.name, speech)
            caller.location.msg_contents(
                emit_string, exclude=None, options=options, from_obj=caller
            )


class CmdEmit(MuxCommand):
    """
    @emit

    Usage:
      @emit[/switches] [<obj>, <obj>, ... =] <message>
      @pemit           [<obj>, <obj>, ... =] <message>

    Switches:
      room : limit emits to rooms only (default)
      players : limit emits to players only
      contents : send to the contents of matched objects too
      stories : send to all current GM events

    Emits a message to the selected objects or to
    your immediate surroundings. If the object is a room,
    send to its contents. @pemit is an emit directly
    to another player.

    For now, no event or room-level emits.
    """

    key = "@emit"
    aliases = ["@pemit", "\\\\"]
    locks = "cmd:all()"
    help_category = "Social"
    perm_for_switches = "Builders"
    arg_regex = None

    def get_help(self, caller, cmdset):
        """Returns custom help file based on caller"""
        if caller.check_permstring(self.perm_for_switches):
            return self.__doc__
        help_string = """
        @emit

        Usage :
            @emit <message>

        Emits a message to your immediate surroundings. This command is
        used to provide more flexibility than the structure of poses, but
        please remember to indicate your character's name.
        """
        return help_string

    def func(self):
        """Implement the command"""

        caller = self.caller
        if caller.check_permstring(self.perm_for_switches):
            args = self.args
        else:
            args = self.raw.lstrip(" ")

        if not args:
            string = "Usage: "
            string += "\n@emit[/switches] [<obj>, <obj>, ... =] <message>"
            string += "\n@pemit           [<obj>, <obj>, ... =] <message>"
            caller.msg(string)
            return

        players_only = "players" in self.switches
        send_to_contents = "contents" in self.switches
        perm = self.perm_for_switches
        normal_emit = False
        has_perms = caller.check_permstring(perm)

        # we check which command was used to force the switches
        cmdstring = self.cmdstring.lstrip("@").lstrip("+")

        if cmdstring == "pemit":
            players_only = True
        

        if not caller.check_permstring(perm):
            rooms_only = False
            players_only = False

        if not self.rhs or not has_perms:
            message = args
            normal_emit = True
            objnames = []
            do_global = False
        else:
            do_global = True
            message = self.rhs
            if caller.check_permstring(perm):
                objnames = self.lhslist
            else:
                objnames = [x.key for x in caller.location.contents if x.player]
        if do_global:
            do_global = has_perms

            '''

            Don't think we need event functionality, but here it lives

        if events_only:
            from datetime import datetime

            events = RPEvent.objects.filter(
                finished=False, gm_event=True, date__lte=datetime.now()
            )
            for event in events:
                obj = event.location
                if not obj:
                    continue
                obj.msg_contents(
                    message, from_obj=caller, kwargs={"options": {"is_pose": True}}
                )
                caller.msg("Emitted to event %s and contents:\n%s" % (event, message))
            return
            '''
            
        # normal emits by players are just sent to the room
        # right now this does not do anything with nospoof. add later in POT functionality.

        if normal_emit:      
            try:
                message = self.args
                message = sub_old_ansi(message)
                self.caller.location.msg_contents(message)
            except ValueError:
                self.caller.msg("Error: no emit.")
                return
        
            return
            
        # send to all objects
        '''
        for objname in objnames:
            if players_only:
                obj = caller.player.search(objname)
                if obj:
                    obj = obj.character
            else:
                obj = caller.search(objname, global_search=do_global)
            if not obj:
                caller.msg("Could not find %s." % objname)
                continue
            if rooms_only and obj.location:
                caller.msg("%s is not a room. Ignored." % objname)
                continue
            if players_only and not obj.player:
                caller.msg("%s has no active player. Ignored." % objname)
                continue
            if obj.access(caller, "tell"):
                if obj.check_permstring(perm):
                    bmessage = "{w[Emit by: {c%s{w]{n %s" % (caller.name, message)
                    obj.msg(bmessage, options={"is_pose": True})
                else:
                    obj.msg(message, options={"is_pose": True})
                if send_to_contents and hasattr(obj, "msg_contents"):
                    obj.msg_contents(
                        message, from_obj=caller, kwargs={"options": {"is_pose": True}}
                    )
                    caller.msg("Emitted to %s and contents:\n%s" % (objname, message))
                elif caller.check_permstring(perm):
                    caller.msg("Emitted to %s:\n%s" % (objname, message))
            else:
                caller.msg("You are not allowed to emit to %s." % objname)
                '''


class CmdPose(BaseCommand):
    """
    pose - strike a pose

    Usage:
      pose <pose text>
      pose's <pose text>

    Describe an action being taken. The pose text will
    automatically begin with your name. Following pose with an apostrophe,
    comma, or colon will not put a space between your name and the character.
    Ex: 'pose, text' is 'Yourname, text'. Similarly, using the ; alias will
    not append a space after your name. Ex: ';'s adverb' is 'Name's adverb'.

    """

    key = "pose"
    aliases = [":", "emote", ";"]
    locks = "cmd:all()"
    help_category = "Social"
    arg_regex = None

    # noinspection PyAttributeOutsideInit
    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        super(CmdPose, self).parse()
        args = self.args
        if (args and not args[0] in ["'", ",", ":"]) and not self.cmdstring.startswith(
            ";"
        ):
            args = " %s" % args.lstrip(" ")
        self.args = args

    def func(self):

        "This performs the actual command"
        errmsg = "Pose what?"
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            message = self.args
            message = sub_old_ansi(message)
            self.caller.location.msg_action(
            self.caller, message
        )
        except ValueError:
            self.caller.msg(errmsg)
            return
        


class CmdMegaSay(CmdSay):
    """
    Override of CmdSay

    We don't do other languages, so don't need that functionality
    Eventually over-ride this so autosay won't fire in IC rooms,
    as a treat.
    
    """

    __doc__ = CmdSay.__doc__
    arg_regex = None

    # noinspection PyAttributeOutsideInit
    def parse(self):
        """Make sure cmdstring 'say' has a space, other aliases don't"""
        super(CmdMegaSay, self).parse()
        if self.cmdstring == "say":
            self.args = " %s" % self.args.lstrip()

    def func(self):
        """Replacement for CmdSay's func"""
        if not self.raw:
            self.msg("Say what?")
            return
        options = {"is_pose": True}
        speech = self.raw.lstrip(" ")
        # calling the speech hook on the location
        speech = self.caller.location.at_say(speech)
        # Feedback for the object doing the talking.
        langstring = ""
        
        # Build the string to emit to neighbors.
        pre_name_emit_string = ' says%s, "%s"' % (langstring, speech)
        self.caller.location.msg_action(
            self.caller, pre_name_emit_string, options=options
        )
