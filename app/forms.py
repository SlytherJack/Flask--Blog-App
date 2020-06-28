from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)]
                           )

    email = StringField('Email',
                        validators=[DataRequired(), Email()]
                        )

    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=20)]
                             )

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')]
                                     )

    submit = SubmitField('Sign Up')

    # You can write a custom validator within a form by writing a validate_{field_name} method
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()

        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        # Query DB for a user by email
        user = User.query.filter_by(email = email.data).first()

        if user:
            raise ValidationError('That email is taken. Please choose a different one')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)]
                           )

    email = StringField('Email',
                        validators=[DataRequired(), Email()]
                        )
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')


    def validate_username(self, username):
        # Only username which is different from the current one will be entertained
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()

            if user:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()

            if user:
                raise ValidationError('That email is taken. Please choose a different one')



class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()]
                        )

    password = PasswordField('Password',
                             validators=[DataRequired()]
                             )

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()]
                        )

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()

        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=20)]
                             )

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')]
                                     )

    submit = SubmitField('Reset Password')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
