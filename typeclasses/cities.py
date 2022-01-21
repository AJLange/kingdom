from typeclasses.objects import Object

class City(Object):
    '''
    A type of object that, when entered, contains a 
    grid of rooms.
    '''
    def __init__ (self):
        self.name = "Start city"
''' 
to do, add this with teleport
https://www.evennia.com/docs/latest/api/evennia.objects.objects.html
'''

class Warship(City):
    '''
    A type of object that, when entered, contains a 
    grid of rooms, but is also mobile from room to room.

    Basically, a warship is a type of mobile city.
    '''
    def __init__ (self):
        self.name = "Colossus"