from calendar import Calendar
from datetime import date

from pytgbot.api_types.receivable.updates import Update
from pytgbot.api_types.sendable.reply_markup import InlineKeyboardButton, InlineKeyboardMarkup

from fichabot import botapp
from fichabot.backends.database import User
from fichabot.backends.openhr import is_imputado, get_proyectos, imputa, clear_cache
from fichabot.constants import CALLBACK_PROYECTOS, CALLBACK_NO_IMPUTAR, CALLBACK_IMPUTAR, COMMAND_CIERRE
from fichabot.utils import process_callback


def preguntar_imputacion(chat_id, dia=None):
    clear_cache()

    if dia is None:
        dia = date.today().day

    # comprobar usuario validado
    if not (user := User.get(chat_id)):
        return

    _preguntar_imputacion(user, dia)


@botapp.command(COMMAND_CIERRE)
def imputa_mes(update: Update, _):
    clear_cache()

    chat_id = update.message.chat.id
    # comprobar usuario validado
    if not (user := User.get(chat_id)):
        return "Usuario sin credenciales"

    # Nos quedamos con los días futuros del mes en curso
    hoy = date.today()
    for dia, dia_sem in Calendar().itermonthdays2(hoy.year, hoy.month):
        if dia > hoy.day and dia_sem < 5:
            _preguntar_imputacion(user, dia)


def _preguntar_imputacion(user, dia):
    # comprobar si ya ha imputado
    if is_imputado(user, dia):
        return

    botones = [[boton_ver_proyectos(dia), boton_no_imputar(dia)]]
    if user.last_project and user.last_project_id:
        boton_last_project = boton_imputa_proyecto(user.last_project_id, user.last_project, dia)
        botones.insert(0, [boton_last_project])

    botapp.bot.send_message(user.id, f'¿Quieres imputar el día {dia}?', reply_markup=InlineKeyboardMarkup(botones))
    return


@botapp.callback(CALLBACK_PROYECTOS)
def ver_proyectos_imputar(update: Update, dia):
    message, user = process_callback(update, botapp.bot)

    proyectos = get_proyectos(user)

    botones = [[boton_imputa_proyecto(p.valor, p.nombre, dia)] for p in proyectos]
    botones.append([boton_no_imputar(dia)])

    botapp.bot.edit_message_text(f'Elige proyecto para imputar el día {dia}:', chat_id=message.chat.id,
                                 message_id=message.message_id, reply_markup=InlineKeyboardMarkup(botones))
    return


@botapp.callback(CALLBACK_NO_IMPUTAR)
def cancela_imputacion(update: Update, dia: str):
    message, _ = process_callback(update, botapp.bot)

    botapp.bot.edit_message_text(f'No se imputa el día {dia}', reply_markup=None, chat_id=message.chat.id,
                                 message_id=message.message_id)


@botapp.callback(CALLBACK_IMPUTAR)
def confirma_imputacion(update: Update, args: str):
    message, user = process_callback(update, botapp.bot)

    nombre_proy = next(boton.text
                       for fila in message.reply_markup.inline_keyboard
                       for boton in fila
                       if boton.callback_data.endswith(args))

    id_proy, dia = args.split('#')

    imputa(user, id_proy, dia=dia)
    botapp.bot.edit_message_text(f'Imputado el día {dia} en el proyecto {nombre_proy}', reply_markup=None,
                                 chat_id=message.chat.id, message_id=message.message_id)

    # Actualizamos el último proyecto imputado
    user.last_project = nombre_proy
    user.last_project_id = id_proy
    user.save()


def boton_imputa_proyecto(id_proyecto, nombre, dia):
    return InlineKeyboardButton(nombre, callback_data=f"{CALLBACK_IMPUTAR} {id_proyecto}#{dia}")


def boton_no_imputar(dia):
    return InlineKeyboardButton('No imputar', callback_data=f'{CALLBACK_NO_IMPUTAR} {dia}')


def boton_ver_proyectos(dia):
    return InlineKeyboardButton('Ver proyectos', callback_data=f"{CALLBACK_PROYECTOS} {dia}")
