#!/usr/bin/env python
import os
import logging

logger = logging.getLogger('rcon')

class ConfigurationError(Exception):
    pass

def _get_missing_env(keys, env):
    missing = []
    for k in keys:
        if not env.get(k):
            missing.append("'{}' was not specified in your configuration".format(k))
    return missing

def pre_flight_checks(env):
    required = [
        'HLL_HOST',
        'HLL_PORT',
        'HLL_PASSWORD',
        'REDIS_URL',
        'DB_URL',
    ]
    optionnal = [
        'DISCORD_WEBHOOK_AUDIT_LOG',
        'LOGGING_PATH',
        'LOGGING_LEVEL'
    ]

    errors = _get_missing_env(required, env)
    warnings = _get_missing_env(optionnal, env)

    if warnings:
        logger.warn

    if errors:
        raise ConfigurationError('\n'.join(errors))
    

if __name__ == "__main__":
    env = os.environ

    try:
        pre_flight_checks(env)
        from rcon.cli import cli, init
        init()
        cli()
    except SystemExit:
        pass
    except ConfigurationError as e:
        print(repr(e))
        logger.error("MISSING Configuration: %s", e.args)
        exit(1)
    except:
        logger.exception("Unexpected error. Env dump %s", env)
        exit(1)
