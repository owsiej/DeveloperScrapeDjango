from django.contrib import admin

from . import models

# Register your models here.

admin.site.register(models.Developer)
admin.site.register(models.Investment)
admin.site.register(models.Flat)
