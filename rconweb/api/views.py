import inspect

from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def wrap_method(func, parameters):
    def wrapper(request):
        arguments = {}
        for pname, param in parameters.items():
            if param.default != inspect._empty:
                arguments[pname] = request.POST.get(pname)
            else:
                arguments[pname] = request.POST[pname]

        res = func(**arguments)
        return JsonResponse({"result": res})
    return wrapper


ctl = Rcon(
    SERVER_INFO
)


PREFIXES_TO_EXPOSE = [
    'get_', 'set_', 'do_'
]

commands = []

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
        continue

    commands.append(
        (name, wrap_method(func, inspect.signature(func).parameters))
    )
