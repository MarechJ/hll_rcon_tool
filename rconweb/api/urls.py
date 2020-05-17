from django.urls import path

from . import views
from . import auth

urlpatterns = [
    path(name, func, name='name')
    for name, func in views.commands
] + [
    path('login', auth.do_login),
    path('logout', auth.do_logout),
    path('is_logged_in', auth.is_logged_in)
]
