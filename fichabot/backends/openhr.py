import os

import requests

URL_FICHAJE = os.environ["FICHAJE"]
URL_FICHAJE_MANUAL = os.environ["FICHAJE_MANUAL"]


def send_fichaje(user, password):
    url = f'{URL_FICHAJE}/ficha'
    r = requests.post(url, data={'user': user, 'password': password})
    if not r.ok:
        raise ValueError('Invalid User-password')
