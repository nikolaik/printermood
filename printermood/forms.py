from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField
from wtforms.validators import DataRequired


class UserForm(Form):
    name = StringField('name', validators=[DataRequired()])


class ImageForm(Form):
    ALLOWED_FILE_EXTENSIONS = ['png', 'jpg', 'jpeg']
    ERROR_MSG = 'Invalid file extension, not {}.'.format(', '.join(ALLOWED_FILE_EXTENSIONS))

    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_FILE_EXTENSIONS, ERROR_MSG)
    ])
