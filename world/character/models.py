from django.db import models
from django.urls import reverse
from evennia.utils.idmapper.models import SharedMemoryModel



class Character(SharedMemoryModel):

    class Meta:
        managed = False
    db_name = models.CharField('Name', max_length=120)

    def web_get_detail_url(self):
        return reverse(
            "character-detail",
            kwargs={"pk": self.pk, "slug": self.name},
        )
        
    def __str__(self):
        return self.db_name

class ArmorMode(SharedMemoryModel):
    # armor mode object for holding stats
    class Meta:
        managed = False

class Weapon(SharedMemoryModel):
    #weapon obj for copyswap
    pass


'''
Roster Code from Arx. Examine this later for recompiling characters.

class Photo(SharedMemoryModel):
    """
    Used for uploading photos to cloudinary. It holds a reference to cloudinary-stored
    image and contains some metadata about the image.
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

    # Points to a Cloudinary image
    image = CloudinaryField("image")

    """ Informative name for mode """

    def __str__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ""
        return "Photo <%s:%s>" % (self.title, public_id)



class Roster(SharedMemoryModel):
    """
    A model for storing lists of entries of characters. Each RosterEntry has
    information on the Player and Character objects of that entry, information
    on player emails of previous players, GM notes, etc. The Roster itself just
    has locks for determining who can view the contents of a roster.
    """

    name = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    lock_storage = models.TextField(
        "locks", blank=True, help_text="defined in setup_utils"
    )
    objects = ArxRosterManager()

    def __init__(self, *args, **kwargs):
        super(Roster, self).__init__(*args, **kwargs)
        self.locks = LockHandler(self)

    def access(self, accessing_obj, access_type="view", default=True):
        """
        Determines if another object has permission to access.
        accessing_obj - object trying to access this one
        access_type - type of access sought
        default - what to return if no lock of access_type was found
        """
        return self.locks.check(accessing_obj, access_type=access_type, default=default)

    def __str__(self):
        return self.name or "Unnamed Roster"


class RosterEntry(SharedMemoryModel):
    """
    Main model for the character app. This is used both as an extension of an evennia AccountDB model (which serves as
    USER_AUTH_MODEL and a Character typeclass, and links the two together. It also is where some data used for the
    character lives, such as action points, the profile picture for their webpage, the PlayerAccount which currently
    is playing the character, and who played it previously. RosterEntry is used for most other models in the app,
    such as investigations, discoveries of clues/revelations/mysteries, etc.
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
    previous_accounts = models.ManyToManyField(
        "PlayerAccount", through="AccountHistory", blank=True
    )
    gm_notes = models.TextField(blank=True)
    # different variations of reasons not to display us
    inactive = models.BooleanField(default=False, null=False)
    frozen = models.BooleanField(default=False, null=False)
    # profile picture for sheet and also thumbnail for list
    profile_picture = models.ForeignKey(
        "Photo", blank=True, null=True, on_delete=models.SET_NULL
    )
    portrait_height = models.PositiveSmallIntegerField(default=480)
    portrait_width = models.PositiveSmallIntegerField(default=320)
    # going to use for determining how our character page appears
    sheet_style = models.TextField(blank=True)
    lock_storage = models.TextField(
        "locks", blank=True, help_text="defined in setup_utils"
    )
    action_points = models.SmallIntegerField(default=100, blank=100)
    show_positions = models.BooleanField(default=False)
    pose_count = models.PositiveSmallIntegerField(default=0)
    previous_pose_count = models.PositiveSmallIntegerField(default=0)
    brief_mode = models.BooleanField(default=False)
    dice_string = models.TextField(blank=True)

    def __init__(self, *args, **kwargs):
        super(RosterEntry, self).__init__(*args, **kwargs)
        self.locks = LockHandler(self)

    class Meta:
        """Define Django meta options"""

        verbose_name_plural = "Roster Entries"
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
        """We don't really want to delete RosterEntries for reals. So we fake it."""
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

    def adjust_xp(self, val):
        """Stores xp the player's earned in their history of playing the character."""
        try:
            if val < 0:
                return
            history = self.accounthistory_set.filter(
                account=self.current_account
            ).last()
            history.xp_earned += val
            history.save()
        except AttributeError:
            pass

    @property
    def undiscovered_clues(self):
        """Clues that we -haven't- discovered. We might have partial progress or not"""
        return Clue.objects.exclude(id__in=self.clues.all())

    @property
    def alts(self):
        """Other roster entries played by our current PlayerAccount"""
        if self.current_account:
            return self.current_account.characters.exclude(id=self.id)
        return []

    def discover_clue(self, clue, method="Prior Knowledge", message=""):
        """Discovers and returns the clue, if not already."""
        disco, created = self.clue_discoveries.get_or_create(clue=clue)
        if created:
            disco.mark_discovered(method=method, message=message or "")
        return disco

    @property
    def current_history(self):
        """Displays the current tenure of the PlayerAccount running this entry."""
        return self.accounthistory_set.last()

    @property
    def previous_history(self):
        """Gets all previous accounthistories after current"""
        return self.accounthistory_set.order_by("-id")[1:]

    @property
    def postable_flashbacks(self):
        """Queryset of flashbacks we can post to."""
        retired = FlashbackInvolvement.RETIRED
        return self.flashbacks.exclude(
            Q(concluded=True) | Q(flashback_involvements__status__lte=retired)
        )

    @property
    def impressions_of_me(self):
        """Gets queryset of all our current first impressions"""
        try:
            return self.current_history.received_contacts.all()
        except AttributeError:
            return []

    @property
    def previous_impressions_of_me(self):
        """Gets queryset of first impressions written on previous"""
        return FirstContact.objects.filter(to_account__in=self.previous_history)

    @property
    def public_impressions_of_me(self):
        """Gets queryset of non-private impressions_of_me"""
        try:
            return self.impressions_of_me.filter(private=False).order_by(
                "from_account__entry__character__db_key"
            )
        except AttributeError:
            return []

    @property
    def impressions_for_all(self):
        """Public impressions that both the writer and receiver have signed off on sharing"""
        try:
            return self.public_impressions_of_me.filter(
                writer_share=True, receiver_share=True
            )
        except AttributeError:
            return []

    def get_impressions_str(self, player=None, previous=False):
        """Returns string display of first impressions"""
        if previous:
            qs = self.previous_impressions_of_me.filter(private=False)
        else:
            qs = self.impressions_of_me.filter(private=False)
        if player:
            qs = qs.filter(from_account__entry__player=player)

        def public_str(obj):
            """Returns markup of the first impression based on its visibility"""
            if obj.viewable_by_all:
                return "{w(Shared by Both){n"
            if obj.writer_share:
                return "{w(Marked Public by Writer){n"
            if obj.receiver_share:
                return "{w(Marked Public by You){n"
            return "{w(Private){n"

        return "\n\n".join(
            "{c%s{n wrote %s: %s" % (ob.writer, public_str(ob), ob.summary) for ob in qs
        )

    @property
    def known_tags(self):
        """Returns a queryset of our collection of tags."""
        dompc = self.player.Dominion
        clu_q = Q(clues__in=self.clues.all())
        rev_q = Q(revelations__in=self.revelations.all())
        plot_q = Q(plots__in=dompc.active_plots)
        beat_q = Q(plot_updates__plot__in=dompc.active_plots)
        act_q = Q(actions__in=self.player.participated_actions)
        evnt_q = Q(events__dompcs=dompc) | Q(events__orgs__in=dompc.current_orgs)
        flas_q = Q(plot_updates__flashbacks__in=self.flashbacks.all())
        obj_q = Q(game_objects__db_location=self.character)
        qs = SearchTag.objects.filter(
            clu_q | rev_q | plot_q | beat_q | act_q | evnt_q | flas_q | obj_q
        )
        return qs.distinct().order_by("name")

    def display_tagged_objects(self, tag):
        """
        Returns a string listing tagged objects sorted by class, or empty string.
            Args:
                tag: SearchTag object
        """
        from server.utils.arx_utils import qslist_to_string
        from world.dominion.models import RPEvent
        from world.dominion.plots.models import PlotUpdate
        from web.helpdesk.models import KBItem, KBCategory

        dompc = self.player.Dominion
        querysets = []
        # knowledge base categories & items:
        querysets.append(KBCategory.objects.filter(search_tags=tag))
        querysets.append(KBItem.objects.filter(search_tags=tag))
        # append clues/revelations we know:
        for related_name in ("clues", "revelations"):
            querysets.append(getattr(self, related_name).filter(search_tags=tag))
        # append our plots:
        querysets.append(dompc.active_plots.filter(search_tags=tag))
        all_beats = PlotUpdate.objects.filter(search_tags=tag)  # ALL tagged beats
        # append our beats~
        querysets.append(all_beats.filter(plot__in=dompc.active_plots))
        # append beat-attached experiences we were part of, but don't have plot access to~
        # actions:
        querysets.append(self.player.participated_actions.filter(search_tags=tag))
        # events:
        querysets.append(
            RPEvent.objects.filter(
                Q(search_tags=tag) & (Q(dompcs=dompc) | Q(orgs__in=dompc.current_orgs))
            )
        )
        # flashbacks:
        querysets.append(self.flashbacks.filter(beat__in=all_beats))
        # append our tagged inventory items:
        querysets.append(
            self.character.locations_set.filter(search_tags=tag).order_by(
                "db_typeclass_path"
            )
        )
        msg = qslist_to_string(querysets)
        if msg:
            msg = ("|wTagged as '|235%s|w':|n" % tag) + msg
        return msg

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
        return super(RosterEntry, self).save(*args, **kwargs)

    @property
    def max_action_points(self):
        """Maximum action points we're allowed"""
        return 300

    @property
    def action_point_regen(self):
        """How many action points we get back in a week."""
        return 150 + self.action_point_regen_modifier

    @CachedProperty
    def action_point_regen_modifier(self):
        """AP penalty from our number of fealties"""
        from world.dominion.plots.models import PlotAction, PlotActionAssistant
        from evennia.server.models import ServerConfig

        ap_mod = 0
        # they lose 10 AP per fealty they're in
        try:
            ap_mod -= 10 * self.player.Dominion.num_fealties
        except AttributeError:
            pass
        # gain 20 AP for not having an investigation
        if not self.investigations.filter(active=True).exists():
            ap_mod += 20
        val = ServerConfig.objects.conf(key="BONUS_AP_REGEN", default=0)
        try:
            ap_mod += int(val)
        except (TypeError, ValueError):
            pass

        return ap_mod

    @classmethod
    def clear_ap_cache_in_cached_instances(cls):
        """Invalidate cached_ap_penalty in all cached RosterEntries when Fealty chain changes. Won't happen often."""
        for instance in cls.get_all_cached_instances():
            delattr(instance, "action_point_regen_modifier")

class PlayerAccount(SharedMemoryModel):
    """
    This is used to represent a player, who might be playing one or more RosterEntries. They're uniquely identified
    by their email address. Karma is for any OOC goodwill they've built up over time. Not currently used. YET.
    """

    email = models.EmailField(unique=True)
    karma = models.PositiveSmallIntegerField(default=0, blank=True)
    gm_notes = models.TextField(blank=True, null=True)
    episodes = models.ManyToManyField(
        "character.Episode",
        related_name="accounts",
        through="dominion.ActionPerEpisode",
    )

    def __str__(self):
        return str(self.email)

    @property
    def total_xp(self):
        """Total xp they've earned over all time"""
        qs = self.accounthistory_set.all()
        return sum(ob.xp_earned for ob in qs)
'''