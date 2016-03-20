import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['nikolaik@gmail.com', 'robert.kolner@gmail.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

THREADS_PER_PAGE = 8

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

LIFX_TOKEN = ''

INDICO_API_KEY = ''

# Mongo DB settings:
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')

try:
    from local_config import *
except ImportError:
    pass
