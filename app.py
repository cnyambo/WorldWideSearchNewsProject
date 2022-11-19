from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,UserFavorites
from forms import RegisterForm, LoginForm 
from sqlalchemy.exc import IntegrityError
from api_secrets import API_SECRET_KEY, APPLENEWS_KEY, TESLANEWS_KEY, TOPBUSINESSNEWS_KEY, TECHCRUSHNEWS_KEY, ALLARTICLESNEWS_KEY
from flask import g
import requests
 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///news'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] ='abc123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
API_BASE_URL ='https://newsapi.org/'

connect_db(app)

with app.app_context():
    db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        name, pwd, email, fname, address = (form.username.data, form.password.data, form.email.data, form.full_name.data, form.address.data)
        new_user = User.register(name, pwd, email,fname,address,'guest')
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f'/users/{name}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)



@app.route('/users/<username>')
def show_user(username):
    """show user"""
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    user = User.query.get_or_404(username)
    if user.username == session['username']:
        user = User.query.get(username)
        news = requests.get('https://newsapi.org/v2/everything',
            params={'domains':'wsj.com','apiKey':ALLARTICLESNEWS_KEY})
  
        return redirect('/')
    return redirect('/')
