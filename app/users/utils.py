from PIL import Image
import os
import secrets
from app import app, mail
from flask_mail import Message

def save_picture(form_picture):
    hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    file_name = hex + f_ext
    file_path = os.path.join(app.root_path, 'static/profile_pics', file_name)

    # Resizing image using Pillow library
    i = Image.open(form_picture)
    i.thumbnail((125, 125))
    i.save(file_path)

    return file_name

def send_reset_email(user):
    '''
        Token generated here will not be of a logged-in user,
        instead, a user will be queried by email and a token
        will be generated from his ID
    '''
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                    sender='noreply@demo.com',
                    recipients=[user.email])

    # _external is used because we want to show absolute URL
    msg.body = f'''To reset your password, visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}

    If you did not make this request, simply ignore this email and no change
        '''

    mail.send(msg)

