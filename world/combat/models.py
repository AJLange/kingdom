from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel


class Weapon(SharedMemoryModel):
    #weapon obj for copyswap
    pass

class ArmorMode(SharedMemoryModel):
    # armor mode object for holding stats
    class Meta:
        managed = False

class BusterList(SharedMemoryModel):
    #storing a list of copied attacks as something unique
    #this matches to a character who has 'bustered' these attacks.
    #the type as bustered is as buster (ranged) or technique (melee)
    #these attacks also contain more metadata such as a timeout
    #fields 'stable' and 'priority' are removed from these attacks.
    pass