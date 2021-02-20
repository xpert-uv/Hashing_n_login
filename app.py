from flask import Flask, request, render_template, redirect, flash, session
from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserForm, LoginForm
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ghimire@localhost/model_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'SQLALCHEMY'
debug = DebugToolbarExtension(app)
connect_db(app)

db.create_all()


@app.route('/')
def index():
    form = LoginForm()
    return render_template("home.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new = User.register(username, password, email, first_name, last_name)
        db.session.add(new)
        db.session.commit()
        session['username'] = username
        return redirect('/secrets')
    return render_template("signup.html", form=form)


@app.route('/secrets')
def secrets():
    if "username" not in session:
        flash("Please login first")
        return redirect('/')
    return f"<h1> You made it</h1>"


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome {user.username}', 'success')
            session['username'] = user.username
            return redirect('/secrets')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop("user_id")
    flash("GoodBye", 'danger')
    return redirect('/')
