from flask_login import UserMixin
from one_word import db,login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class ChatRoom(db.Model, UserMixin):
    host = db.Column(db.Integer,nullable=False)
    turn = db.Column(db.Integer,nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), nullable = False)
    members = db.relationship('User', backref='member', lazy=True)
    messages = db.relationship('Message', backref='room',lazy=True,cascade="all, delete-orphan")

class User(db.Model, UserMixin):
    chatroom_id = db.Column(db.Integer, db.ForeignKey(ChatRoom.id,ondelete='CASCADE'))
    email = db.Column(db.String(120),unique=True,nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    messages = db.relationship('Message', backref='author', lazy=True, cascade="all, delete-orphan")
    password = db.Column(db.String(60), nullable = False)
    username = db.Column(db.String(20),unique=True,nullable=False)

class Message(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(45), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id,ondelete='CASCADE'))
    chatroom_id = db.Column(db.Integer, db.ForeignKey(ChatRoom.id,ondelete='CASCADE'))

class StoryPost(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    story = db.Column(db.String(10000), nullable = False)
    authors = db.Column(db.String(1800), nullable = False)