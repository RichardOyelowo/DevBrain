from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class Login(FlaskForm):
    email = StringField("Name", render_kw={"placeholder": "John Doe"}, validators=[DataRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=50)])
    submit = SubmitField("Login")


class Register(FlaskForm):
    email = StringField("Name", render_kw={"placeholder": "John Doe"}, validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[Length(max=40)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=50)])
    confirmation = PasswordField("Retype Password", validators=[DataRequired(), EqualTo("password", message="Password must match")])
    submit = SubmitField("Register")


class ForgotPassword(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=50)])
    submit = SubmitField("Submit")


class ResetPassword(FlaskForm):
    password = StringField(" New Password", validators=[DataRequired(), Length(max=50)])
    confirmation = PasswordField("Retype-Password", validators=[DataRequired(), EqualTo("password", message="Password doesn't match")])
    submit = SubmitField("Update Password")