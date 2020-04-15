from django.contrib import admin
from .models import Event, Metadata

# username: sam
# password: passwrod

# Register your models here.

admin.site.register(Event)
admin.site.register(Metadata)