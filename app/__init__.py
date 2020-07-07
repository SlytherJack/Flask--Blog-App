import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.users.routes import users
from app.main.routes import main
from app.posts.routes import posts


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fe69ced23ce91aec103f3c0f252c4b81'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_HOST_PASS')
mail = Mail(app)

app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(posts)

from app import routes
