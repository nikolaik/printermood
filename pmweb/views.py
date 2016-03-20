import base64
import datetime

from bson import ObjectId, Binary
from flask import render_template, redirect, request, jsonify
from pmweb.utils import get_mime_type, get_data_url
from pmweb import socketio, app
from flask.ext.pymongo import PyMongo
from pmweb.forms import UserForm, ImageForm
from pmweb.lifx_api import get_lights


mongo = PyMongo(app)


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    app.logger.debug(error.message, error.payload)
    return response


def _get_menu_items():
    menu_items = [
        {'label': 'Home', 'url': '/'},
        {'label': 'Users', 'url': '/users/'},
        {'label': 'Faces', 'url': '/faces/'},
    ]
    for item in menu_items:
        if item['url'] == request.path:
            item['is_active'] = True
    return menu_items


@app.route('/', methods=['GET', 'POST'])
def home_page():
    form = UserForm()
    if form.validate_on_submit():
        mongo.db.users.insert_one(form.data)
        return redirect('/')

    data = {
        'lights': get_lights(),
        'users': mongo.db.users.find(),
        'moods': mongo.db.moods.find(),
        'form': form,
        'menu_items': _get_menu_items()
    }
    return render_template('index.html', **data)


@app.route('/users/')
def user_list():
    form = UserForm()
    users = mongo.db.users.find()

    data = {
        'users': users,
        'form': form,
        'menu_items': _get_menu_items()
    }

    return render_template('user_list.html', **data)


@app.route('/user/<user_id>/')
def user_detail(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)}),
    data = {
        'user': user[0],
        'menu_items': _get_menu_items()
    }

    return render_template('user_detail.html', **data)


@app.route('/faces/')
def face_list():
    face_objects = mongo.db.images.find()
    faces = []
    for f in face_objects:
        faces.append({
            'id': f['_id'],
            'url': get_data_url(f),
            'timestamp': f['timestamp']
        })
    data = {
        'face_list': faces,
        'menu_items': _get_menu_items()
    }
    return render_template('face_list.html', **data)


@app.route('/process/', methods=['PUT'])
def process():
    form = ImageForm(csrf_enabled=False)

    if not form.validate_on_submit():
        raise InvalidAPIUsage({'result': 'Less than OK', 'errors': form.errors})

    image_data = form.data['image'].read()

    timestamp = datetime.datetime.now()
    mime_type = get_mime_type(image_data)

    image_doc = {
        'file': Binary(image_data),
        'timestamp': timestamp,
        'mime_type': mime_type
    }
    res = mongo.db.images.insert_one(image_doc)

    # notify clients
    client_data = {
        'id': str(res.inserted_id),
        'data': base64.b64encode(image_data).decode('ascii'),
        'mime_type': mime_type,
        'timestamp': timestamp.isoformat(),
    }

    socketio.emit('image-new', client_data)

    return jsonify(**{'result': 'OK', 'id': str(res.inserted_id)})


@app.route('/process/bulk/', methods=['PUT'])
def process_bulk():
    """Process multiple images in one go"""
    # TODO stub


@socketio.on('message')
def handle_message(message):
    if isinstance(message, dict):
        print('received message: ' + '\n'.join(['{}: {}'.format(k, v) for k, v in message.items()]))
    else:
        print('received message: ' + message)
