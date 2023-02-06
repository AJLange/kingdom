"""
Managers for the Character app. The ArxRosterManager was written as a replacement for a roster manager that
originally was an ObjectDB typeclass that stored roster entries as lists/dicts in Attributes.
"""
from django.db import models


class MuRosterManager(models.Manager):
    """
    Manager for the game's Roster. A lot of our methods will actually retrieve Character/ObjectDB instances
    for convenience.

    Active - for PCs played
    Available - for PCs unplayed
    Unavailable - for PCs on reserve or being used in plots.
    
    """

    @property
    def active(self):
        """Gets our Active roster"""
        return self.get_or_create(name="Active")[0]

    @property
    def available(self):
        """Gets our Available roster"""
        return self.get_or_create(name="Available")[0]

    @property
    def unavailable(self):
        """Gets our Unavailable roster"""
        return self.get_or_create(name="Unavailable")[0]

    @property
    def incomplete(self):
        """Gets our Incomplete roster"""
        return self.get_or_create(name="Incomplete")[0]

    @property
    def gone(self):
        """Gets our Gone roster, for dead/removed characters"""
        return self.get_or_create(name="Gone")[0]

    @property
    def deleted(self):
        """Gets our Deleted roster, for characters slated for removal"""
        return self.get_or_create(name="Deleted")[0]

    def get_all_active_characters(self):
        """Gets a queryset of all character objects in our Active roster"""
        from evennia.objects.models import ObjectDB

        return (
            ObjectDB.objects.select_related("roster__roster")
            .filter(roster__roster=self.active)
            .order_by("db_key")
        )

    def get_all_available_characters(self):
        """Gets a queryset of all character objects in our Available roster"""
        from evennia.objects.models import ObjectDB

        return (
            ObjectDB.objects.select_related("roster__roster")
            .filter(roster__roster=self.available)
            .order_by("db_key")
        )

    def get_all_unavailable_characters(self):
        """Gets a queryset of all character objects in our Unavailable roster"""
        from evennia.objects.models import ObjectDB

        return (
            ObjectDB.objects.select_related("roster__roster")
            .filter(roster__roster=self.unavailable)
            .order_by("db_key")
        )

    def get_all_incomplete_characters(self):
        """Gets a queryset of all character objects in our Incomplete roster"""
        from evennia.objects.models import ObjectDB

        return (
            ObjectDB.objects.select_related("roster__roster")
            .filter(roster__roster=self.incomplete)
            .order_by("db_key")
        )

    @staticmethod
    def get_character(name):
        """Gets a character by name"""
        from evennia.objects.models import ObjectDB

        try:
            return ObjectDB.objects.get(
                db_key__iexact=name, roster__roster__isnull=False
            )
        except ObjectDB.DoesNotExist:
            return None

    @staticmethod
    def search_by_filters(
        list_of_filters,
        roster_type="active",
        concept="None",
        group="None",
        social_rank="None",
        family="None",
    ):
        """
        Looks through the active characters and returns all who match
        the filters specified. 
        
        This is based on an Arx class and will be altered later based 
        on what I think we'd actually need to search by. For now it 
        searches on gender (but only in a binary way - weak) group 
        and concept which isn't really a thing and is totally a 
        placeholder.
        """
        from evennia.objects.models import ObjectDB

        char_list = ObjectDB.objects.filter(roster__roster__name__iexact=roster_type)
        match_set = set(char_list)
        if not char_list:
            return
        for char_filter in list_of_filters:
            if char_filter == "male":
                for char in char_list:
                    if (
                        not char.item_data.gender
                        or char.item_data.gender.lower() != "male"
                    ):
                        match_set.discard(char)
            if char_filter == "female":
                for char in char_list:
                    if (
                        not char.item_data.gender
                        or char.item_data.gender.lower() != "female"
                    ):
                        match_set.discard(char)
            if char_filter == "concept":
                for char in char_list:
                    if (
                        not char.item_data.group
                        or concept.lower() not in str(char.item_data.concept).lower()
                    ):
                        match_set.discard(char)

            if char_filter == "group":
                for char in char_list:
                    if (
                        not char.item_data.group
                        or group.lower() not in str(char.item_data.group).lower()
                    ):
                        match_set.discard(char)

        return match_set

