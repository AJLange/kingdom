from django.contrib import admin
from world.groups.models import Squad, PlayerGroup

class SquadAdmin(admin.ModelAdmin):
    model = Squad

class PlayerGroupAdmin(admin.ModelAdmin):
    model = PlayerGroup

admin.site.register(Squad)
admin.site.register(PlayerGroup)