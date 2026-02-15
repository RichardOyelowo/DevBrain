from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo


class Login(FlaskForm):
    email = StringField("Email", render_kw={"placeholder": "John Doe"}, validators=[DataRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=50)])
    submit = SubmitField("Login")


class Register(FlaskForm):
    email = StringField("Name", render_kw={"placeholder": "John Doe"}, validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[Length(max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20), 
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).*$', 
            message='Password must contain at least 1 letter, 1 number and 1 symbol')])
    confirmation = PasswordField("Retype Password", validators=[DataRequired(), EqualTo("password", message="Password must match")])
    submit = SubmitField("Register")


class ForgotPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Send Email')


class ResetPassword(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=20), 
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).*$', 
            message='Password must contain at least 1 letter, 1 number and 1 symbol')])
    confirmation = PasswordField('Retype Password', validators=[DataRequired(), EqualTo("password", message="Password doesn't match.")])
    submit = SubmitField("Update Password")