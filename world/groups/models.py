from django.db import models
from evennia import ObjectDB
from world.character.models import Character
from evennia.utils.idmapper.models import SharedMemoryModel
from django.utils import timezone

# Storage of groups for PCs

class Squad(models.Model):

    db_key = models.CharField(max_length=100, db_index=True, default=0)
    db_name = models.CharField('Group Name', max_length=100)
    db_leader = models.CharField('Leader', max_length=120)
    db_orders = models.TextField(blank=True)
    db_members = models.ManyToManyField(Character, blank=True)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)

    def __str__(self):
        return self.db_name


class PlayerGroup(models.Model):

    db_key = models.CharField(max_length=80, db_index=True, default=0)
    db_name = models.CharField('Group Name', max_length=100)
    db_leader = models.CharField('Leader', max_length=120)
    db_description = models.TextField(blank=True)
    db_color = models.CharField(max_length=20)
    db_radio_a = models.CharField(max_length=10)
    db_radio_b = models.CharField(max_length=10)
    db_motd = models.TextField(blank=True)
    db_squads = models.ForeignKey(Squad, blank=True, null=True, on_delete=models.CASCADE)
    db_members = models.ManyToManyField(Character, blank=True)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)


    def __str__(self):
        return self.db_name


