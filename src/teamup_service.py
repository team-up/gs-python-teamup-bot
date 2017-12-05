import sys
import requests

from event import EventFactory

event_host = 'https://dev-ev.tmup.com'
auth_host = 'https://dev-auth.tmup.com'
edge_host = 'https://dev-edge.tmup.com'


class Chat:
    def __init__(self, chat_index, response_json):
        self.index = chat_index
        self.user_index = response_json['user']
        self.chat_type = response_json['type']
        self.content = response_json['content']

    def __str__(self):
        return "Msg Index : {}\nUser Index : {}\nType : {}\nContent : {}\n".format(self.index, self.user_index,
                                                                                   self.chat_type, self.content)


class TeamUpService:
    def __init__(self, configuration):
        # TODO 각 필드별로 설명 써주면 좋을 듯 (이게 컨벤션인듯?)
        self.auth = configuration
        self.client = None
        self.token = None
        self.config = {
            'lp_idle_time': 1,
            'lp_wait_timeout': 30
        }

    def login(self):
        # TODO 실패 처리
        # TODO add hooks
        self.config = self.get_event_config()
        self.client = self.login_with_password()

    def login_with_password(self):
        client_id = self.auth['client_id']
        client_secret = self.auth['client_secret']
        username = self.auth['username']
        password = self.auth['password']

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }

        auth_dict = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password
        }

        response = requests.post(url=auth_host + "/oauth2/token",
                      headers=headers,
                      data=auth_dict)

        self.token = response.json()
        session = requests.session()
        session.headers = {'Authorization': "{} {}".format(self.token['token_type'], self.token['access_token'])}
        return session

    def refresh_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }

        auth_dict = {
            'grant_type': 'refresh_token',
            'refresh_token': self.token['refresh_token'],
        }

        response = requests.post(url=auth_host + "/oauth2/token",
                                 headers=headers,
                                 data=auth_dict)

        self.token = response.json()
        self.client.headers = {'Authorization': "{} {}".format(self.token['token_type'], self.token['access_token'])}

    def get_event_config(self):
        response = requests.get(event_host + '/', timeout=self.config['lp_wait_timeout'])

        if response.status_code == 200:
            return response.json()

    def get_events(self):
        response = self.client.get(url=event_host + '/v3/events', timeout=self.config['lp_wait_timeout'])
        print(response)

        if response.json()['events']:
            return [EventFactory.create(event_json) for event_json in response.json()['events']]
        else:
            return []

    def get_chat_summary(self, room_index, chat_index):
        response = self.client.get(
            edge_host + '/v3/message/summary/{}/{}/1'.format(room_index, chat_index),  # 1 은 confirm
            timeout=self.config['lp_wait_timeout']
        )

        if response.status_code == 200:
            return Chat(chat_index, response.json())

    def post_chat(self, team_index, room_index, content, extras=None):
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        if extras:
            json = {'content': content, 'extras': extras}
        else:
            json = {'content': content}

        response = self.client.post(
            edge_host + '/v3/message/{}/{}'.format(room_index, 1),  # 1은 일반, 2는 파일
            headers=headers,
            json=json,
            timeout=self.config['lp_wait_timeout']
        )

        if response.status_code == 403:
            if not self.am_i_bot(team_index):
                print("봇으로 등록되어 있지 않습니다.")
                sys.exit()

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
