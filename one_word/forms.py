from flask_wtf import FlaskForm
from one_word.models import User
from wtforms import PasswordField,StringField,SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()],render_kw={"placeholder": "example@example.com*"})
    password = PasswordField('Password',validators=[DataRequired()],render_kw={"placeholder": "Your password here*"})
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()],render_kw={"placeholder": "Input email here*"})
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')],render_kw={"placeholder": "Confirm password here*"})
    password = PasswordField('Password',validators=[DataRequired(),Length(min=8, max=35)],render_kw={"placeholder": "Your password here*"})
    submit = SubmitField('Sign Up')
    username = StringField('Username', validators=[DataRequired(), Length(min=5,max=20)],render_kw={"placeholder": "Create your usename here*"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken.')
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is already taken.')