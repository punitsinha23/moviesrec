from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo , ValidationError
from movierec.models import User

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
            user = User.query.filter_by(username=username.data).first()  # Add .first() here
            if user:
                raise ValidationError('Username is taken.')

        # Custom validation for email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()  # Add .first() here
        if user:
            raise ValidationError('Email is taken.')    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
