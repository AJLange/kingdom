from django.contrib import admin
from world.requests.models import Request

# Register your models here.

class RequestAdmin(admin.ModelAdmin):
    model = Request
    
admin.site.register(Request)
