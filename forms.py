from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,EmailField
from wtforms.validators import InputRequired, Optional


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("email", validators=[InputRequired()])
    full_name = StringField("full_name", validators=[InputRequired()])
    address = StringField("address", validators=[InputRequired()])
    
class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

  
class SearchForm(FlaskForm):
    """Form for search of news."""

    categories = StringField("Categories", validators=[Optional()])
    search = StringField("Search", validators=[Optional()])
    language = StringField("Language", validators=[Optional()])