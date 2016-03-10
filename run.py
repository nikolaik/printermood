import os
from printermood import app

host = os.getenv('FLASK_HOST', '127.0.0.1')
app.run(debug=True, host=host)
