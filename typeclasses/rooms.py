"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from commands.default_cmdsets import ChargenCmdset


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def at_say(
        self,
        message,
        msg_self=None,
        msg_location=None,
        receivers=None,
        msg_receivers=None,
        **kwargs,
    ):
        return message

    def msg_action(self, from_obj, no_name_emit_string, exclude=None, options=None):
        
        emit_string = "%s%s" % (
            "%s {c(%s){n" % (from_obj.name, from_obj.key),
            no_name_emit_string,
        )
            
        emit_string = "%s%s" % (from_obj, no_name_emit_string)
        self.msg_contents(
            emit_string,
            exclude=exclude,
            from_obj=from_obj,
            options=options,
            mapping=None,
        )


    pass

class PlayRoom(Room):
    """
    This room class is the most standard playroom for most RP.

    This room class does not have the commands associated with broader
    grid travel.
    """
    def at_object_creation(self):
        "this is called only at first creation"

class ChargenRoom(Room):
    """
    This room class is used by character-generation rooms. It makes
    the ChargenCmdset available.
    """
    def at_object_creation(self):
        "this is called only at first creation"
        self.cmdset.add(ChargenCmdset, permanent=True)


class StaffRoom(Room):
    """
    This room class is used by staff for lounges and such.
    """
    def at_object_creation(self):
        "this is called only at first creation"      


class OOCRoom(Room):
    """
    This is an OOC room that is missing play features but allows
    for people to go IC.
    """
    def at_object_creation(self):
        "this is called only at first creation"


class ShopRoom(Room):
    """
    This room class will be used for player-run shops
    """
    def at_object_creation(self):
        "this is called only at first creation"


class TravelRoom(Room):
    """
    This room would contain commands for fast-travel 
    and grid teleportation
    """
    def at_object_creation(self):
        "this is called only at first creation"


class TrainingRoom(Room):
    """
    This is an IC room that allows for no holds barred combat
    """
    def at_object_creation(self):
        "this is called only at first creation"


class WarRoom(Room):
    """
    This room type would allow interaction with the war system
    """
    def at_object_creation(self):
        "this is called only at first creation"
        