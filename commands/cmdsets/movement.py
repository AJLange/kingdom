"""
All the stuff related to moving around the grid, such as 
teleport (override), follow, summon, are here.

"""


from evennia.objects.models import ObjectDB
from evennia.commands.default.building import CmdTeleport
from evennia.utils.evmenu import get_input
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.rooms import PlayRoom



class CmdSummon(MuxCommand):
    """
    summon

    Usage:
        +summon <person>

    Summons a person to your location. 
    A summon invite can be turned down by choosing
    the option to deny.

    """

    key = "+summon"
    aliases = ["summon", "+port", "port"]
    locks = "cmd:all()"
    help_category = "Travel"


    def func(self):
        """ Functionality for this mechanism. """
        caller = self.caller        
        args = self.args
        if not args:
            caller.msg("Summon who?")
            return

        port_targ = self.caller.search(self.args)
        if not port_targ:
            caller.msg("Can't find that player.")
            return
        try:
            #get confirmation first
            port_targ.msg(f"{caller} is trying to teleport to your location. Is this OK? Type accept to agree, deny to deny summon.")
            agreedeny = yield("Accept or Deny?")
            get_input(port_targ, agreedeny)
            if agreedeny.startswith('d'):
                port_targ.msg("Teleport denied.")
                caller.msg("Teleport was denied.")
                return
            elif agreedeny.startswith('a'):
                destination = caller.search(args, global_search=True)
                if not destination:
                    caller.msg("Destination not found.")
                    return
                if destination:
                    if not isinstance(destination, PlayRoom):
                        caller.msg("Destination is not a room.")
                    return
            else:
                caller.move_to(destination)
                caller.msg("Teleported to %s." % destination)

                return
        except:
            caller.msg("Error.")



class CmdJoin(MuxCommand):
    """
    Join

    Usage:
        +join <person>

    Summons a person to your location. 
    A summon invite can be turned down with 
    +summon deny. +port and +summon have the 
    same functionality.
    """

    key = "+join"
    aliases = ["join"]
    locks = "cmd:all()"
    help_category = "Travel"

    def agreedeny(caller, result):
        if result.lower() in ("agree", "a", "deny", "d"):
            return result
        else:
            caller.msg("Please answer if you agree or deny the teleport. ")
            return True

    def func(self):
        """ Functionality for this mechanism. """
        caller = self.caller
        args = self.args
        if not args:
            caller.msg("Join who?")
            return

        port_targ = self.caller.search(self.args)
        if not port_targ:
            caller.msg("Can't find that player.")
            return
        try:
            #get confirmation first
            port_targ.msg(f"{caller} is trying to teleport to your location. Is this OK? Type accept to agree, deny to deny summon.")
            agreedeny = yield("Accept or Deny?")
            get_input(port_targ, agreedeny)
            if agreedeny.startswith('d'):
                port_targ.msg("Teleport denied.")
                caller.msg("Teleport was denied.")
                return
            elif agreedeny.startswith('a'):
                destination = caller.search(args, global_search=True)
                if not destination:
                    caller.msg("Destination not found.")
                    return
                if destination:
                    if not isinstance(destination, PlayRoom):
                        caller.msg("Destination is not a room.")
                    return
            else:
                caller.move_to(destination)
                caller.msg("Teleported to %s." % destination)

                return

        except:
            caller.msg("Error.")


class CmdFollow(MuxCommand):
    """
    follow

    Usage:
        follow

    Starts following the chosen object. Use follow without
    any arguments to stop following. While following a player,
    you can follow them through locked doors they can open.

    To stop someone from following you, use 'ditch'.
    """

    key = "follow"
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        """Handles followin'"""
        caller = self.caller
        args = self.args
        f_targ = caller.ndb.following
        if not args and f_targ:
            caller.stop_follow()
            return
        if not args:
            caller.msg("You are not following anyone.")
            return
        f_targ = caller.search(args)
        if not f_targ:
            caller.msg("No one to follow.")
            return
        caller.follow(f_targ)


class CmdDitch(MuxCommand):
    """
    ditch

    Usage:
        ditch
        ditch <list of followers>

    Shakes off someone following you. Players can follow you through
    any locked door you have access to.
    """

    key = "ditch"
    locks = "cmd:all()"
    aliases = ["lose"]
    help_category = "Travel"

    def func(self):
        """Handles followin'"""
        caller = self.caller
        args = self.args
        followers = caller.ndb.followers
        if not followers:
            caller.msg("No one is following you.")
            return
        if args:
            matches = []
            for arg in self.lhslist:
                obj = ObjectDB.objects.object_search(
                    arg, exact=False, candidates=caller.ndb.followers
                )
                if obj:
                    matches.append(obj[0])
                else:
                    AT_SEARCH_RESULT(obj, caller, arg)
            for match in matches:
                match.stop_follow()
            return
        # no args, so make everyone stop following
        if followers:
            for follower in followers:
                follower.stop_follow()
        caller.ndb.followers = []
        return



