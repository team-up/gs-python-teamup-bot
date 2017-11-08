import threading
from teamup_service import TeamUpService

import time

service = TeamUpService()
service.login()

while True:
    events = service.get_events()
    if events[0]:
        print("!!!!!")
        print(events[0].chat_event.user_index)
    time.sleep(service.config['lp_idle_time'])

