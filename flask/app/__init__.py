from flask import Flask

app = Flask(__name__)

#Include config from config.py
app.config.from_object('config')
app.secret_key = 'some_secret'

#Create an instance of SQLAclhemy
#db = SQLAlchemy(app)
from app import views, models