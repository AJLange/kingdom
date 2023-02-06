from django.contrib import admin
from world.character.models import PlayerCharacter, Roster

class PlayerCharacterAdmin(admin.ModelAdmin):
    model = PlayerCharacter


class RosterAdmin(admin.ModelAdmin):
    model = Roster

admin.site.register(PlayerCharacter, PlayerCharacterAdmin)
admin.site.register(Roster, RosterAdmin)