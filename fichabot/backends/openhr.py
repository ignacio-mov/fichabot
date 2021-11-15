import os
from dataclasses import dataclass
from datetime import date
from functools import cache

import requests

from fichabot.backends.database import User

URL_FICHAJE = os.environ["FICHAJE"]
URL_FICHAJE_MANUAL = os.environ["FICHAJE_MANUAL"]


@dataclass
class Proyecto:
    nombre: str
    valor: str


def clear_cache():
    get_imputaciones.cache_clear()
    get_proyectos.cache_clear()


def send_fichaje(user: User):
    url = f'{URL_FICHAJE}/ficha'
    r = requests.post(url, auth=(user.name, user.password))
    if not r.ok:
        raise ValueError('Invalid User-password')


@cache
def get_proyectos(user: User) -> list[Proyecto]:
    url = f'{URL_FICHAJE}/proyectos'
    r = requests.get(url, auth=(user.name, user.password))
    if not r.ok:
        raise ValueError('Invalid User-password')

    return [Proyecto(**data) for data in r.json()['proyectos']]


def is_imputado(user: User, dia: int = None) -> bool:
    if dia is None:
        dia = date.today().day
    return get_imputaciones(user)[dia]


@cache
def get_imputaciones(user: User) -> dict[int, bool]:
    url = f'{URL_FICHAJE}/imputaciones'
    r = requests.get(url, auth=(user.name, user.password))
    if not r.ok:
        raise ValueError('Invalid User-password')

    # Antes de devolver pasamos los dias a entero
    data = r.json()['imputado']
    return {int(dia): es_imputado for dia, es_imputado in data.items()}


def imputa(user: User, id_proyecto, dia=None):
    url = f'{URL_FICHAJE}/imputacion'
    r = requests.post(url, auth=(user.name, user.password), data={'proyecto': id_proyecto, 'dia': dia})
    if not r.ok:
        raise ValueError('Invalid User-password')
