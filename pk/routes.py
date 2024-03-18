from flask import render_template, url_for, redirect, request, session
from pk import app, db, bcrypt
from pk.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, ResetPasswordForm, ChangeUsernameForm
from pk.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

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
    return redirect("/home/")

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
        session["email"] = current_user.email
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
            # login_user(user, remember=form.remember.data)
                session["email"] = user.email
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                return render_template('login.html', title='Login', form=form)
        else:
            return render_template('login.html', title='Login', form=form)
    else:
        return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                sender='noreply@demo.com', 
                recipients=[user.email])
    msg.body= f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you didn't make this request then simply ignore this email and no changes will be made.
'''

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.password = hashed_password
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ResetPasswordForm()
    id = current_user.id
    curr_user = User.query.get_or_404(id)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        curr_user.password = hashed_password
        db.session.commit()
        return redirect(url_for('account'))
    return render_template('reset_password.html', title='Change Password', form=form)
 
@app.route("/change_username", methods=['GET', 'POST'])
@login_required
def change_name():
    form = ChangeUsernameForm()
    id = current_user.id
    curr_user = User.query.get_or_404(id)
    if form.validate_on_submit():
        curr_user.username = form.username.data
        db.session.commit()
        return redirect(url_for('account'))
    return render_template('reset_username.html', title='Change Username', form=form)