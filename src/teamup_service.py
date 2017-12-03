from oauthlib.oauth2 import LegacyApplicationClient, MissingTokenError
from requests_oauthlib import OAuth2Session
import requests

event_host = 'https://test-ev.tmup.com'
auth_host = 'https://test-auth.tmup.com'
edge_host = 'https://test-edge.tmup.com'

class Chat:
    def __init__(self, chat_index, response_json):
        self.index = chat_index
        self.user_index = response_json['user']
        self.chat_type = response_json['type']
        self.content = response_json['content']

    def __str__(self):
        return "Msg Index : {}\nUser Index : {}\nType : {}\nContent : {}\n".format(self.index, self.user_index,
                                                                                   self.chat_type, self.content)


class ChatEvent:
    def __init__(self, json):
        self.team_index = json.get('team')
        self.room_index = json.get('room')
        self.user_index = json.get('user')
        self.msg_index = json.get('msg')
        self.room_name = json.get('name')


class Event:
    def __init__(self, response_json):
        self.type = response_json['type']
        if response_json['chat']:
            self.chat_event = ChatEvent(response_json['chat'])


class TeamUpService:
    def __init__(self):
        self.auth = None
        self.client = None
        self.config = {
            'lp_idle_time': 1,
            'lp_wait_timeout': 30
        }

    def login(self, auth):
        # TODO 실패 처리
        self.config = self.get_event_config()

        # TODO 6개월 뒤엔 다시 아디, 비번으로 로그인 해야해서 일단 저장
        self.auth = auth
        client_id = auth['client_id']
        client_secret = auth['client_secret']
        username = auth['username']
        password = auth['password']

        extra = {
            'client_id': client_id,
            'client_secret': client_secret
        }

        def token_saver(token):
            self.client.token = token

        # TODO refresh Token 잘 동작하는지 확인 필요
        self.client = OAuth2Session(
            client=LegacyApplicationClient(client_id=client_id),
            auto_refresh_url='https://auth.tmup.com/oauth2/token',
            auto_refresh_kwargs=extra,
            token_updater=token_saver
        )

        try:
            self.client.fetch_token(token_url='https://test-auth.tmup.com/oauth2/token',
                                    timeout=self.config['lp_wait_timeout'],
                                    username=username, password=password, client_id=client_id, client_secret=client_secret)
        except MissingTokenError:
            print("로그인에 실패했습니다.")
            raise

    def get_event_config(self):
        response = requests.get(event_host + '/', timeout=self.config['lp_wait_timeout'])

        if response.status_code == 200:
            return response.json()

    def get_events(self):
        response = self.client.get(url=event_host + '/v3/events', timeout=self.config['lp_wait_timeout'])

        if response.json()['events']:
            return [Event(event_json) for event_json in response.json()['events']]
        else:
            return []

    def get_chat_summary(self, room_index, chat_index):
        response = self.client.get(
            edge_host + '/v3/message/summary/{}/{}/1'.format(room_index, chat_index),  # 1 은 confirm
            timeout=self.config['lp_wait_timeout']
        )

        if response.status_code == 200:
            return Chat(chat_index, response.json())

    def post_chat(self, room_index, content, extras=None):
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        if extras:
            json = {'content': content, 'extras': extras}
        else:
            json = {'content:': content}

        response = self.client.post(
            edge_host + '/v3/message/{}/{}'.format(room_index, 1),  # 1 은 타입
            headers=headers,
            json=json,
            timeout=self.config['lp_wait_timeout']
        )

# 403 나오면 확인하는 용도로 사용
    def am_i_bot(self, team_index):
        my_info_response = self.client.get(
            auth_host + '/v1/user',
            timeout=self.config['lp_wait_timeout']
        )
        user_index = my_info_response.json()['index']

        response = self.client.get(
            auth_host + '/v1/user/{}/team/{}'.format(user_index, team_index),
            timeout=self.config['lp_wait_timeout']
        )

        return response.json()['is_bot']

