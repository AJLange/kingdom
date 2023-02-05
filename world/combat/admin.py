from django.contrib import admin
from world.combat.models import Weapon, ArmorMode, BusterList

class WeaponAdmin(admin.ModelAdmin):
    list_display = ("id", "db_name","db_class","db_type_1", "db_type_2", "db_type_3")
    list_display_links  = ("id","db_name")
    
    search_fields = ["^db_date_created", "^db_name"]
    save_as = True
    save_on_top = True
    list_select_related = True

class ArmorModeAdmin(admin.ModelAdmin):
    list_display = ("id", "db_name",)
    list_display_links  = ("id","db_name")
    
    search_fields = ["^db_date_created", "^db_name"]
    save_as = True
    save_on_top = True
    list_select_related = True

class BusterListAdmin(admin.ModelAdmin):
    list_display = ("id","db_thief", "db_name", "db_class","db_type_1", "db_type_2", "db_type_3")
    list_display_links  = ("id","db_thief","db_name")
    
    search_fields = ["^db_date_created", "^db_title"]
    save_as = True
    save_on_top = True
    list_select_related = True


admin.site.register(Weapon, WeaponAdmin)
admin.site.register(BusterList, BusterListAdmin)

