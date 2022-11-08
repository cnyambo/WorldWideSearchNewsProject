from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,UserFavorites
from forms import RegisterForm, LoginForm 
from sqlalchemy.exc import IntegrityError
from secrets import API_SECRET_KEY
from flask import g
 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///news"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
API_BASE_URL ='https://newsapi.org/'

connect_db(app)

with app.app_context():
    db.create_all()

toolbar = DebugToolbarExtension(app)

