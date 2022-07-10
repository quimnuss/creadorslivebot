import asyncio
import curlify
import requests
import typer

from services.twitch import Twitch
from config.config import *

app = typer.Typer()


async def subscribe(twitch_username: str = TWITCH_USERNAME):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    channel_id = await twitch.get_channel_id_from_username(username=twitch_username)

    esubtype = 'channel.follow'

    try:
        response = await twitch.event_subscribe(
            esubtype=esubtype, channel_id=channel_id)
        print(f"Status {response.status_code}. Body: {response.json()}")
    except requests.HTTPError as e:
        print(f"Error request: {e.request}")
        curl_request = curlify.to_curl(e.request)
        print(f"Curl version: {curl_request}")
    except Exception as e:
        print(
            f"Error subscribing to {esubtype} response code: {e}")

        raise e


async def check_subscriptions():
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)
    esublist = await twitch.get_event_subscriptions()

    logging.info(esublist)


@app.command()
async def ttvsubscribe(twitch_username: str = TWITCH_USERNAME):
    asyncio.run(subscribe(twitch_username))


@app.command()
def unsubscribe(twitch_username: str):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    channel_id = twitch.get_channel_id_from_username(username=twitch_username)
    channel_id = int(channel_id)

    esublist = twitch.get_event_subscriptions()

    # delete all event subscriptions
    logging.info(esublist)
    for esub in esublist.data:
        logging.info(
            f'channel_id {channel_id} : broadcaster_id {esub.condition.broadcaster_user_id}')

        if esub.condition.broadcaster_user_id == channel_id:
            response = twitch.delete_event_subscription(esub.id)
            if response.status_code == 204:
                logging.info(f'Deleted subscription {esub.id}')
                return response
            else:
                response.raise_for_status()
                logging.info(
                    f'response: {response.status_code} {response.json()}')
                return response


@app.command()
def unsubscribe_all():
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    esublist = twitch.get_event_subscriptions()

    # delete all event subscriptions
    logging.info(esublist)
    for esub in esublist.data:
        response = twitch.delete_event_subscription(esub.id)
        if response.status_code == 204:
            logging.info(f'Deleted subscription {esub.id}')


@app.command()
def ttv_check_subscriptions():
    asyncio.run(check_subscriptions())


if __name__ == '__main__':
    app()

# c = curlify.to_curl(response.request)
# print(c)
# import ipdb
# ipdb.set_trace()
