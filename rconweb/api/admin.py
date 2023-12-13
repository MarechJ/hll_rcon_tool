# Register your models here.
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from rconweb.settings import SECRET_KEY

from .models import DjangoAPIKey, SteamPlayer


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class SteamPlayerInline(admin.StackedInline):
    model = SteamPlayer
    can_delete = False
    verbose_name_plural = "steamid"


class DjangoAPIKeyAdminForm(forms.ModelForm):
    class Meta:
        model = DjangoAPIKey
        fields = "__all__"

    def clean_api_key(self):
        if len(self.cleaned_data["api_key"]) < 32:
            raise forms.ValidationError("Minimum API key length is 32 characters")

        if DjangoAPIKey.objects.filter(
            api_key=make_password(self.cleaned_data["api_key"], salt=SECRET_KEY)
        ).exists():
            raise forms.ValidationError("Duplicate API keys are not allowed")

        return self.cleaned_data["api_key"]


class DjangoAPIKeyInline(admin.StackedInline):
    model = DjangoAPIKey
    form = DjangoAPIKeyAdminForm

    can_delete = True
    verbose_name_plural = "API Keys"

    show_change_link = True

    extra = 0
    readonly_fields = ["date_created", "date_modified"]


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (SteamPlayerInline, DjangoAPIKeyInline)
    # inlines = [SteamPlayerInline]


class DjangoAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "api_key", "date_created", "date_modified", "notes")
    list_filter = ("user",)
    search_fields = ("notes",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    form = DjangoAPIKeyAdminForm


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(DjangoAPIKey, DjangoAPIKeyAdmin)
