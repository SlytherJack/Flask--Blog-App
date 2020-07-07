from flask import Blueprint, render_template
from app.models import Post

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@main.route('/about')
def about():
    return '<h1>About Page</h1>'

