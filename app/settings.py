DB_ENGINE = 'sqlite:///db.sqlite3'
LIFX_TOKEN = ''
INDICO_API_KEY = ''

try:
    from .local_settings import *
except ImportError:
    pass

