from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField, ValidationError,\
    BooleanField, PasswordField, HiddenField, validators, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, NumberRange
from vfinance.models import User
from flask_ckeditor import CKEditorField

from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets



class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1,20)])
    password = PasswordField("Password", validators = [DataRequired(), Length(1, 128), validators.EqualTo("confirm", message='Passwords must match')])
    confirm = PasswordField("Repeat Password")
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")

class QuoteForm(FlaskForm):
    symbol = StringField("Symbol", validators =[DataRequired()])
    submit = SubmitField("Submit")

class TradeForm(FlaskForm):
    action = SelectField("Action",choices=[('Buy','Buy'),('Sell','Sell')])
    symbol = StringField("Symbol", validators =[DataRequired()])
    price = FloatField("Price", validators = [NumberRange(min = 0,message=' Should not be less than 0')])
    quantity = IntegerField("Quantity", widget=h5widgets.NumberInput(min=1))
    submit = SubmitField("Review Order")