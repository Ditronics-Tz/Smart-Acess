from django.contrib import admin
from .models import SecurityPersonnel, PhysicalLocations, AccessGates

# Register your models here.
admin.site.register(SecurityPersonnel)
admin.site.register(PhysicalLocations)
admin.site.register(AccessGates)
