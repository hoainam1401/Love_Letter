from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Player

# Register your models here.
admin.site.register(Player, UserAdmin)
