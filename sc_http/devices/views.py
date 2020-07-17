import json
from datetime import datetime

from flask import Blueprint, jsonify, session, request, render_template, g

from sc_http.common.functions import tangle_session
from sc_http.common.decorators import requires_auth, requires_be_admin

mod = Blueprint('devices', __name__, url_prefix='/devices/')

@mod.before_request
def before_request():
    tangle_session()

@mod.route('/', methods=["GET"])
@requires_auth
def index():
    user = database.Users.get_by_id(session['user_id'])
    return render_template("html/devices.html", username=g.username, isAdmin=g.isAdmin)