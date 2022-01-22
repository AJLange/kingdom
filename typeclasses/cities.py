from typeclasses.objects import Object
from evennia import Command, CmdSet



class CmdEnterCity(Command):
    """
    entering the train
    
    Usage:
      enter <city>

    This will be available to players in the same location
    as the train and allows them to embark.
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




