from django.db import models
from evennia import ObjectDB
from django.utils import timezone

# request database

class Request(models.Model):

    db_title = models.CharField('Title', max_length=200)
    db_submitter = models.CharField('Submitter', max_length=120)
    db_message_body = models.TextField('Message Body')
    db_assigned_to = models.CharField('Assigned To', max_length=120)
    db_copied_to = models.TextField('Copied To')
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)
    class RequestCategory(models.IntegerField):
        GENERAL = 1
        BUGFIX = 2
        CHARACTER = 3
        NEWS = 4
        BUILD = 5
        AUTO = 6
        RESEARCH = 7
        TYPE_CHOICES = (
            (GENERAL, 'General'),
            (BUGFIX, 'Bugfix'),
            (CHARACTER, 'Character'),
            (NEWS, 'News'),
            (BUILD, 'Build'),
            (AUTO, 'Auto'),
            (RESEARCH, 'Research'),
        )

    # The type of request
    type = models.IntegerField(
        choices=RequestCategory.TYPE_CHOICES
    )

    def __str__(self):
        return self.db_name



