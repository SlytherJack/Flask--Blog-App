from app import app, db, bcrypt, mail
from app.models import User, Post
from app.users.utils import save_picture, send_reset_email
from app.users.forms import (
    RegistrationForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm
)from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    request,
    redirect,
    abort
)
from flask_login import login_user, logout_user, current_user, login_required

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    # current_user is fetched from flask_login module, Authenticated User will not be able to register
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, you may now login', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # If a query parameter named next is found
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')


    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    # This method comes from flask_login module
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    # We don't want the user to be logged in here
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            flash('No such user exists in our database', 'warning')
            return redirect(url_for('users.login'))

        send_reset_email(user)

        flash('An email with instructions to reset your password has been sent.', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an expired token', 'warning')
        return redirect(url_for('users.reset_request'))

    form = ResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, you may now login', 'success')
        return redirect(url_for('users.login'))


    return render_template('reset_token.html', title='Reset Password', form = form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)
