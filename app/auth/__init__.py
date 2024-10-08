import functools
from flask import redirect, flash, url_for, abort, session
from flask_openid import OpenID
from . import db
from flask_login import login_user, LoginManager
from flask_login import AnonymousUserMixin
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.reddit import make_reddit_blueprint, reddit
from flask_dance.consumer import oauth_authorized
from flask_login import current_user
from .models import User



bcrypt = Bcrypt()
oid = OpenID()
jwt = JWTManager()

class BlogAnonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"
login_manager.anonymous_user = BlogAnonymous

def create_module(app, **kwargs):
    bcrypt.init_app(app)
    oid.init_app(app)
    jwt.init_app(app)

    facebook_blueprint = make_facebook_blueprint(
        client_id =app.config.get("FACEBOOK_OAUTH_CLIENT_ID"),
        client_secret=app.config.get("FACEBOOK_OAUTH_CLIENT_SECRET"),
    )
    app.register_blueprint(facebook_blueprint, url_prefix="/auth/login")

    google_blueprint= make_google_blueprint(
        client_id=app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    )
    app.register_blueprint(google_blueprint, url_prefix="/auth/login")

    reddit_blueprint=make_reddit_blueprint(
        client_id=app.config.get("REDDIT_OAUTH_CLIENT_ID"),
        client_secret=app.config.get("REDDIT_OAUTH_CLIENT_SECRET")
    )
    app.register_blueprint(reddit_blueprint, url_prefix="/auth/login")

    from .controllers import auth_blueprint
    app.register_blueprint(auth_blueprint)

def authenticate(username, password):
    from .models import User
    user = User.query.filter_by(username=username).first()

    if not user:
        return None
    
    if not user.verify_password(password):
        return None
    
    return user

def identify(payload):
    return load_user(payload['payload'])

def has_role(name):
    def real_decorator(f):
        def wraps(*args, **kwargs):
            if current_user.has_role(name):
                return f(*args, **kwargs)
            else:
                abort(403)
        return functools.update_wrapper(wraps, f)
    return real_decorator

@login_manager.user_loader
def load_user(userid):
    from .models import User
    return User.query.get(userid)

@oid.after_login
def create_or_login(resp):
    from .models import User
    username = resp.fullname or resp.nickname or resp.email
    if not username :
        flash('Invalid login. Please try again', 'danger')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('main.index'))
    
@oauth_authorized.connect
def logged_in(blueprint, token):
    if blueprint.name == 'facebook':
        resp = facebook.get("/me")
        username = resp.json()['name']
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User()
        user.username = username
        db.session.add(user)
        db.session.commmit()
    login_user(user)
    flash("You have been logged in.", category="success")