'''
Places code. This is borrowed from Arx with some modification -
we want Places to broadcast, to organize big scenes, rather
than be private places that don't broadcast out, so everything
should hit the main room.

To do: update pose code to reflect this change
(since tt will be deleted in later iteration)
'''

from evennia.commands.cmdset import CmdSet
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import list_to_string


def get_movement_message(verb, place):
    """Returns the movement message for joining/leaving a place"""
    if not place or not place.key:
        return "You %s the place." % verb
    prefix = place.key.split()[0]
    article = ""
    if prefix.lower() not in ("the", "a", "an"):
        article = "the "
    return "You %s %s%s." % (verb, article, place.key)


# ------------------------------------------------------------
# Commands defined for places
# ------------------------------------------------------------


class CmdJoin(MuxCommand):
    """
    Enters a particular place.

    Usage:
        join <place #>

    Sits down at one of the places in the room. Posing while in 
    a place will append the location of the place to your pose.
    This is for organizing plot scenes that technically take place
    in more than one location.

    To leave, use 'depart'.
    """

    key = "join"
    locks = "cmd:all()"
    help_category = "Posing"

    def func(self):
        """Implements command"""
        caller = self.caller
        places = caller.location.places
        table = caller.sitting_at_place
        args = self.args
        if not args or not args.strip("#").strip().isdigit():
            caller.msg("Usage: {wjoin <place #>{n")
            caller.msg("To see a list of places: {wplaces{n")
            return
        if table:
            table.leave(caller)
        # The player probably only has this command if it's in their inventory
        if not places:
            caller.msg("This room has no places installed.")
            return
        args = args.strip("#").strip()
        args = int(args) - 1
        if not (0 <= args < len(places)):
            caller.msg("Number specified does not match any of the places here.")
            return
        table = places[args]
        occupants = table.item_data.occupants
        if len(occupants) >= table.item_data.max_spots:
            caller.msg("There is no room at %s." % table.key)
            return
        table.join(caller)
        caller.msg(get_movement_message("join", table))






class CmdListPlaces(MuxCommand):
    """
    Lists places in current room for private chat
    Usage:
        places

    Lists all the places in the current room that you can chat at and how
    many empty spaces each has. If there any places within the room, the
    'join' command will be available. 
    
    Posing while in a place will append the location of the place 
    to your pose.
    This is for organizing plot scenes that technically take place
    in more than one location.
    Logging out or disconnecting will require you to join a place 
    once more. To leave a place, use 'depart'.
    """

    key = "places"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        """Implements command"""
        caller = self.caller
        places = caller.location.places
        caller.msg("{wPlaces here:{n")
        caller.msg("{w------------{n")
        if not places:
            caller.msg("No places found.")
            return
        for num in range(len(places)):
            p_name = places[num].key
            max_spots = places[num].item_data.max_spots
            occupants = places[num].item_data.occupants
            spots = max_spots - len(occupants)
            caller.msg("%s (#%s) : %s empty spaces" % (p_name, num + 1, spots))
            if occupants:
                # get names
                names = [ob.name for ob in occupants if ob.access(caller, "view")]
                caller.msg("-Occupants: %s" % list_to_string(names))

'''
I'm retaining this over-rides from Arx's set
but I don't think we necessarily need them yet.

class DefaultCmdSet(CmdSet):
    """
    The default cmdset always sits
    on the button object and whereas other
    command sets may be added/merge onto it
    and hide it, removing them will always
    bring it back. It's added to the object
    using obj.cmdset.add_default().
    """

    key = "PlacesDefault"
    # if we have multiple wearable objects, just keep
    # one cmdset, ditch others
    key_mergetype = {"PlacesDefault": "Replace"}
    priority = 0
    duplicates = False

    def at_cmdset_creation(self):
        """Init the cmdset"""
        self.add(CmdJoin())
        self.add(CmdListPlaces())


class SittingCmdSet(CmdSet):
    """
    The default cmdset always sits
    on the button object and whereas other
    command sets may be added/merge onto it
    and hide it, removing them will always
    bring it back. It's added to the object
    using obj.cmdset.add_default().
    """

    key = "SittingCmdSet"
    # if we have multiple wearable objects, just keep
    # one cmdset, ditch others
    key_mergetype = {"SittingCmdSet": "Replace"}
    priority = 0
    duplicates = False

    def at_cmdset_creation(self):
        """Init the cmdset"""
        self.add(CmdDepart())
        self.add(CmdTableTalk())
'''

