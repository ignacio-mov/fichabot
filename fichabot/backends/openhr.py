import os

import requests
from datetime import date

URL_FICHAJE = os.environ["FICHAJE"]
URL_FICHAJE_MANUAL = os.environ["FICHAJE_MANUAL"]


def send_fichaje(user, password):
    url = f'{URL_FICHAJE}/ficha'
    r = requests.post(url, auth=(user, password))
    if not r.ok:
        raise ValueError('Invalid User-password')


def get_proyectos(user, password):
    url = f'{URL_FICHAJE}/proyectos'
    r = requests.get(url, auth=(user, password))
    if not r.ok:
        raise ValueError('Invalid User-password')
    # TODO devolver un objeto dataclass
    return r.json()['proyectos']


def imputado(user, password):
    return imputaciones(user, password)[str(date.today().day)]


def imputaciones(user, password):
    url = f'{URL_FICHAJE}/imputaciones'
    r = requests.get(url, auth=(user, password))
    if not r.ok:
        raise ValueError('Invalid User-password')
    return r.json()['imputado']


def imputa(user, password, proyecto):
    url = f'{URL_FICHAJE}/imputacion'
    r = requests.post(url, auth=(user, password), data={'proyecto': proyecto})
    if not r.ok:
        raise ValueError('Invalid User-password')
