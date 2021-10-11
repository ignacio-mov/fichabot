from pytgbot.api_types.receivable.updates import Message

from datetime import datetime, timedelta
from pytz import timezone

from fichabot.config import DOMAIN_NAME, TIMEZONE
from fichabot.constants import ENDPOINT_FICHAJE


def confirmacion_fichaje():
    return f'Fichaje registrado a las {format_time()}'


def format_time(datetime_var: datetime = None) -> str:
    if not datetime_var:
        datetime_var = datetime.now(timezone(TIMEZONE))
    return str(datetime_var.time())[:5]


def build_url_fichaje(chat_id, message_id, inicio=None):

    url = f'https://{DOMAIN_NAME}{ENDPOINT_FICHAJE}?chat_id={chat_id}&message_id={message_id}'
    if inicio:
        url += f"&inicio={inicio}"

    return url


def dentro_de(**kwargs):
    return datetime.now(timezone(TIMEZONE)) + timedelta(**kwargs)
