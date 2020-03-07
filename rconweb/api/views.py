import inspect
import logging
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.extended_commands import Rcon
from rcon.commands import CommandFailedError
from rcon.settings import SERVER_INFO



def wrap_method(func, parameters):
    @csrf_exempt
    def wrapper(request):
        logger = logging.getLogger('rconweb')
        arguments = {}
        data = {}
        failure = False

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.GET

        logger.info("%s %s", func.__name__, data)

        for pname, param in parameters.items():
            if param.default != inspect._empty:
                arguments[pname] = data.get(pname)
            else:
                try:
                    arguments[pname] = data[pname]
                except KeyError:
                    # TODO raise 400
                    raise

        try:
            logger.debug("%s %s", func.__name__, arguments)
            res = func(**arguments)
        except CommandFailedError:
            failure = True
            res = None
        #logger.debug("%s %s -> %s", func.__name__, arguments, res)
        return JsonResponse({
            "result": res,
            "command": func.__name__,
            "arguments": data,
            "failed": failure
        })
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
