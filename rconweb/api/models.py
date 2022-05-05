from django.db import models
from django.contrib.auth.models import User


class SteamPlayer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    steam_id_64 = models.CharField(max_length=100)

class RconUser(User):
    class Meta:
        permissions = (("can_not_change_server_settings", "Can NOT Change Server Settings"),)