class CmdDepart(MuxCommand):
    """
    Stands up from the table you are at.

    Usage:
        depart

    Leaves your current table. Logging out or disconnecting will
    cause you to leave automatically. To see available places,
    use 'places'. To join a place, use 'join'.
    """

    key = "depart"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        """Implements command"""
        caller = self.caller
        table = caller.sitting_at_place
        if not table:
            caller.msg("You are not sitting at a table.")
            return
        table.leave(caller)
        caller.msg(get_movement_message("leave", table))


'''
class CmdTableTalk(MuxCommand):
    """
    Speaks at your current table.

    Usage:
        tt <message>
        tt/ooc <message>

    Sends a message to your current table. You may pose at the table by
    starting a message with ':' or ';'. ':' has a space after your name,
    while ';' does not. So ':waves' is 'Bob waves', while ';s waves' is
    'Bobs waves'. A table emit '|' does not add your name, so be sure to
    identify yourself somehow in your text.

    To leave a place, use 'depart'.
    """

    key = "tt"
    locks = "cmd:all()"
    help_category = "Social"
    # characters used for poses/emits
    char_symbols = (";", ":", "|")

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Usage: {wtt <message>{n")
            return

        table = caller.sitting_at_place
        if not table:
            caller.msg("You are not sitting at a private table currently.")
            return

        is_ooc = False
        msg_type = table.TT_SAY
        options = {"is_pose": True}

        # If /ooc was used
        ooc_string = ""
        if "ooc" in self.switches:
            options = {}
            ooc_string = "|w(OOC)|n "
            is_ooc = True

        # If highlighting color for caller
        highlight = caller.player_ob.db.highlight_place
        if highlight:
            place_color = caller.char_ob.db.place_color or ""
        else:
            place_color = ""

        # get the first character to see if it's special
        start_char = args[0]
        if start_char in self.char_symbols:
            whitespace = " " if args.startswith(":") else ""
            msg = args.lstrip(":").lstrip(";").lstrip("|")
            msg = "%s%s" % (whitespace, msg)
            if start_char == "|":
                # send message as an emit
                msg_type = table.TT_EMIT
            else:
                # send message as a pose
                msg_type = table.TT_POSE

        # If tt "say" msg, send to caller as "you say" then everyone else as "caller.name says"
        if msg_type == table.TT_SAY:
            you_msg = '{ooc}At the {place_color}{place_name}|n, you say, "{msg}"'
            you_msg = you_msg.format(
                ooc=ooc_string, place_color=place_color, place_name=table.key, msg=args
            )

            caller.msg(you_msg, options=options, from_obj=caller)
            table.tt_msg(
                args,
                from_obj=caller,
                exclude=caller,
                msg_type=msg_type,
                is_ooc=is_ooc,
                options=options,
            )
        else:
            # Otherwise, it's a pose or emit so send it to everyone as a pose/emit.
            table.tt_msg(
                msg, from_obj=caller, msg_type=msg_type, is_ooc=is_ooc, options=options
            )
'''

class CmdConstruct(MuxCommand):
    """
    Create a private room object.
    Players will have a limited quota of private room objects.
    Construct a room using 

    construct <name of room>
    eg
    construct Doctor's Office
    """

    key = "construct"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("What do yo want to construct?")
            return

        ''' to do: the rest of the command '''


class CmdCraft(MuxCommand):
    """
    Create a small object.
    Players will have a limited quota of miscellaneous objects.
    These objects can hold a desc, but have no other 
    functionality. 

    craft <name of object>
    eg
    craft Soccer Ball
    """

    key = "craft"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("What do yo want to craft?")
            return

        ''' to do: the rest of the command '''


class CmdMakePlace(MuxCommand):
    """
    Create a place.
    A place is an object that can be entered.
    It does not behave like a room; it simply shows
    a relative location of players to ease in the creation
    of setpieces that may have multiple sub-locations.

    All poses done inside a place append the name of the 
    place to the front of the pose, for ease of
    readability.

    place <name of place>
    eg
    place Corner Table
    """

    key = "place"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Syntax: Place <name of place>")
            return

        ''' to do: the rest of the command '''


'''
notes here on player quotas:
10 items
10 personal rooms
10 places

per player character.
Pets can only be created by staff for now (may change later)

'''

