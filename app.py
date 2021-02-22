from flask import Flask, request, render_template, redirect, flash, session
from models import db, connect_db, User, Feedback
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserForm, LoginForm, FeedbackForm
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
        flash("User Created!", "success")
        return redirect('/users/{{username}}')
    return render_template("signup.html", form=form)


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
            return redirect(f'/feeds')


@app.route('/logout')
def logout():
    session.pop("username")
    flash("GoodBye", 'danger')
    return redirect('/')


@app.route('/users/<username>')
def user_details(username):
    if "username" not in session:
        flash("Please login first", "danger")
        return redirect('/')

    user = User.query.get_or_404(username)
    form = UserForm(obj=user)
    feeds = Feedback.query.filter_by(username=user.username).all()
    return render_template("user_details.html", form=form, feeds=feeds)


@app.route('/feedback/<int:id>/edit', methods=['GET', 'POST'])
def edit_feeds(id):
    if "username" not in session:
        flash("Please login first", "danger")
        return redirect('/')
    feed = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj=feed)
    if form.validate_on_submit():
        feed.title = form.title.data
        feed.content = form.content.data
        db.session.add(feed)
        db.session.commit()
        return redirect('/feeds')
    return render_template("edit_feed.html", form=form)


@app.route('/feeds')
def feeds():
    if "username" not in session:
        flash("Please login first")
        return redirect('/')

    feeds = Feedback.query.all()
    return render_template("feeds.html", feeds=feeds)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if "username" not in session:
        flash("Please login first")
        return redirect('/')
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        newFeed = Feedback(title=title, content=content,
                           username=session['username'])
        db.session.add(newFeed)
        db.session.commit()
        flash("Feedback posted", "success")
        return redirect('/feeds')

    return render_template("add_feeds.html", form=form)


@app.route('/feeds/<int:id>', methods=["POST"])
def delete_feeds(id):
    if "username" not in session:
        flash("Please login first")
        return redirect('/login')
    feed = Feedback.query.get_or_404(id)

    if feed.username == session['username']:
        db.session.delete(feed)
        db.session.commit()
        flash("Deleted", 'danger')
        return redirect('/feeds')
    flash("You don't have permisson to delete")
    return redirect('/feeds')
