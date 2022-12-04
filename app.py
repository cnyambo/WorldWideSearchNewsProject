from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,UserFavorites, Articles
from forms import RegisterForm, LoginForm, SearchForm, UserAddForm, UserUpdateForm
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

def add_article():
    existedArticles = Articles.query.all()
    news = requests.get(f'{API_BASE_URL}/all', params={'api_token':API_SECRET_KEY})   
    topnews = requests.get(f'{API_BASE_URL}/top', params={'api_token':API_SECRET_KEY}) 
    all_news = news.json()
    topall = topnews.json()
    newsdata = [article for article in  all_news['data']] 
    newstop = [article for article in  topall['data']] 
    data = newsdata + newstop
    if len(existedArticles) > 0:
        existedData = [article.uuid for article in  existedArticles]
        for i in data:
            if i['uuid'] in existedData:
                continue
            else:
                articles = Articles(uuid =i['uuid'])
                db.session.add(articles)    
    else:
        for i in data:
            articles = Articles(uuid =i['uuid'])
            db.session.add(articles)              
    db.session.commit()



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
        flash('Welcome to the news site! You Successfully Created Your Account!', "success")
        return redirect(f'/users/{name}/all')

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
            session['role'] = user.role
            return redirect(f'/users/{username}/all')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)



@app.route('/users/<username>/<language>')
def log_user(username,language):
    """user go to homepage"""
    add_article()
    
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    user = User.query.filter_by(username = username).first()

    if user.username == session['username']:
        
        if language and language!='all':
            news = requests.get(f'{API_BASE_URL}/top',
                params={'api_token':API_SECRET_KEY, 'language':language,'limit':50})
            if len(news.json()) >0 :  
                news = news
            else:
                news = requests.get(f'{API_BASE_URL}/top',
                params={'api_token':API_SECRET_KEY,'limit':50})

        else:
            news = requests.get(f'{API_BASE_URL}/top',
                params={'api_token':API_SECRET_KEY,'limit':50})
 
        all_news = news.json()
        
        return render_template('news.html',user= user,news=all_news )
    return redirect('/')

@app.route('/searchAll/<username>/<language>')
def show_all_news(username,language):
    """show all news"""
    if language and language != 'all':
        news = requests.get(f'{API_BASE_URL}/all',
            params={'api_token':API_SECRET_KEY,'language':language,'limit':50})
        if len(news.json()) >0 :  
                news = news
        else:
                news = requests.get(f'{API_BASE_URL}/all',
                params={'api_token':API_SECRET_KEY,'limit':50})
    
    else:
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
        if language and language!='all':
            news = requests.get(f'{API_BASE_URL}/all',
                params={'api_token':API_SECRET_KEY, 'categories':categories, 'search':search, 'language':lang, 'limit':50})
        
            if len(news.json()) >0 :  
                news = news
            else:
                news = requests.get(f'{API_BASE_URL}/all',
                params={'api_token':API_SECRET_KEY, 'categories':categories, 'search':search , 'limit':50})
        else: 
            news = requests.get(f'{API_BASE_URL}/all',
                params={'api_token':API_SECRET_KEY, 'categories':categories, 'search':search,'limit':50})   
        all_news = news.json()
        data = [article for article in  all_news['data']]  
        for i in data:
            article  = Articles.query.filter_by(uuid = i['uuid']).first()
            if article is None:
                newarticle  = Articles(uuid =i['uuid'])
                db.session.add(newarticle)
                db.session.commit()
                article = Articles.query.filter_by(uuid = i['uuid']).first()
            user = User.query.filter_by(username =username).first()
            favorites_news = UserFavorites(article_id =article.id, user_id=user.id)
            db.session.add(favorites_news)      
        db.session.commit()

        return render_template('search.html',user=username, news=all_news)  
    return render_template('search_form.html',form=form)    

@app.route('/newsAll/<lang>')
def change_lang(lang):
    """this will help users to pick the languages they want"""
    rule = request.referrer
    user = session['username']
    #news =''
       
    if 'searchAll' in rule:
        return redirect(f'/searchAll/{user}/{lang}') 
         
    elif 'searchNews' in rule:
        return redirect(f'/searchNews/{user}/{lang}')  
    else:
        return redirect(f'/users/{user}/{lang}')



@app.route('/users/<username>/delete')
def delete_user(username):
     """Delete user"""
     if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/register')
     deluser = User.query.get_or_404(username)
     favorites=UserFavorites.query.filter_by(user_id = deluser.id)
     if deluser.username == session['username']:
        for i in favorites:
            db.session.delete(i)
        db.session.delete(deluser)
        db.session.commit()
        flash("User deleted!", "info")
        return redirect('/')
     flash("You don't have permission to do that!", "danger")
     return redirect(f'/users/{username}/all')

 
@app.route('/users/<username>/add', methods=['GET', 'POST'])
def add_user(username):
    """ Add users """
    form = UserAddForm()
    if form.validate_on_submit():
        name, pwd, email, fname, address, role = (form.username.data, form.password.data, form.email.data, form.full_name.data, form.address.data, form.role.data)
        new_user = User.register(name, pwd, email,fname,address,role)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return redirect(f'/users/{username}/add', form=form)
        #session['username'] = new_user.username
        flash('New User created!', "success")
        return redirect(f'/users/{username}/all')

    return render_template('add_user.html',form=form)

@app.route('/users/<admin_username>/update', methods=['GET', 'POST'])
def get_edited_user(admin_username):
    """ Update users """
    form = UserUpdateForm()
    users = User.query.all()
    form.username.choices = [(user.username) for user in users]
    if form.validate_on_submit():
        name = form.username.data
        return redirect(f'/users/{admin_username}/update/{name}')

    return render_template('edit_user_form.html',form=form)

@app.route('/users/<admin_username>/update/<username>', methods=['GET','POST'])
def edit_user(admin_username, username):
    """edit user"""
    form = UserAddForm()    
    user = User.query.get_or_404(username)
    form.username.data = user.username
    form.full_name.data = user.full_name
    form.email.data = user.email
    form.address.data = user.address
    form.role.data = user.role
    if form.validate_on_submit():
        user.username = form.username.data  
        user.full_name = form.full_name.data  
        user.email = form.email.data 
        user.address = form.address.data 
        user.role = form.role.data 
        db.session.add(user)
        db.session.commit()
        flash("You updated user's account!", "success")
        return redirect(f'/users/{admin_username}/all')	
    
    return render_template('/edit_user.html', form = form , user=user)
 

@app.route('/users/<admin_username>/delete_account', methods=['GET', 'POST'])
def get_deleted_user(admin_username):
    """ Delete users """
    form = UserUpdateForm()
    users = User.query.all()
    form.username.choices = [(user.username) for user in users]
    if form.validate_on_submit():
        name = form.username.data
        return redirect(f'/users/{admin_username}/delete/{name}')

    return render_template('edit_user_form.html',form=form)

@app.route('/users/<admin_username>/delete/<username>')
def delete_existing_user(admin_username,username):
     """Delete user"""
     if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
     deluser = User.query.get_or_404(username)
     favorites=UserFavorites.query.filter_by(username = deluser.username)
     for i in favorites:
            db.session.delete(i)
     db.session.delete(deluser)
     db.session.commit()
     flash("User deleted!", "info")
     return redirect(f'/users/{admin_username}/all')
    
@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')        