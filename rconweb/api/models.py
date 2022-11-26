from django.contrib.auth.models import User
from django.db import models


class SteamPlayer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    steam_id_64 = models.CharField(max_length=100)
