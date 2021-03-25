#!/usr/bin/env python
import os
import logging




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

    print(warnings)
    if errors:
        print(errors)
        raise ConfigurationError('\n'.join(errors))
    

if __name__ == "__main__":
    env = os.environ
    logger = logging.getLogger('rcon')
    try:
        #pre_flight_checks(env)
        from rcon.cli import cli, init
        init()
        cli()
    except SystemExit as e:
        logger.error("Program requested exit")
        exit(e.args[0])
    except ConfigurationError as e:
        print(repr(e))
        logger.error("MISSING Configuration: %s", e.args)
        exit(1)
    except Exception as e:
        print(repr(e))
        logger.exception("Unexpected error.")
        exit(1)
