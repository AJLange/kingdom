
from typeclasses.objects import Object
from evennia import Command, CmdSet
from evennia.commands.default.building import CmdTeleport
from evennia.objects.models import ObjectDB
from typeclasses.objects import Object
from typeclasses.exits import Exit
from evennia import DefaultExit




class CmdEnterCity(Command):
    """
    entering a city
    
    Usage:
      enter <city>

    This will be available to players in the same location
    as a city and allows entering that city.
    """

    key = "enter"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Enter where?")
            return
        city = self.caller.search(self.args)
        self.caller.msg("You enter the city.")
        self.caller.move_to(city)


class CmdLeaveCity(Command):
    """
    leaving the city.
 
    Usage:
      leave

    When inside a city, exit the city with this.
    """

    key = "leave"
    locks = "cmd:all()"

    def func(self):
        city = self.obj
        parent = city.location
        self.caller.move_to(parent)


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


'''
notes here on player quotas:
10 items
10 personal rooms
10 places

per player character.
Pets can only be created by staff for now (may change later)

'''

