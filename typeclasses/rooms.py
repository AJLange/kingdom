"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom


'''
eventually make use of this for special roomtypes
https://www.evennia.com/docs/0.9.5/Zones.html

you do not need that many discreet roomtypes if categorized
this way.

'''

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


class OOCRoom(Room):
    """
    This is an OOC room that is missing play features but allows
    for people to go IC.
    """
    def at_object_creation(self):
        "this is called only at first creation"


class PlayRoom(Room):
    """
    This room class is the most standard playroom for most RP.

    This room class does not have the commands associated with broader
    grid travel.
    """
    def at_object_creation(self):
        "this is called only at first creation"

class StaffRoom(Room):
    """
    This room class is used by staff for lounges and such.
    """
    def at_object_creation(self):
        "this is called only at first creation"      

class ChargenRoom(StaffRoom):
    """
    This room class is used by character-generation rooms. It makes
    the ChargenCmdset available.
    """
    def at_object_creation(self):
        "this is called only at first creation"
        


class TrainingRoom(PlayRoom):
    """
    This is an IC room that allows for no holds barred combat
    """
    def at_object_creation(self):
        "this is called only at first creation"



class QuartersRoom(PlayRoom):
    """
    This room type would allow people to set down quarters rooms of their own.
    """
    def at_object_creation(self):
        "this is called only at first creation"
        
        


class ShopRoom(PlayRoom):
    """
    This room class will be used for player-run shops
    """
    def at_object_creation(self):
        "this is called only at first creation"


class WarRoom(PlayRoom):
    """
    This room type would allow interaction with the war system
    """
    def at_object_creation(self):
        "this is called only at first creation"



class Cockpit(PlayRoom):
    """
    This room type is for driving mobile bases
    """
    def at_object_creation(self):
        "this is called only at first creation"



class PrivateRoom(PlayRoom):
    """
    A type of IC room with some additional lock functions.
    """
    def at_object_creation(self):
        "this is called only at first creation"