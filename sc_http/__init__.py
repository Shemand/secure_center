import os
import sys

from flask import Flask, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

sys.path.append("/home/shemand/PycharmProjects/ff/sc_http")

app = Flask(__name__, static_folder='templates/static')
CORS(app)
app.config.from_object('config')

db = SQLAlchemy(app)

from sc_http.index.views import mod as index_module
from sc_http.api.views import mod as api_module
from sc_http.admin.views import mod as admin_module
from sc_http.devices.views import mod as devices_module

def install_secret_key(app, filename='secret_key'):
    filename = os.path.join(app.instance_path, filename)

    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print('Error: No secret key. Create it with:')
        full_path = os.path.dirname(filename)
        if not os.path.isdir(full_path):
            print('mkdir -p {filename}'.format(filename=full_path))
        print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
        sys.exit(1)

if not app.config['DEBUG']:
    install_secret_key(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('index.main'))
    else:
        return redirect(url_for('index.login'))


app.register_blueprint(index_module)
app.register_blueprint(api_module)
app.register_blueprint(admin_module)
app.register_blueprint(devices_module)

http_server = app
