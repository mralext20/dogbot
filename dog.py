print('[dog] early startup')

import argparse
import asyncio
import logging

from ruamel.yaml import YAML

from dog import DogBot

parser = argparse.ArgumentParser(description='Dogbot.')
parser.add_argument('--docker', action='store_true', help='Enables Docker mode.', default=False)
args = parser.parse_args()

# load yaml configuration
print('[dog] reading configuration')
with open('config.yml', 'r') as config_file:
    cfg = YAML(typ='safe').load(config_file)

print('[dog] configuring logging')
# configure logging, and set the root logger's info to INFO
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# formatters
console_fmt = logging.Formatter('[{asctime}] [{levelname: <7}] {name}: {message}', '%I:%M:%S %p', style='{')
nice_fmt = logging.Formatter('%(asctime)s [%(name)s %(levelname)s] %(message)s', '%m/%d/%Y %I:%M:%S %p')

# enable debug logging for us, but not for discord
logging.getLogger('discord').setLevel(logging.INFO)
logging.getLogger('dog').setLevel(logging.DEBUG)

# main file handler, only info
file_handler = logging.FileHandler(filename='dog.log', encoding='utf-8')
file_handler.setFormatter(nice_fmt)

# stream handler (stdout)
stream = logging.StreamHandler()
stream.setFormatter(console_fmt)

# handle from all logs
root_logger.addHandler(stream)
root_logger.addHandler(file_handler)

logger = logging.getLogger('dog')

logger.info('Bot is starting...')

try:
    print('[dog] importing uvloop')
    import uvloop

    # uvloop for speedups
    print('[dog] setting policy')
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info('Using uvloop\'s event loop policy.')
except ModuleNotFoundError:
    print('[dog] uvloop not found')
    pass

if args.docker:
    logger.info('Running in Docker mode.')
    cfg['docker'] = True
    cfg['db']['redis'] = 'redis'
    cfg['db']['postgres'] = {
        'user': 'dogbot',
        'database': 'dogbot',
        'password': 'dogbot',
        'host': 'postgres'
    }
    logger.debug('Finished patching database configuration: %s', cfg['db'])

# additional options are passed directly to the bot as kwargs
additional_options = cfg['bot'].get('options', {})
additional_options.update({
    'owner_id': getattr(cfg, 'owner_id', None)
})

logger.info('Bot options: %s', additional_options)

# create and run the bot
print('[dog] creating instance')
d = DogBot(cfg=cfg, **additional_options)

print('[dog] loading extensions')
d.load_exts_recursively('dog/ext', 'Initial recursive load')

print('[dog] running')
d.run(cfg['tokens']['bot'])
print('[dog] run() exit')

# close log handlers (why)
# https://github.com/Rapptz/RoboDanny/blob/master/bot.py#L128-L132
handlers = root_logger.handlers[:]
for hndlr in handlers:
    hndlr.close()
    root_logger.removeHandler(hndlr)

print('[dog] exit')
