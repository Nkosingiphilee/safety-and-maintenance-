import datetime

import flask_login
from flask import Flask, render_template, request, redirect, flash, url_for, session
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import UserMixin, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import Register, Login, Maintenance

with sqlite3.connect('maintenance.db') as db:
    curse = db.cursor()
    curse.execute("""CREATE TABLE IF NOT EXISTS  register(
    user_id Integer PRIMARY KEY AUTOINCREMENT,
    student_no VARCHAR(10),
    stud_name TEXT NOT NULL,
    stud_surname TEXT NOT NULL,
    email VARCHAR(50) NOT NULL,
    password VARCHAR(50),
    phone_number TEXT,
    is_admin BOOLEAN DEFAULT False
    )
    """)

with sqlite3.connect('maintenance.db') as db:
    curse = db.cursor()
    curse.execute("""CREATE TABLE IF NOT EXISTS  report(
        report_id Integer PRIMARY KEY AUTOINCREMENT,
        campus VARCHAR(10),
        Block TEXT NOT NULL,
        Room_no TEXT NOT NULL,
        Report VARCHAR(50) NOT NULL,
        Description VARCHAR(50),
        level TEXT,
        Date datetime DEFAULT utcnow,
        Image TEXT ,
        user_id Integer
        )
        """)

with sqlite3.connect('maintenance.db') as db:
    curse = db.cursor()
    curse.execute("""CREATE TABLE IF NOT EXISTS maintenee(
        main_id Integer PRIMARY KEY AUTOINCREMENT,
        main_no VARCHAR(10),
        main_name TEXT NOT NULL,
        main_type TEXT NOT NULL,
        main_email VARCHAR(50) NOT NULL,
        password VARCHAR(50),
        phone_number TEXT 
        )
        """)

app = Flask(__name__)
app.config["SECRET_KEY"] = 'random string'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


# create an instance of user that gonna be available where user is logged on the system
class User(UserMixin):
    def __init__(self, id, name, email, password, is_admin):
        self.user_id = id
        self.name = name
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_admin(self):
        return self.is_admin


# load user from database
# and substatiate User class to create user to log in
@login_manager.user_loader
def user_loader(user_id):
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        cur.execute("""SELECT * FROM register WHERE user_id =%d""" % user_id)
        user = cur.fetchone()
    if user is None:
        return None
    else:
        return User(user[0], user[2], user[4], user[5], user[7])


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


# register users to the database
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('reported'))
    form = Register()
    if form.validate_on_submit():
        with sqlite3.connect('maintenance.db') as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO register(student_no,stud_name,stud_surname,email,password,phone_number,is_admin) VALUES(?,?,?,?,?,?,?) 
            """, (
                form.id_number.data, form.stud_name.data, form.stud_surname.data, form.email.data,
                generate_password_hash(form.password.data), form.phone_number.data,form.admin.data))
            db.commit()
        flash("%s registration Successful" % form.stud_name.data, 'successful ')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


# log in and the system determine
# if is_admin is true you are and admin
# else is_admin is false you just a user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('reported'))
    form = Login()
    if form.validate_on_submit():
        db = sqlite3.connect('maintenance.db')
        cur = db.cursor()
        num = str(form.id_number.data)
        cur.execute("""SELECT * FROM register WHERE student_no=%s""" % num)
        user = cur.fetchone()
        if user is None:
            return redirect(url_for('index'))
        if user[1] == form.id_number.data and check_password_hash(user[5], form.password.data):
            Us = user_loader(user[0])
            flask_login.login_user(Us)
            flash("%s" % str(user[2]), 'successful ')
            return redirect(url_for('report'))
    return render_template('login.html', form=form)


# set all login sessions to defaut
@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@app.route('/report')
@login_required
def report():
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        cur.execute("""SELECT * FROM report""")
    reports = cur.fetchall()
    return render_template('report.html', reports=reports)


@app.route('/report-form', methods=['GET', 'POST'])
@login_required
def report_form():
    if request.method == 'POST':
        image = request.files['damage-image']
        image.save('static/Images/' + secure_filename(image.filename))

        with sqlite3.connect('maintenance.db') as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO report(campus,Block,room_no,Report,Description,Date,Image,user_id) VALUES(?,?,?,?,?,?,?,?) 
            """, (request.form['campus'], request.form['block'], request.form['room'], request.form['report'],
                  request.form['description'], datetime.utcnow(), image.filename, current_user.user_id))
            db.commit()
        flash("report submitted")
        return redirect(url_for('report'))
    return render_template('reform.html')


# admin page for all reported issues in the system
@app.route('/reported')
@login_required
def reported():
    if not current_user.is_admin:
        flash("admin required")
        return redirect(url_for('index'))
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        cur.execute("""SELECT * FROM report ORDER BY report_id  DESC""")
    reports = cur.fetchall()
    return render_template('reported.html', reports=reports)


@app.route('/detailed/<int:report_id>')
@login_required
def detailed(report_id):
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        id = int(report_id)
        cur.execute("""SELECT * FROM report WHERE report_id=%d""" % int(id))
    return render_template('detailed.html', reports=cur.fetchone())


@app.route('/my-report')
def my_report():
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        cur.execute("""SELECT * FROM report WHERE user_id=(?)""", [current_user.user_id])
    return render_template('reported.html', reports=cur.fetchall())


@app.route('/reg-maintenance', methods=['GET', 'POST'])
def register_maintenance():
    form = Maintenance()
    if form.validate_on_submit():
        with sqlite3.connect('maintenance.db') as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO maintenee(main_no,main_name,main_type,main_email,password,phone_number) VALUES(?,?,?,?,?,?) 
            """, (
                form.id_number.data, form.main_name.data, form.main_type.data, form.main_email.data,
                generate_password_hash(form.password.data), form.phone_number.data))
            db.commit()
        flash("%s  registration succession" % form.main_name.data, 'successful ')
    return render_template('reg-mainance.html', form=form)


@app.route('/assign/<int:id>')
def assign(id):
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        cur.execute("""SELECT * FROM maintenee""")
        maintain = cur.fetchall()
        cur.execute("""SELECT * FROM report WHERE report_id=?""", (id,))
        report = cur.fetchone()
    return render_template('assign.html', maintain=maintain, report=report)


if __name__ == '__main__':
    app.run()
