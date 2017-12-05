import logging
import threading
import time

import sys

from event import ChatMessageEvent, UserDropEvent, UserPasswordChangedEvent
from thread_pool import ThreadPool

logger = logging.getLogger("teamup-bot")

class BaseBot:
    def __init__(self, service):
        self.service = service
        self.error_count = 0
        self.thread_pool = ThreadPool()

    # thread-safe 하다고 나와있긴 하지만 보장이 되는지 고민해 봐야함
    # callback 패턴으로 바꾸는 것 고려
    def handle_event(self, events):
        for event in events:
            if isinstance(event, ChatMessageEvent):
                # TODO 에러 처리
                chat = self.service.get_chat_summary(event.room_index,
                                                     event.msg_index)

                self.handle_chat(event.team_index, event.room_index, chat)

            # TODO 나인지 확인해줘야 할듯.
            elif isinstance(event, UserDropEvent):
                logger.error("봇 계정이 탈퇴되었습니다.")
                sys.exit()
            elif isinstance(event, UserPasswordChangedEvent):
                logger.error("봇 계정의 비밀번호가 바뀌었습니다.")
                sys.exit()

    def run(self):
        while True:
            try:
                events = self.service.get_events()
                if events:
                    self.thread_pool.add_task(self.handle_event, events)
                time.sleep(self.service.config['lp_idle_time'])
            except Exception as e:
                # TODO status code 를 확인하고 이 로직을 타야할지?
                self.error_count += 1
                if self.error_count > 3:
                    logger.error("오류가 발생했습니다. 프로그램을 종료합니다.")
                    sys.exit()
                else:
                    logger.error("오류가 발생했습니다.")
                    time.sleep(5)

    def handle_chat(self, team_index, room_index, chat):
        raise NotImplementedError()


class TextBot(BaseBot):
    def handle_chat(self, team_index, room_index, chat):
        if chat and chat.content == "Hello":
            self.service.post_chat(team_index, room_index, "World")


class ButtonBot(BaseBot):
    def __init__(self, service):
        super(ButtonBot, self).__init__(service)
        self.test_extras = [
            {
                'version': 1,
                'type': 'answer',
                'msg_buttons': [
                    {"type": "text", "text": "텍스트 버튼"},
                    {"type": "url", "text": "구글", "url": "https://www.google.com"}
                ]
            }
        ]

    def handle_chat(self, team_index, room_index, chat):
        if chat and chat.content == "Hello":
            self.service.post_chat(team_index, room_index, "World", self.test_extras)
