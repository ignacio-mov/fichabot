from pytgbot.api_types.receivable.updates import Update

from fichabot import app, bot
from fichabot.actions import fichar, send_question, preguntar_imputacion
from fichabot.backends.database import User, db
from fichabot.backends.scheduler import scheduler
from fichabot.constants import COMMAND_JORNADA, COMMAND_FICHA, COMMAND_IMPUTA


@app.route('/users')
def users():
    return {'data': [u.as_dict() for u in User.get_all()]}


@app.route('/reset')
def init_tables():
    db.create_all()
    User.query.delete()
    db.session.commit()
    scheduler.remove_all_jobs()

    return {'data': [u.as_dict() for u in User.get_all()]}


# DEBUG COMMANDS

@bot.command(COMMAND_JORNADA)
def forzar_nuevo_dia(update: Update, *_):
    """Fuerza el envío de un mensaje para fichar el día entero"""
    send_question(update.message.chat.id)


@bot.command(COMMAND_FICHA)
def forzar_fichaje(update: Update, _: str):
    """Fuerza un fichaje individual"""
    fichar(update.message.chat.id)


@bot.command(COMMAND_IMPUTA)
def forzar_imputacion(update: Update, _: str):
    """Fuerza el envío de un mensaje para imputar el día entero"""
    preguntar_imputacion(update.message.chat.id)
