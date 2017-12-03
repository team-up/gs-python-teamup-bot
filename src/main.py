import json

import os

from bot import TextBot, ButtonBot
from teamup_service import TeamUpService


service = TeamUpService()

file_name = os.path.join(os.path.dirname(__file__), 'configuration.json')
with open(file_name) as data_file:
    configuration = json.load(data_file)

service.login(configuration)

if configuration['button_bot']:
    bot = ButtonBot(service)
else:
    bot = TextBot(service)
bot.run()

