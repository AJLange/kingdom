from django.contrib import admin
from world.character.models import Character

class CharacterAdmin(admin.ModelAdmin):
    fields = ('name')

admin.site.register(Character, CharacterAdmin)