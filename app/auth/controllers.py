from flask import (render_template, Blueprint, flash, redirect, url_for)
from . import oid
from .forms import RegisterForm, OpenIDForm, LoginForm
from .models import User, db
from flask_login import login_user, logout_user
from .email import send_email

auth_blueprint = Blueprint('auth',
                            __name__,
                            template_folder='../templates/auth',
                            url_prefix='/auth')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
@oid.loginhandler
def register():
    form = RegisterForm()
    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )
    
    if form.validate_on_submit():
        new_user = User(form.username.data)
        new_user.password(form.password.data)

        db.session.add(new_user)
        db.session.commmit()

        flash("Your user has been created, please login.", category="success")

        token = new_user.generate_confirmation_token()
        send_email(new_user.email, 'Confirm Your Account', 'auth/email/confirm', user=new_user, token=token)

        flash('A confirmation email has been sent to you by email.')


        return redirect(url_for('.login'))
    
    openid_errors = oid.fetch_error()
    if openid_errors:
        flash(openid_errors, category="danger")

    return render_template('register.html', form=form, openid_form=openid_form)
    
@auth_blueprint.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    form = LoginForm()
    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user, remember=form.remember.data)
        flash("You have been logged in.", category="success")
        return redirect(url_for('main.index'))
    
    openid_errors = oid.fetch_error()
    if openid_errors:
        flash(openid_errors, category="danger")

    return render_template('login.html', form=form, openid_form=openid_form)

@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("You have been logged out.", category="success")
    return redirect(url_for('main.index'))