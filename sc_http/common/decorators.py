from functools import wraps
from flask import g, flash, redirect, url_for, request


def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.username is None:
            flash(u"You need to be signed in for this page.")
            return redirect(url_for('index.login'))
        return f(*args, **kwargs)
    return decorated_function

def requires_unauth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.username is not None:
            return redirect(url_for('index.main'))
        return f(*args, **kwargs)
    return decorated_function

def requires_be_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.isAdmin is False:
            return redirect(url_for('index.main'))
        return f(*args, **kwargs)
    return decorated_function