# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config, make_celery
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

celery = make_celery(app)
celery.conf.update(app.config)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .api import api_routes as api_blueprint
app.register_blueprint(api_blueprint)

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

