from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, number_range
from extend import db
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    opinion_score = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    author = db.relationship('Users', backref=db.backref('posts', lazy=True))
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=150)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=6, max=100), EqualTo('password')])
    submit = SubmitField('Register')

class ReviewForm(FlaskForm):
    score = IntegerField('Score (1-5)', validators=[DataRequired(), number_range(min=1, max=5)])
    content = StringField('Your Opinion', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Review')