from bson import ObjectId
from flask import render_template, redirect, request
from printermood import app
from flask.ext.pymongo import PyMongo
from printermood.forms import UserForm
from printermood.lifx_api import get_lights


mongo = PyMongo(app)


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
    faces = mongo.db.faces.find()
    data = {
        'faces': faces,
        'menu_items': _get_menu_items()
    }
    return render_template('face_list.html', **data)
