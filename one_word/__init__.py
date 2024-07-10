from flask import Flask
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =  "sqlite:///data.db"
app.config['SECRET_KEY'] = 'dbc761867601a6df37da071b55b8128d'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socket = SocketIO(app,logger=True,enginio=True)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = "info" 

from one_word.main_py.routes import main
from one_word.userAuth_py.routes import users
from one_word.game_py.routes import game

app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(game)