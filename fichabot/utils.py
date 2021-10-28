from datetime import datetime, timedelta
from random import random

from pytz import timezone

from fichabot.backends.database import User
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


def dentro_de(*, jitter=0, **kwargs):
    jitter_time = (random() - 0.5) * 2 * jitter
    kwargs['seconds'] = kwargs.get('seconds', 0) + jitter_time
    return datetime.now(timezone(TIMEZONE)) + timedelta(**kwargs)


def process_callback(update, bot):
    query = update.callback_query
    bot.answer_callback_query(query.id, text="Procesando solicitud")

    message = query.message
    user = User.get(message.chat.id)

    return message, user
