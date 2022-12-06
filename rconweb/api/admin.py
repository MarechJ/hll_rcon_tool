# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import SteamPlayer


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class SteamPlayerInline(admin.StackedInline):
    model = SteamPlayer
    can_delete = False
    verbose_name_plural = "steamid"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (SteamPlayerInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
