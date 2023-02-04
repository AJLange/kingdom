from django.db import models
from evennia import ObjectDB
from django.utils import timezone
from evennia.utils.idmapper.models import SharedMemoryModel

# request database
# todo - some of these charfields should be manytomany screens for characters

# response to a request. Request can have multiple responses/back and forth
class RequestResponse(models.Model):
    db_text = models.TextField('Response',blank=True)
    db_submitter = models.CharField('Submitter', max_length=120)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)

class Request(models.Model):

    db_title = models.CharField('Title', max_length=200)
    db_submitter = models.CharField('Submitter', max_length=120)
    db_message_body = models.TextField('Message Body')
    db_assigned_to = models.CharField('Assigned To', max_length=120,blank=True)
    db_copied_to = models.TextField('Copied To',blank=True)
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
    db_response = models.ForeignKey(RequestResponse, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.db_title


class Keyword(SharedMemoryModel):
    db_key = models.CharField('Keyword', max_length=200, primary_key=True)
    
    def __str__(self):
        return self.db_key

class File(SharedMemoryModel):
    db_title = models.CharField('Name', max_length=200)
    db_text = models.TextField('File',blank=True)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)
    db_author = models.CharField('Author',max_length=200)
    db_keywords = models.ForeignKey(Keyword,blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.db_title

class Topic(SharedMemoryModel):
    db_name = models.CharField('Name', max_length=200)
    db_file = models.ForeignKey(File,blank=True, null=True, on_delete=models.CASCADE)
    db_date_created = models.DateTimeField('date created', editable=False,
                                            auto_now_add=True, db_index=True)

    def __str__(self):
        return self.db_name


