from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,UserFavorites
from forms import RegisterForm, LoginForm, SearchForm 
from sqlalchemy.exc import IntegrityError
from api_secrets import API_SECRET_KEY
from flask import g
import requests
 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///news'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] ='abc123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
API_BASE_URL ='https://api.thenewsapi.com/v1/news'

CURR_USER_KEY = "curr_user"
connect_db(app)

with app.app_context():
    db.create_all()

toolbar = DebugToolbarExtension(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.route('/')
def home_page():
    return redirect('/login')


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
def log_user(username):
    """user go to homepage"""
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    user = User.query.get_or_404(username)
    if user.username == session['username']:
        user = User.query.get(username)
        news = requests.get(f'{API_BASE_URL}/top',
            params={'api_token':API_SECRET_KEY, 'language':'en'})
 
        all_news = news.json()

        return render_template('news.html',user= user,news=all_news )
    return redirect('/')

@app.route('/searchAll/<username>')
def show_all_news(username):
    """show all news"""
    news = requests.get(f'{API_BASE_URL}/all',
        params={'api_token':API_SECRET_KEY,'limit':50})
    all_news = news.json()
    return render_template('news.html',user= username,news=all_news )

@app.route('/searchNews/<username>/<language>', methods=['GET', 'POST'])
def search_form(username, language):
    """search for news"""
    form = SearchForm()
    if form.validate_on_submit():
        categories, search, lang = (form.categories.data, form.search.data, form.language.data)
        if lang:
            news = requests.get(f'{API_BASE_URL}/all',
                params={'api_token':API_SECRET_KEY, 'categories':categories, 'search':search, 'language':lang, 'limit':50})
        else: 
            news = requests.get(f'{API_BASE_URL}/all',
                params={'api_token':API_SECRET_KEY, 'categories':categories, 'search':search,'language':language,'limit':50})   
        all_news = news.json()
        data = [article for article in  all_news['data']]  
        for i in data:
            favorites_news = UserFavorites(article_id =i['uuid'], username=username)
            db.session.add(favorites_news)      
        db.session.commit()

        return render_template('search.html',user=username, news=all_news)  
    return render_template('search_form.html',form=form)    

@app.route('/newsAll/<lang>')
def change_lang(lang):
    """this will help users to pick the languages they want"""
    #rule = request.url_rule
    rule = request.referrer
    user = session['username']
    news =''
       
    if 'searchAll' in rule:
        news = requests.get(f'{API_BASE_URL}/all',
        params={'api_token':API_SECRET_KEY, 'language':lang,'limit':50})
    elif 'searchNews' in rule:
        redirect(f'/searchNews/{user}>/{lang}')  
    else:
        news = requests.get(f'{API_BASE_URL}/top',
            params={'api_token':API_SECRET_KEY, 'language':lang})
    print(f'************************************{user}' )
    all_news = news.json()
    if   len(all_news['data']) >0:
        return render_template('news.html',user= user,news=all_news )
    else:
        flash(f'No news available for {lang}', 'danger')
        return redirect(f'/users/{user}')


@app.route('/user/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not session['username']:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    del session['username']
    db.session.delete(session['username'])
    db.session.commit()

    return redirect("/signup")


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')        