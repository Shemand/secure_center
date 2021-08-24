import json
from datetime import datetime
from sc_statistic.control_statistics import ControlStatistics
from flask import Blueprint, jsonify, session, request, render_template, g

from sc_http.common.functions import tangle_session
from sc_http.common.decorators import requires_auth, requires_be_admin
from sc_databases import db as database

stat = ControlStatistics()
mod = Blueprint('admin', __name__, url_prefix='/admin/')

@mod.before_request
def before_request():
    tangle_session()

@mod.route('/', methods=["GET"])
@requires_auth
@requires_be_admin
def index():
    user = database.Users.get_by_id(session['user_id'])
    return render_template("html/admin.html", username=g.username, isAdmin=g.isAdmin)

@mod.route('statistics', methods=["GET"])
@requires_auth
@requires_be_admin
def statistics():
    user = database.Users.get_by_id(session['user_id'])
    stat.create_upload()
    return render_template("html/statistics.html", username=g.username, isAdmin=g.isAdmin)