import os

TOKEN = os.environ['TOKEN']
DOMAIN_NAME = os.environ['DOMAIN_NAME']
INTERNAL_DOMAIN = os.environ["INTERNAL_NAME"]
SCHEDULER_URL = os.environ['SCHEDULER_URL']

TIMEZONE = os.environ['TIMEZONE']
INICIO_JORNADA = {'day_of_week': 'mon-fri', 'hour': '8', 'minute': '0', 'jitter': 15 * 60}
JORNADA = {'hours': 9, 'minutes': 0}

LOG_LEVEL = os.environ['LOG_LEVEL']


class Config:
    """App configuration."""
    SCHEDULER_TIMEZONE = TIMEZONE
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOB_DEFAULTS = {'misfire_grace_time': 15 * 60}
    SQLALCHEMY_DATABASE_URI = os.environ['USER_DB']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
