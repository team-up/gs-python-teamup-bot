import json

import os

from teamup_service import TeamUpService

import time

service = TeamUpService()

file_name = os.path.join(os.path.dirname(__file__), 'authentication.json')
with open(file_name) as data_file:
    authentication = json.load(data_file)

service.login(authentication)

while True:
    events = service.get_events()
    if events[0]:
        print("!!!!!")
        print(events[0].chat_event.user_index)
    time.sleep(service.config['lp_idle_time'])

