from django.db import models
from django.urls import reverse
from django.conf import settings
from evennia.utils.idmapper.models import SharedMemoryModel
from world.character.manager import MuRosterManager
# from cloudinary.models import CloudinaryField
from evennia.locks.lockhandler import LockHandler
import traceback



'''
Roster Code from Arx. Examine this later for recompiling characters.
'''

'''

class Photo(SharedMemoryModel):
    """
    Used for uploading photos to cloudinary. It holds a reference to cloudinary-stored
    image and contains some metadata about the image.

    I'm not using this right now, just keeping it, later will have a custom upload 
    solution.
    """

    #  Misc Django Fields
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(
        "Name or description of the picture (optional)", max_length=200, blank=True
    )
    owner = models.ForeignKey(
        "objects.ObjectDB",
        blank=True,
        null=True,
        verbose_name="owner",
        help_text="a Character owner of this image, if any.",
        on_delete=models.SET_NULL,
    )
    alt_text = models.CharField(
        "Optional 'alt' text when mousing over your image", max_length=200, blank=True
    )

    # Points to an image
    image = CloudinaryField("image")

    """ Informative name for mode """

    def __str__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ""
        return "Photo <%s:%s>" % (self.title, public_id)
'''

class Roster(SharedMemoryModel):
    """
    A model for storing lists of entries of characters. 
    
    I'm not worried about locking access to the Roster. Used for +FClist.
    """

    name = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    objects = MuRosterManager()
    lock_storage = models.TextField(
        "locks", blank=True, help_text="defined in setup_utils"
    )

    def __init__(self, *args, **kwargs):
        super(Roster, self).__init__(*args, **kwargs)
        self.locks = LockHandler(self)

    def __str__(self):
        return self.name or "Unnamed Roster"


class PlayerCharacter(SharedMemoryModel):
    """
    Main model for the character app. This is used both as an extension of an evennia 
    AccountDB model which serves as USER_AUTH_MODEL and a Character typeclass, and links 
    the two together. It also is where some data used for the
    character lives, the profile picture for their webpage, 
    the PlayerAccount which currently is playing the character, and who played it previously. 

    This is based on Arx modified RosterEntry minus the stuff that's specific to Arx, until
    I refactor it again.
    
    This model will be referenced in the future as a rebuild of basic character setup.
    """

    roster = models.ForeignKey(
        "Roster",
        related_name="entries",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True,
    )
    player = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="roster",
        blank=True,
        null=True,
        unique=True,
        on_delete=models.CASCADE,
    )
    character = models.OneToOneField(
        "objects.ObjectDB",
        related_name="roster",
        blank=True,
        null=True,
        unique=True,
        on_delete=models.CASCADE,
    )
    current_account = models.ForeignKey(
        "PlayerAccount",
        related_name="characters",
        db_index=True,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    gm_notes = models.TextField(blank=True)
    # different variations of reasons not to display us
    inactive = models.BooleanField(default=False, null=False)
    frozen = models.BooleanField(default=False, null=False)
    # profile picture for sheet and also thumbnail for list

    '''
    profile setup for web, not using this yet.

        profile_picture = models.ForeignKey(
        "Photo", blank=True, null=True, on_delete=models.SET_NULL
    )
    
    portrait_height = models.PositiveSmallIntegerField(default=480)
    portrait_width = models.PositiveSmallIntegerField(default=320)
    '''

    # going to use for determining how our character page appears
    sheet_style = models.TextField(blank=True)
    lock_storage = models.TextField(
        "locks", blank=True, help_text="defined in setup_utils"
    )

    brief_mode = models.BooleanField(default=False)
    dice_string = models.TextField(blank=True)

    def __init__(self, *args, **kwargs):
        super(PlayerCharacter, self).__init__(*args, **kwargs)
        self.locks = LockHandler(self)

    class Meta:
        """Define Django meta options"""

        verbose_name = "Character"
        unique_together = ("player", "character")

    def __str__(self):
        if self.character:
            return self.character.key
        if self.player:
            return self.player.key
        return "Blank Entry"

    def access(self, accessing_obj, access_type="show_hidden", default=False):
        """
        Determines if another object has permission to access.
        accessing_obj - object trying to access this one
        access_type - type of access sought
        default - what to return if no lock of access_type was found
        """
        return self.locks.check(accessing_obj, access_type=access_type, default=default)

    def fake_delete(self):
        """for some reason this is fake delete. I am not gonna mess with it for now."""
        self.roster = Roster.objects.deleted
        self.inactive = True
        self.frozen = True
        self.save()

    def undelete(self):
        """Restores a fake-deleted entry."""
        self.roster = Roster.objects.active
        self.inactive = False
        self.frozen = False
        self.save()

    @property
    def alts(self):
        """Other roster entries played by our current PlayerAccount"""
        if self.current_account:
            return self.current_account.characters.exclude(id=self.id)
        return []

    @property
    def current_history(self):
        """Displays the current tenure of the PlayerAccount running this entry."""
        return self.accounthistory_set.last()

    @property
    def previous_history(self):
        """Gets all previous accounthistories after current"""
        return self.accounthistory_set.order_by("-id")[1:]

    def save(self, *args, **kwargs):
        """check if a database lock during profile_picture setting has put us in invalid state"""
        if self.profile_picture and not self.profile_picture.pk:
            print("Error: RosterEntry %s had invalid profile_picture." % self)
            # noinspection PyBroadException
            try:
                self.profile_picture.save()
            except Exception:
                print("Error when attempting to save it:")
                traceback.print_exc()
            else:
                print("Saved profile_picture successfully.")
            # if profile_picture's pk is still invalid we'll just clear it out to super().save won't ValueError
            if not self.profile_picture.pk:
                print("profile_picture has no pk, clearing it.")
                self.profile_picture = None
        return super(PlayerCharacter, self).save(*args, **kwargs)

    '''
    this except for properties I actually want

    @property
    def action_point_regen(self):
        """How many action points we get back in a week."""
        return 150 + self.action_point_regen_modifier
    '''


class PlayerAccount(SharedMemoryModel):
    """
    This is used to represent a player, who might be playing one or more RosterEntries. 
    They're uniquely identified by their email address which is all we use for matching right now.
    """

    email = models.EmailField(unique=True)
    gm_notes = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return str(self.email)
