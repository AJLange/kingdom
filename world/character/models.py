from django.db import models
from django.urls import reverse


class Character(models.Model):

    class Meta:
        managed = False

    def web_get_detail_url(self):
        return reverse(
            "character-detail",
            kwargs={"pk": self.pk, "slug": self.name},
        )
        

class ArmorMode(models.Model):
    # armor mode object for holding stats
    class Meta:
        managed = False

class Weapon(models.Model):
    #weapon obj for copyswap
    pass