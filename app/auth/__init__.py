from flask_openid import OpenID

oid = OpenID()

def authenticate(username, password):
    from .models import User
    user = User.query.filter_by(username=username).first()

    if not user:
        return None
    
    if not user.verify_password(password):
        return None
    
    return user