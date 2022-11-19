from urllib.robotparser import RobotFileParser
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import  relationship

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String(50),nullable=False, unique=True)
    
    full_name = db.Column(db.String(50),nullable=False)

    address = db.Column(db.String(50),nullable=False)

    role = db.Column(db.String(30),nullable=False)


    @classmethod
    def register(cls, username, pwd, email, fname, address, role):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, full_name = fname, address = address, role = role)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False


class UserFavorites(db.Model):
    __tablename__ = 'users_favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    article_id = db.Column(db.String(20), nullable=False)

    username = db.Column(db.String(20), db.ForeignKey('users.username'))

    user = db.relationship('User', backref="users_favorites")

    