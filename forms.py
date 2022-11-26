from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField
from wtforms.validators import InputRequired, Optional, Email, Length


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])
    email = EmailField("E-mail", validators=[InputRequired(), Email()])
    full_name = StringField("Full Name", validators=[InputRequired()])
    address = StringField("Address", validators=[InputRequired()])
    
class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

  
class SearchForm(FlaskForm):
    """Form for search of news."""

    categories = StringField("Categories", validators=[Optional()])
    search = StringField("Search", validators=[Optional()])
    language = StringField("Language", validators=[Optional()])

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField("Username", validators=[InputRequired()])
    email = StringField("E-mail", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=6)])
    full_name = StringField("Full Name", validators=[InputRequired()])
    address = StringField("Address", validators=[InputRequired()])
    role = SelectField("Role",  choices=[('admin', 'Administrator'), ('guest', 'Guest')])



class UserUpdateForm(FlaskForm):
    """Form for adding users."""

    username = SelectField("Username", choices=[])    
    