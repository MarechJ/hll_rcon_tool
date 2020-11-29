from django.urls import path

from . import views
from . import auth
from . import services

urlpatterns = [
    path(name, func, name='name')
    for name, func in views.commands
] + [
    path('login', auth.do_login),
    path('logout', auth.do_logout),
    path('is_logged_in', auth.is_logged_in),
    path('get_online_mods', auth.get_online_mods),
    path('get_ingame_mods', auth.get_ingame_mods),
    path('get_services', services.get_services),
    path('do_service', services.do_service)
]
