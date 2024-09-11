from flask import Blueprint, current_app, render_template, flash, redirect, url_for
from .models import Post, Tag, tags
from flask_login import login_required, current_user
from .. import db
from sqlalchemy import desc, func
from ..auth import has_role
from .forms import PostForm

blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='../templates/blog',
    url_prefix="/blog"
)

def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags = db.session.query(Tag, func.count(tags.c.post_id).label('total')
                                ).join(tags).group_by(Tag).order_by(desc('total')).limit(5).all()

    return recent, top_tags

@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, current_app.config.get('POSTS_PER_PAGE', 10), False)

    recent, top_tags = sidebar_data()

    return render_template('home.html', posts=posts, recent=recent, top_tags=top_tags)

@blog_blueprint.route('/new', methods=['GET', 'POST'])
@login_required
@has_role('poster')
def new_post():
    form = PostForm
    if form.validate_on_submit():
        new_post = Post()
        new_post.title = form.title.data
        new_post.user_id = current_user.id
        new_post.text = form.text.data
        db.session.add(new_post)
        db.session.commit()
        flash('Post added', 'info')
        return redirect(url_for('.post', post_id=new_post.id))
    return render_template('new.html', form=form)

