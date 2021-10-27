from pytgbot.api_types.receivable.updates import Update
from pytgbot.api_types.sendable.reply_markup import InlineKeyboardButton, InlineKeyboardMarkup

from fichabot import bot
from fichabot.backends.database import User
from fichabot.backends.openhr import imputado, get_proyectos, imputa
from fichabot.constants import CALLBACK_PROYECTOS, CALLBACK_NO_IMPUTAR, CALLBACK_IMPUTAR


def preguntar_imputacion(chat_id):
    user = User.get(chat_id)
    # comprobar usuario validado
    if not user:
        return
    # comprobar si ya ha imputado
    if imputado(user.name, user.password):
        return
    botones = [[InlineKeyboardButton('Ver proyectos', callback_data=f"{CALLBACK_PROYECTOS}"),
               InlineKeyboardButton('No imputar', callback_data=f"{CALLBACK_NO_IMPUTAR}")]]

    if user.last_proyect and user.last_proyect_id:
        callback_last_project = f"{CALLBACK_IMPUTAR} {user.last_proyect} {user.last_proyect_id}"
        botones.insert(0, [InlineKeyboardButton(f'Imputar: {user.last_proyect}', callback_data=callback_last_project)])

    message = bot.bot.send_message(chat_id, '¿Quieres imputar?', reply_markup=InlineKeyboardMarkup(botones))
    return


@bot.callback(CALLBACK_PROYECTOS)
def ver_proyectos_imputar(update: Update, _):

    query = update.callback_query
    bot.bot.answer_callback_query(query.id, text="Procesando solicitud")

    chat_id = update.callback_query.message.chat.id
    message_id = update.callback_query.message.message_id

    user = User.get(chat_id)
    proyectos = get_proyectos(user.name, user.password)
    botones = [[InlineKeyboardButton(p['nombre'], callback_data=f"{CALLBACK_IMPUTAR} {p['nombre']}#{p['valor']}")]
               for p in proyectos]
    botones.append([InlineKeyboardButton('No imputar', callback_data=f"{CALLBACK_NO_IMPUTAR}")])

    bot.bot.edit_message_text('Elige proyecto para imputar:', chat_id=chat_id, message_id=message_id,
                              reply_markup=InlineKeyboardMarkup(botones))
    return


@bot.callback(CALLBACK_NO_IMPUTAR)
def cancela_imputacion(update: Update, _):

    query = update.callback_query
    bot.bot.answer_callback_query(query.id, text="Procesando solicitud")

    chat_id = update.callback_query.message.chat.id
    message_id = update.callback_query.message.message_id

    bot.bot.edit_message_text('No se imputa el día de hoy', reply_markup=None, chat_id=chat_id, message_id=message_id)


@bot.callback(CALLBACK_IMPUTAR)
def confirma_imputacion(update: Update, args: str):

    query = update.callback_query
    bot.bot.answer_callback_query(query.id, text="Procesando solicitud")

    chat_id = update.callback_query.message.chat.id
    message_id = update.callback_query.message.message_id

    nombre, valor = args.split('#')

    user = User.get(chat_id)
    imputa(user.name, user.password, valor)
    bot.bot.edit_message_text(f'Imputado en el proyecto {nombre}', reply_markup=None,
                              chat_id=chat_id, message_id=message_id)

    # Actualizamos el último proyecto imputado
    user.last_proyect = nombre
    user.last_proyect_id = valor
    user.save()

