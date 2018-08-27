import logging
import time

import sys

from event import ChatMessageEvent, UserDropEvent, UserPasswordChangedEvent, ChatInitEvent
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
            if isinstance(event, ChatInitEvent):
                self.handle_entered_room(event.team_index, event.room_index)

            elif isinstance(event, ChatMessageEvent):
                chat = self.service.get_chat_summary(event.room_index,
                                                     event.msg_index)
                if chat:
                    self.handle_chat(event.team_index, event.room_index, chat)

            elif isinstance(event, UserDropEvent) \
                    and self.service.my_index == event.user_index:
                logger.error("봇 계정이 탈퇴되었습니다.")
                sys.exit()
            elif isinstance(event, UserPasswordChangedEvent) \
                    and self.service.my_index == event.user_index:
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
                self.error_count += 1
                if self.error_count > 3:
                    logger.error("오류가 발생했습니다. 프로그램을 종료합니다.")
                    sys.exit()
                else:
                    logger.error("오류가 발생했습니다.")
                    time.sleep(5)

    def handle_entered_room(self, team_index, room_index):
        raise NotImplementedError()

    def handle_chat(self, team_index, room_index, chat):
        raise NotImplementedError()


class TextBot(BaseBot):
    def handle_entered_room(self, team_index, room_index):
        self.service.post_chat(team_index, room_index, "안녕하세요. 저는 샘플 봇입니다.")

    def handle_chat(self, team_index, room_index, chat):
        if chat and chat.content == "Hello":
            self.service.post_chat(team_index, room_index, "World")


class ButtonBot(BaseBot):
    def __init__(self, service):
        super(ButtonBot, self).__init__(service)
        self.buttons = [
            {"type": "text", "id": "bottom", "button_text": "하단 버튼 예시", "response_text": "하단 버튼을 보여주세요."},
            {"type": "text", "id": "calendar_button", "button_text": "달력 예시", "response_text": "달력을 보여주세요."},
            {"type": "text", "id": "range_calendar_button", "button_text": "범위 달력 예시", "response_text": "범위 달력을 보여주세요."}
        ]
        self.test_extras = {
            "2": {
                'type': 'bot',
                'message_buttons': [
                    {"type": "url", "button_text": "팀업 홈페이지", "url": "https://tmup.com"},
                    {"type": "url", "button_text": "챗봇 가이드 문서",
                     "url": "http://cf-xdn.altools.co.kr/teamUP/TeamUP_develop_chatbot_guide_v2.pdf"}
                ],
                'scroll_buttons': self.buttons
            }
        }

    def handle_entered_room(self, team_index, room_index):
        self.service.post_chat(team_index, room_index, "안녕하세요. 저는 샘플 봇입니다.", self.test_extras)

    def handle_chat(self, team_index, room_index, chat):
        if chat.content == "?":
            self.service.post_chat(team_index, room_index, "안녕하세요. 저는 샘플 봇입니다.", self.test_extras)

        elif chat.response_id == "bottom":
            extras = {
                "2": {
                    'type': 'bot',
                    'bottom': {
                        'type': 'button',
                        'buttons': self.buttons
                    }
                }
            }
            self.service.post_chat(team_index, room_index, "하단 버튼을 보여드리겠습니다.", extras)

        elif chat.response_id == "calendar_button":
            extras = {
                "2": {
                    'type': 'bot',
                    'bottom': {
                        'id': 'test_calendar',
                        'type': 'calendar',
                        'range': False
                    }
                }
            }

            self.service.post_chat(team_index, room_index, "달력을 보여드리겠습니다.", extras)

        elif chat.response_id == "range_calendar_button":
            extras = {
                "2": {
                    'type': 'bot',
                    'bottom': {
                        'id': 'test_range_calendar',
                        'type': 'calendar',
                        'range': True
                    }
                }
            }

            self.service.post_chat(team_index, room_index, "범위 달력을 보여드리겠습니다.", extras)

        elif chat.response_id == "test_calendar":
            extras = {
                "2": {
                    'type': 'bot',
                    'scroll_buttons': self.buttons
                }
            }
            self.service.post_chat(team_index, room_index, "{} 날짜를 선택해 주셨네요.".format(chat.content), extras)

        elif chat.response_id == "test_range_calendar":
            extras = {
                "2": {
                    'type': 'bot',
                    'scroll_buttons': self.buttons
                }
            }
            split_result = chat.content.split("~")
            range_start = split_result[0]
            range_end = split_result[1]
            content = "{} 부터 {} 날짜를 선택해 주셨네요.".format(range_start, range_end)
            self.service.post_chat(team_index, room_index, content, extras)
