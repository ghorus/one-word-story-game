from flask import render_template, redirect,flash,url_for,Blueprint,request
from flask_login import current_user,login_user,logout_user
from one_word.forms import SignupForm, LoginForm
from one_word.models import User
from one_word import db,bcrypt
users = Blueprint('users',__name__)

@users.route('/signup',methods=['GET', 'POST'])
def signup():
    """
    Users register their account.
    """
    form = SignupForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created.','success')
        return redirect(url_for('users.login'))
    return render_template('signup.html',form=form,title='Sign Up')

@users.route('/login',methods=['GET', 'POST'])
def login():
    """
    User logs in.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome, {user.username}!','success')
            return redirect(next_page) if next_page else redirect(url_for('game.room_lobby'))
        else:
            flash('Login unsuccessful. Please check email and password.','danger')
    return render_template('login.html',form=form,title='Login')

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))