from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import DataRequired, Length, email


class Register(FlaskForm):
    student_no = StringField('student number', validators=[DataRequired(), Length(min=8, max=8)])
    stud_name = StringField('student name', validators=[DataRequired()])
    stud_surname = StringField('student surname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), email()])
    phone_number = StringField('cellphone number', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Register')


class Login(FlaskForm):
    student_no = StringField('student number', validators=[DataRequired(), Length(min=8, max=8)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=8)])
    login = SubmitField('Log in')
