import logging
from urllib.error import HTTPError
import requests

from api.schemas import EventSubList


class Twitch:

    def __init__(self, app_id, app_secret, callback_url):
        self.app_id = app_id
        self.app_secret = app_secret
        self.auth_url = 'https://id.twitch.tv/oauth2/token'
        self.base_url = 'https://api.twitch.tv/helix'
        self.sub_url = f'{self.base_url}/eventsub/subscriptions'
        self.token = None
        self.callback_url = callback_url

    def update_token(self):
        # TODO refresh token
        params = {'client_id': self.app_id, 'client_secret': self.app_secret,
                  'grant_type': 'client_credentials'}
        response = requests.post(
            url=self.auth_url, data=params, timeout=10)

        response.raise_for_status()

        self.token = response.json()['access_token']
        return self.token

    def auth_headers(self):
        if not self.token:
            self.update_token()
        headers = {
            'Client-Id': self.app_id,
            'Authorization': f'Bearer {self.token}'
        }
        return headers

    async def get_channel_id_from_username(self, username):
        response = await requests.get(
            url=f'{self.base_url}/users', headers=self.auth_headers(), params={'login': username}, timeout=10)

        response.raise_for_status()

        # TODO validate instead of assuming?
        channel_id = response.json()['data'][0]['id']
        return channel_id

    def get_event_subscriptions(self):
        response = requests.get(self.sub_url, headers=self.auth_headers())
        response.raise_for_status()
        esublist = EventSubList(**response.json())
        return esublist

    def delete_event_subscription(self, esub_id):

        response = requests.delete(
            self.sub_url, headers=self.auth_headers(), json={'id': str(esub_id)})
        response.raise_for_status()
        return response

    async def event_subscribe(self, esubtype, channel_id):
        """ type esubtype event subscription to channel channel_id

            get channel_id with get_channel_id_from_username
            esubtypes are here:
        """

        data = {
            'client_id': self.app_id,
            "type": esubtype,
            "version": "1",
            "condition": {"broadcaster_user_id": channel_id},
            "transport": {"method": "webhook", "callback": self.callback_url, "secret": self.app_secret}
        }

        response = await requests.post(
            self.sub_url, headers=self.auth_headers(), json=data, timeout=10)

        logging.info(response.json())
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logging.error(f'Callback url:{self.callback_url}')
            raise e

        return response
