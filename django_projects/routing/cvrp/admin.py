from django.contrib import admin
from .models import Address, Location, Route, Driver

admin.site.register(Driver)
admin.site.register(Route)
admin.site.register(Address)
admin.site.register(Location)
