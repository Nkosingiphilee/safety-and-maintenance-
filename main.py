import datetime

import flask_login
from flask import Flask, render_template, request, redirect, flash, url_for, session
import sqlite3
import string
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import UserMixin, login_required, current_user

from forms import Register, Login

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
    role TEXT DEFAULT "user" NOT NULL
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
        Date datetime DEFAULT utcnow,
        Image TEXT 
        )
        """)

app = Flask(__name__)
app.config["SECRET_KEY"] = 'random string'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.user_id = id
        self.name = name
        self.email = email
        self.password = password
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


@login_manager.user_loader
def user_loader(user_id):
    with sqlite3.connect('maintenance.db') as db:
        cur = db.cursor()
        cur.execute("""SELECT * FROM register WHERE user_id =%d""" % user_id)
        user = cur.fetchone()
    if user is None:
        return None
    else:
        return User(user[0], user[2], user[4], user[5])


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('reported'))
    form = Register()
    if form.validate_on_submit():
        with sqlite3.connect('maintenance.db') as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO register(student_no,stud_name,stud_surname,email,password,phone_number,role) VALUES(?,?,?,?,?,?,?) 
            """, (
                form.student_no.data, form.stud_name.data, form.stud_surname.data, form.email.data, form.password.data,
                form.phone_number.data, "user"))
            db.commit()
        flash("%s has been registered" % form.stud_name.data, 'successful ')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        db = sqlite3.connect('maintenance.db')
        cur = db.cursor()
        num = str(form.student_no.data)
        cur.execute("""SELECT * FROM register WHERE student_no=%s""" % num)
        user = cur.fetchone()
        if user is None:
            return redirect(url_for('index'))
        if user[1] == form.student_no.data and user[5] == form.password.data:
            Us = user_loader(user[0])
            flask_login.login_user(Us)
            flash("%s" % str(user[2]), 'successful ')
            return redirect(url_for('report'))
    return render_template('login.html', form=form)


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
        image.save('Images/' + secure_filename(image.filename))

        with sqlite3.connect('maintenance.db') as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO report(campus,Block,room_no,Report,Description,Date,Image) VALUES(?,?,?,?,?,?,?) 
            """, (request.form['campus'], request.form['block'], request.form['room'], request.form['report'],
                  request.form['description'], datetime.utcnow(), image.filename))
            db.commit()
        flash("report submitted")
        return redirect(url_for('report'))
    return render_template('reform.html')


@app.route('/reported')
@login_required
def reported():
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


if __name__ == '__main__':
    app.run(debug=True)
