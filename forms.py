import sqlite3

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, email, ValidationError


class Register(FlaskForm):
    id_number = StringField('Identity number', validators=[DataRequired(), Length(min=8, max=8)])
    stud_name = StringField('student name', validators=[DataRequired()])
    stud_surname = StringField('student surname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), email()])
    phone_number = StringField('cellphone number', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=8)])
    admin = BooleanField('admin registration')
    submit = SubmitField('Register')

    def validate_id(self, id_number):
        with sqlite3.connect('maintenance.db') as db:
            cur = db.cursor()
            cur.execute("""SELECT * FROM register WHERE student_no=%s""" % id_number)
            user = cur.fetchone()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class Maintenance(FlaskForm):
    id_number = StringField('Identity number', validators=[DataRequired(), Length(min=8, max=8)])
    main_name = StringField('maintenance name', validators=[DataRequired()])
    main_type = SelectField('maintenance Type',
                            choices=[('Electrical', 'Electrician'), ('Mechanic', 'Mechanic'), ('Plumber', 'plumber'),
                                     ('Pipe fitter', 'pipe fitter'), ])
    main_email = StringField('email', validators=[DataRequired(), email()])
    phone_number = StringField('cellphone number', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Register')


class Login(FlaskForm):
    id_number = StringField('Identity number', validators=[DataRequired(), Length(min=8, max=8)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=8)])
    login = SubmitField('Log in')
