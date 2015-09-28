import requests
from app.settings import LIFX_TOKEN


# ref: http://api.developer.lifx.com/
LIFX_API_URL = 'https://api.lifx.com/v1/'


def get_lights():
    headers = {"Authorization": "Bearer %s" % LIFX_TOKEN}
    url = '{}lights/all'.format(LIFX_API_URL)
    response = requests.get(url, headers=headers)

    return response.json()


def toggle_light(light):
    headers = {"Authorization": "Bearer %s" % LIFX_TOKEN}
    url = '{}lights/id:{}/toggle'.format(LIFX_API_URL, light['id'])
    response = requests.post(url, headers=headers)

    return response.json()