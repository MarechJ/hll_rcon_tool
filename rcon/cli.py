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

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not name.startswith('get_') and not name.startswith('set_'):
        continue
    wrapped = do_print(func)
    for pname, param in inspect.signature(func).parameters.items():
        if param.default != inspect._empty:
            wrapped = click.option(f"--{pname}", pname, default=param.default)(wrapped)
        else:
            wrapped = click.argument(pname)(wrapped)
    
    cli.command(name=name)(wrapped)
        
    
if __name__ == '__main__':
    cli()
