from flask import Flask
from fichabot.config import TOKEN, DOMAIN_NAME, Config, LOG_LEVEL

app = Flask(__name__)
app.config.from_object(Config())

from fichabot.backends.database import db
from fichabot.backends.teleflask import CallbackBot

bot = CallbackBot(TOKEN, app=app, hostname=DOMAIN_NAME)

# inicializa la app de flask, bot, BBDD y scheduler
# Añadimos las acciones y rutas a la app al importarlas
from fichabot import status, debug, actions

db.init_app(app)

app.logger.setLevel(LOG_LEVEL)
