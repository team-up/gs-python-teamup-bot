import json

import os

from bot import TextBot, ButtonBot
from teamup_service import TeamUpService


file_name = os.path.join(os.path.dirname(__file__), 'configuration.json')
with open(file_name) as data_file:
    configuration = json.load(data_file)

is_button_bot = configuration.pop('button_bot')
service = TeamUpService(configuration)
print(configuration)

service.login()

if is_button_bot:
    bot = ButtonBot(service)
else:
    bot = TextBot(service)
bot.run()

