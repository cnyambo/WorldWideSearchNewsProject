from urllib.robotparser import RobotFileParser
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True )

    username = db.Column(db.String(50), nullable=False)

    password = db.Column(db.String(250), nullable=False)

    email = db.Column(db.String(100),nullable=False, unique=True)
    
    full_name = db.Column(db.String(100),nullable=True)

    address = db.Column(db.String(250),nullable=True)

    role = db.Column(db.String(50),nullable=False)


    @classmethod
    def register(cls, username, password, email, full_name, address, role):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, full_name = full_name, address = address, role = role)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()
        if not u and not bcrypt.check_password_hash(u.password, pwd):
            return False 
        else:    
            return u

class Articles(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    uuid = db.Column(db.String(100), nullable=False, unique=True)



class UserFavorites(db.Model):
    __tablename__ = 'users_favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref="users_favorites")

    