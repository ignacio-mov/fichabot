from pytgbot.api_types.receivable.updates import Update
from teleflask.messages import TextMessage

from fichabot.backends.scheduler import scheduler
from fichabot.backends.database import User
from fichabot import bot
from fichabot.config import INICIO_JORNADA
from fichabot.constants import COMMAND_START, COMMAND_STOP, COMMAND_STATUS, COMMAND_AUTOLOGIN, ENDPOINT_JORNADA


@bot.command(COMMAND_START)
def start(update: Update, _):
    """Da la bienvenida a un usuario y lo registra en la app"""
    chat_id = update.message.chat.id
    scheduler.add_job(f'buenos_dias_{chat_id}', replace_existing=True, endpoint=f'{ENDPOINT_JORNADA}/{chat_id}',
                      trigger='cron', **INICIO_JORNADA)

    mensaje = f"""
    <b>¡Hola!</b> ¡Bienvenido a @{bot.username}!
    
    A partir de ahora, cada mañana a las 8:00 recibirás un recordatorio para que fiches.
    Una vez fichado, recibirás otro recordatorio a las 9 horas.
    
    Si deseas parar estos mensajes escribe /{COMMAND_STOP}"""

    return TextMessage(mensaje, parse_mode="html")


@bot.command(COMMAND_STOP)
def stop(update: Update, _):
    """Elimina el trigger del usuario"""
    chat_id = update.message.chat.id
    scheduler.remove_job(f'buenos_dias_{chat_id}')
    return TextMessage(f"Ya has sido dado de baja. Si quieres volver a usar el bot, escribe /{COMMAND_START}."
                       f"¡Hasta la vista!",
                       parse_mode="html")


@bot.command(COMMAND_STATUS)
def status(update: Update, *_):
    """Fuerza el envío de un mensaje para fichar"""
    data = {}
    chat_id = update.message.chat.id

    # USUARIO
    usuario = User.get(chat_id)
    if usuario:
        data['usuario'] = str(usuario)

    # PROGRAMACION DIARIA
    programacion = scheduler.get_job(f'buenos_dias_{chat_id}')
    data['programacion'] = bool(programacion)

    # FIN DE JORNADA PENDIENTE
    fichaje_pendiente = scheduler.get_job(f'fichar_salida-{chat_id}')
    if fichaje_pendiente:
        data['fichaje_pendiente'] = fichaje_pendiente

    return str(data)


@bot.command(COMMAND_AUTOLOGIN)
def auto_login(update: Update, text: str):
    """Da de alta un usuario para los fichaje automáticos"""
    chat_id = update.message.chat.id

    # Si no se indica usuario y contraseña se borra el fichaje automático
    if not text:
        User.delete(chat_id)
        return TextMessage("Se han desactivado los fichajes automáticos")

    usuario, password = text.split(' ', maxsplit=1)

    # Vemos si el usuario existe o si no lo creamos
    User(id=chat_id, name=usuario, password=password).upsert()

    # Se devuelve un aviso con la información para desactivarlos
    command = update.message.entities[0]
    return f"Se han activado los fichajes automáticos. Escribe {command} sin argumentos para cancelarlo"
