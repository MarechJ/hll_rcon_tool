import os, json, sys

# Setup logger
import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logging.info('Upgrading auto settings...')

CONFIG_DIR = sys.argv[1] if len(sys.argv) >= 2 else 'config/'
logging.info('Using "%s" as config dir', CONFIG_DIR)
if not os.path.exists(CONFIG_DIR):
    logging.fatal('Invalid config dir, aborting...')
    exit(1)


"""

To upgrade, run the below command:

python3 upgrade_auto_settings.py [config/]

"""


for filename in os.listdir(CONFIG_DIR):
    if filename.startswith('auto_settings'):
        try:
            with open(CONFIG_DIR+filename, 'r') as f:
                config = json.load(f)

            new = dict(
                always_apply_defaults=False,
                defaults={command: params for (command, params) in config['player_count']['defaults']},
                rules=[]
            )

            for i, (condition, params, commands) in enumerate(config['player_count']['rules']):
                new_rule = dict(
                    conditions={},
                    commands={command: params for (command, params) in config['player_count']['defaults']}
                )
                
                if condition == "between":
                    min, max = params
                    new_rule['conditions']['player_count'] = dict(min=min, max=max)
                elif condition == "equals":
                    val = params[0]
                    new_rule['conditions']['player_count'] = dict(min=val, max=val)
                else:
                    logging.warning('Invalid condition for rules[%s], skipping condition...', i)

                new['rules'].append(new_rule)

            with open(CONFIG_DIR+filename, 'w') as f:
                json.dump(new, f, indent=2)

        except Exception as e:
            logging.error('Failed to upgrade %s: %s: %s', filename, e.__class__.__name__, e)
        
        else:
            logging.info('Successfully upgraded %s', filename)