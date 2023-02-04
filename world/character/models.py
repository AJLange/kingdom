from django.db import models
from django.urls import reverse
from evennia.utils.idmapper.models import SharedMemoryModel



class Character(SharedMemoryModel):

    class Meta:
        managed = False

    def web_get_detail_url(self):
        return reverse(
            "character-detail",
            kwargs={"pk": self.pk, "slug": self.name},
        )
        

class ArmorMode(SharedMemoryModel):
    # armor mode object for holding stats
    class Meta:
        managed = False

class Weapon(SharedMemoryModel):
    #weapon obj for copyswap
    pass