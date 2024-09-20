import os
from app import db, migrate, create_app
from app.auth.models import User
from app.blog.models import Post, Tag


env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app('config.%sConfig' % env.capitalize())


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post, Tag=Tag, migrate=migrate)