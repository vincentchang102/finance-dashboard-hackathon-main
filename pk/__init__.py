from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from pk.plotly_dashboard import create_dash
from flask_mail import Mail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.app_context().push()
db = SQLAlchemy(app) # make sure db is created before hand with db.create_all()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER']= 'smtp-mail.outlook.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
mail = Mail(app)
from pk import routes
from pk.routes import protect_view
create_dash(app, protect_view)
