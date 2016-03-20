import os
from pmweb import socketio, app

host = os.getenv('FLASK_HOST', '127.0.0.1')
socketio.run(app, debug=True, host=host)
