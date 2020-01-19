import inspect

import click

from rcon.settings import SERVER_INFO
from rcon.commands import ServerCtl

@click.group()
def cli():
    pass

ctl = ServerCtl(
    SERVER_INFO
)

def do_print(func):
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        print(res)
        return res
    return wrap


PREFIXES_TO_EXPOSE = [
    'get_', 'set_', 'do_'
]

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
        continue
    wrapped = do_print(func)

    # Registering the arguments of the function must be done from last
    # to first as they are decorators
    for pname, param in [i for i in inspect.signature(func).parameters.items()][::-1]:
        if param.default != inspect._empty:
            wrapped = click.option(f"--{pname}", pname, default=param.default)(wrapped)
        else:
            wrapped = click.argument(pname)(wrapped)
    
    cli.command(name=name)(wrapped)
        
    
if __name__ == '__main__':
    cli()
