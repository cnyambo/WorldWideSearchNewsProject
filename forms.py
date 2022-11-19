from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,EmailField
from wtforms.validators import InputRequired


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
