from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app=Flask(__name__)
app.config.from_object('config')
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
limiter=Limiter(app, key_func=get_remote_address)

db = SQLAlchemy(app)

from app import views, models
