import os
import secrets
from PIL import Image
from flask import (
    render_template,
    url_for,
    flash,
    request,
    redirect,
    abort
)
from app.forms import (
    RegistrationForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
    PostForm
)
from app import app, db, bcrypt, mail
from app.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return '<h1>About Page</h1>'


@app.route('/register', methods=['GET', 'POST'])
def register():
    # current_user is fetched from flask_login module, Authenticated User will not be able to register
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, you may now login', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # If a query parameter named next is found
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')


    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    # This method comes from flask_login module
    logout_user()
    return redirect(url_for('home'))


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


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            file_name = save_picture(form.picture.data)
            current_user.image_file = file_name

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated successfully')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


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
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email and no change
    '''

    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    # We don't want the user to be logged in here
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            flash('No such user exists in our database', 'warning')
            return redirect(url_for('login'))

        send_reset_email(user)

        flash('An email with instructions to reset your password has been sent.', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an expired token', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, you may now login', 'success')
        return redirect(url_for('login'))


    return render_template('reset_token.html', title='Reset Password', form = form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post', form=form)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        'create_post.html',
        title='Update Post',
        form=form, legend='Update Post'
    )


@app.route("/delete_post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))