'''
Arx stuff to examine in more detail later:
'''


class CmdKeyring(MuxCommand):
    """
    Checks keys
    Usage:
        +keyring
        +keyring/remove <chest or room>

    Checks your keys, or Removes a key.
    """

    key = "+keyring"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Executes keyring command"""
        caller = self.caller

        if "remove" in self.switches:
            removed = caller.item_data.remove_key_by_name(self.args.lower())
            if removed:
                self.msg("Removed %s." % ", ".join(ob.key for ob in removed))
        key_list = caller.held_keys.all()
        caller.msg("Keys: %s" % ", ".join(str(ob) for ob in key_list))

class CmdLockObject(MuxCommand):
    """
    Locks or unlocks an exit or container

    Usage:
        lock <object>
        unlock <object>

    Locks or unlocks an object for which you have a key.
    """

    key = "+lock"
    aliases = ["lock", "unlock", "+unlock"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Executes lock/unlock command"""
        caller = self.caller
        verb = self.cmdstring.lstrip("+")
        obj = caller.search(self.args)
        if not obj:
            return
        if hasattr(obj, "lock_exit"):
            if verb == "lock":
                obj.lock_exit(caller)
            else:
                obj.unlock_exit(caller)
            return
        try:
            lock_method = getattr(obj, verb)
            lock_method(caller)
        except AttributeError:
            self.msg("You cannot %s %s." % (verb, obj))
            return


class CmdTidyUp(MuxCommand):
    """
    Removes idle characters from the room

    Usage:
        +tidy

    This removes any character who has been idle for at least
    one hour in your current room, provided that the room is
    public or a room you own.
    """

    key = "+tidy"
    aliases = ["+gohomeyouredrunk"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Executes tidy command"""
        caller = self.caller
        loc = caller.location
        if "private" in loc.tags.all() and not caller.check_permstring("builders"):
            owners = loc.db.owners or []
            if caller not in owners:
                self.msg("This is a private room.")
                return
        from typeclasses.characters import Character

        # can only boot Player Characters
        chars = Character.objects.filter(db_location=loc, roster__roster__name="Active")
        found = []
        for char in chars:
            time = char.idle_time
            player = char.player
            # no sessions connected, character that somehow became headless, such as server crash
            if not player or not player.is_connected or not player.sessions.all():
                char.at_post_unpuppet(player)
                found.append(char)
                continue
            if time > 3600:
                player.unpuppet_all()
                found.append(char)
        if not found:
            self.msg("No characters were found to be idle.")
        else:
            self.msg(
                "The following characters were removed: %s"
                % ", ".join(ob.name for ob in found)
            )



class CmdWarp(MuxCommand):
    """
    teleport to another location
    Usage:
      warp <target location>
    Examples:
      warp granse - zerhem kingdom
    """

    key = "warp"
    aliases = "+warp"
    locks = "cmd:all()"

    # This is a copy-paste of @tel (or teleport) with reduced functions. @tel is an admin
    # command that takes objects as args, allowing you to teleport objects to places.
    # Warp only allows you to teleport yourself. I chose to make a new command rather than
    # expand on @tel with different permission sets because the docstring/help file is
    # expansive for @tel, as it has many switches in its admin version.
    def func(self):
        """Performs the teleport"""

        caller = self.caller
        args = self.args

        destination = caller.search(args, global_search=True)
        if not destination:
            caller.msg("Destination not found.")
            return
        if destination:
            if not isinstance(destination, PlayRoom):
                caller.msg("Destination is not a room.")
                return
            else:
                caller.move_to(destination)
                caller.msg("Teleported to %s." % destination)

#home doesn't care about private rooms or combat occuring for now

class CmdHome(MuxCommand):
    """
    home
    Usage:
      home
    Teleports you to your home location.
    """

    key = "home"
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        """Implement the command"""
        caller = self.caller
        home = caller.home
        
        if not home:
            caller.msg("You have no home!")
        elif home == caller.location:
            caller.msg("You are already home!")

        else:
            mapping = {"secret": True}
            caller.move_to(home, mapping=mapping)
            caller.msg("There's no place like home ...")
            
            caller.messages.messenger_notification(force=True)


class CmdLinkhere(MuxCommand):
    """
    linkhere
    Usage:
      +linkhere
    Sets a room as your IC home.
    """

    #todo: some permissions about what can and can't be set as home, for privacy purposes.

    key = "linkhere"
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        """Implement the command"""
        caller = self.caller
        home = caller.home

        if home == caller.location:
            caller.msg("You are already home!")
                
        elif not home:
            caller.msg("You set your home in this location.")
            caller.location = caller.home
