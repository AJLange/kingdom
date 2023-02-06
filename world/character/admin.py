from django.contrib import admin
from world.character.models import PlayerCharacter, Roster, ArmorMode

class PlayerCharacterAdmin(admin.ModelAdmin):
    model = PlayerCharacter


class ArmorModeAdmin(admin.ModelAdmin):
    list_display = ("id","db_name")
    list_display_links  = ("id","db_name")
    
    search_fields = ["^db_date_created", "^db_name"]
    save_as = True
    save_on_top = True
    list_select_related = True

class RosterAdmin(admin.ModelAdmin):
    model = Roster


admin.site.register(PlayerCharacter, PlayerCharacterAdmin)
admin.site.register(ArmorMode, ArmorModeAdmin)
admin.site.register(Roster, RosterAdmin)