import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

from sc_http.common.functions import tangle_session
from sc_http.index.forms import RegisterForm, LoginForm
from sc_http.common.decorators import requires_auth, requires_unauth

mod = Blueprint('index', __name__, url_prefix='/')

@mod.before_request
def before_request():
    tangle_session()

@mod.route('/login/', methods=['GET', 'POST'])
@requires_unauth
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        if database.Users.check_password(form.login.data.lower(), form.password.data):
            user = database.Users.get_one(form.login.data)
            session['user_id'] = user['id']
            return redirect(url_for('index.main'))
        flash('Wrong email or password', 'error_message')
    return render_template("html/login.html", form=form)

@mod.route('/registration/', methods=['GET', 'POST'])
@requires_unauth
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user_id = database.Users.add(form.login.data.lower(), form.password.data, _name=form.name.data, _email=form.email.data)
        if user_id is None:
            flash('User with this name already exists')
            return render_template("html/registration.html", form=form)
        session['user_id'] = user_id
        return redirect(url_for('index.main'))
    return render_template("html/registration.html", form=form)

@mod.route('/logout/')
@requires_auth
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index.login'))

@mod.route('/main', methods=['GET'])
@requires_auth
def main():
    return render_template("html/index.html", username=g.username, isAdmin=g.isAdmin, unit_list=g.unit_list)