from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from Queue import Queue

app = Flask(__name__)

#Include config from config.py
app.config.from_object('config')
app.secret_key = 'Dkqj4v$eLR9ov]'
app.queue = Queue()

#Create an instance of SQLAclhemy
db = SQLAlchemy(app)

socketio = SocketIO(app)

from app import views, models