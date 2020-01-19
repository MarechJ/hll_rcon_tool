from django.urls import path

from . import views

urlpatterns = [
    path(name, func, name='name')
    for name, func in views.commands
]
