
from typeclasses.objects import Object
from evennia import Command, CmdSet
from evennia.commands.default.building import CmdTeleport
from evennia.objects.models import ObjectDB
from typeclasses.objects import Object
from typeclasses.exits import Exit
from evennia import DefaultExit


class City(Object):
    '''
    A type of object that, when entered, contains a 
    grid of rooms.
    '''
    def __init__ (self):
        self.name = "Start city"    
    def at_cmdset_creation(self):
        self.add(CmdEnterCity())
        self.add(CmdLeaveCity())

    def at_object_creation(self):
        self.db.desc = "Default City Description."

        
''' 
to do, add this with teleport
https://www.evennia.com/docs/latest/api/evennia.objects.objects.html

here's how to do a moving one:
https://www.evennia.com/docs/latest/Tutorial-Vehicles.html

'''

class Warship(City):
    '''
    A type of object that, when entered, contains a 
    grid of rooms, but is also mobile from room to room.

    Basically, a warship is a type of mobile city.
    '''
    def __init__ (self):
        self.name = "Colossus"
    def at_object_creation(self):
        self.db.desc = "Default Mobile Base Desc."


class PersonalRoom(Exit):
    '''
    A personal Room is an exit created by a player.
    Entering a personal room teleports the player to
    a single room on the grid which is their dedicated
    personal quarters room. 
    Personal Rooms can be picked up, moved, and re-desced.

    '''

    def at_object_creation(self):
        self.db.desc = "This is a personal room."


class Place(Object):
    '''
    A Place is an object that, when entered, still broadcasts to 
    the room that it's in.
    (This may replace the current way that Places is coded.)
    This does not leave the current location.
    '''

    def at_object_creation(self):
        self.db.desc = "This is a Place. Enter it to append your location to the room."


class Vehicle(Place):
    '''
    A vehicle is a type of Place.
    The difference between a vehicle and an ordinary Place
    is that a vehicle can be moved around from the inside via
    a series of driving commans.

    '''

    def at_object_creation(self):
        self.db.desc = "This is a Place. Enter it to append your location to the room."


