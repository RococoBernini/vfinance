from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_moment import Moment
from flask_wtf import CSRFProtect



bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
toolbar = DebugToolbarExtension()
moment = Moment()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    from vfinance.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Helloooo'
login_manager.login_message_category = 'warning'