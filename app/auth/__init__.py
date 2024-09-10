from flask import redirect, flash, url_for
from flask_openid import OpenID
from . import db
from flask_login import login_user

oid = OpenID()

def authenticate(username, password):
    from .models import User
    user = User.query.filter_by(username=username).first()

    if not user:
        return None
    
    if not user.verify_password(password):
        return None
    
    return user

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
    