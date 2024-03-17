from flask import render_template, url_for, redirect, request
from pk import app, db, bcrypt
from pk.forms import RegistrationForm, LoginForm
from pk.models import User
from flask_login import login_user, current_user, logout_user, login_required

def protect_view(app):
    for view_function in app.server.view_functions:
        if view_function.startswith(app.config["routes_pathname_prefix"]):
            app.server.view_functions[view_function] = login_required(
                app.server.view_functions[view_function]
            )

@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account")

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        print(User.query.filter_by(username=form.username.data).first())
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            print("pass")
            if bcrypt.check_password_hash(user.password, form.password.data):
            # login_user(user, remember=form.remember.data)
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
    else:
        print("Fail")
        return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))