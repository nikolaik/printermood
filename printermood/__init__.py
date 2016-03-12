from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app)

import printermood.views  # flake8: noqa
