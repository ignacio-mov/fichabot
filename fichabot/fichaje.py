from flask import request
from pytgbot.api_types.receivable.updates import Update
from pytgbot.api_types.sendable.reply_markup import InlineKeyboardMarkup, InlineKeyboardButton
from werkzeug.utils import redirect

from fichabot import botapp, app
from fichabot.backends.database import User
from fichabot.backends.openhr import URL_FICHAJE_MANUAL, send_fichaje
from fichabot.backends.scheduler import scheduler
from fichabot.config import JORNADA
from fichabot.constants import ENDPOINT_FICHAR, ENDPOINT_JORNADA, ENDPOINT_FICHAJE, \
    CALLBACK_INICIO, CALLBACK_DESCANSAR, CALLBACK_FICHAR
from fichabot.imputacion import preguntar_imputacion
from fichabot.utils import build_url_fichaje, confirmacion_fichaje, dentro_de, format_time, process_callback


@app.route(f'{ENDPOINT_JORNADA}/<chat_id>')
def send_question(chat_id):
    """Envía a un chat un mensaje para que fiche el inicio de jornada"""

    # Envía el mensaje primero y lo guardamos para adjuntarlo al callback url
    message = botapp.bot.send_message(chat_id, 'Buenos días, ¿quieres fichar hoy?')
    message_id = message.message_id

    # Envía confirmación de fichaje automático o el enlace para fichar
    if User.get(chat_id):
        payload_fichaje = {'callback_data': CALLBACK_INICIO}
    else:
        payload_fichaje = {'url': build_url_fichaje(chat_id, message_id, inicio=True)}

    # Creamos un teclado con las respuestas
    teclado = InlineKeyboardMarkup([[
        InlineKeyboardButton('Sí, quiero fichar hoy', **payload_fichaje),
        InlineKeyboardButton('No, hoy no trabajo', callback_data=CALLBACK_DESCANSAR)
    ]])

    # Adjuntamos el teclado al mensaje
    botapp.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=teclado)
    return 'OK'


@botapp.callback(CALLBACK_DESCANSAR)
def descansar(update: Update, _):
    """Limpia el mensaje para fichar"""
    message, _ = process_callback(update, botapp.bot)

    botapp.bot.edit_message_text('No se programan fichajes para hoy', reply_markup=None,
                                 chat_id=message.chat.id, message_id=message.message_id)
    return None


@botapp.callback(CALLBACK_INICIO)
def callback_iniciar_jornada(update: Update, _):
    """ Realiza el fichaje y programa el fin de la jornada"""
    message, _ = process_callback(update, botapp.bot)

    fichaje_automatico(message.chat.id, message_id=message.message_id)
    programar_fin_jornada(message.chat.id)


@app.route(ENDPOINT_FICHAJE, methods=['GET'])
def fichar_url():
    """Limpia el enlace una vez fichado y redirige a la página de fichajes"""
    message_id = int(request.args.get('message_id'))
    chat_id = request.args.get('chat_id')

    botapp.bot.edit_message_text(confirmacion_fichaje(), reply_markup=None, chat_id=chat_id, message_id=message_id)

    if request.args.get('inicio'):
        programar_fin_jornada(chat_id)
        app.logger.info('programado normal')
    else:
        preguntar_imputacion(chat_id)

    return redirect(URL_FICHAJE_MANUAL)


def programar_fin_jornada(chat_id):
    """Programa el aviso de fin de jornada"""
    trigger_id = f'fichar_salida-{chat_id}'
    date = dentro_de(**JORNADA, jitter=15 * 60)

    scheduler.add_job(trigger_id, trigger='date', run_date=date.isoformat(),
                      endpoint=f'{ENDPOINT_FICHAR}/{chat_id}')
    texto = f'Programado fin de jornada a las {format_time(date)}'
    botapp.bot.send_message(text=texto, chat_id=chat_id)


@app.route(f'{ENDPOINT_FICHAR}/<chat_id>')
def fichar(chat_id, message_id=None):
    """
    Realiza un fichaje

    Puede ser como respuesta a un mensaje previo o como un nuevo mensaje
    """
    if (user := User.get(chat_id)) and user.auto:
        fichaje_automatico(chat_id, message_id)
        preguntar_imputacion(chat_id)
    else:
        confirma_fin_jornada(chat_id, message_id)


def fichaje_automatico(chat_id, message_id):
    """Realiza un fichaje automático"""

    user = User.get(chat_id)
    send_fichaje(user)
    if message_id:
        botapp.bot.edit_message_text(confirmacion_fichaje(), reply_markup=None, chat_id=chat_id, message_id=message_id)
    else:
        botapp.bot.send_message(chat_id, confirmacion_fichaje())


def confirma_fin_jornada(chat_id, message_id=None, text='Pulsa para fichar'):
    """Envía el mensaje con el enlace para fichar"""

    # Se envía el mensaje
    if not message_id:
        mensaje = botapp.bot.send_message(chat_id, text)
        message_id = mensaje.message_id

    # Y se adjunta el enlace para fichar
    if User.get(chat_id):
        payload_fichaje = {'callback_data': CALLBACK_FICHAR}
    else:
        payload_fichaje = {'url': build_url_fichaje(chat_id, message_id, inicio=False)}
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton('Fichar', **payload_fichaje)]])
    botapp.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=teclado)


@botapp.callback(CALLBACK_FICHAR)
def callback_fin_jornada(update: Update, _):
    message, _ = process_callback(update, botapp.bot)

    fichaje_automatico(message.chat.id, message.message_id)
    preguntar_imputacion(message.chat.id)
