from django.db import models
from world.groups.models import PlayerGroup

# Create your models here.

class BulletinBoard(models.Model):

    db_name = models.CharField('Board Name',max_length=120)
    db_groups = models.ManyToManyField(PlayerGroup, blank=True)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)

    def __str__(self):
        return self.db_name


class BoardPost(models.Model):

    db_title = models.CharField('Post Title',max_length=120)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)

    db_board = models.ForeignKey(BulletinBoard, on_delete=models.CASCADE)
    posted_by = models.CharField('Author',max_length=120)
    body_text = models.TextField('Post')

    def __str__(self):
        return self.db_title